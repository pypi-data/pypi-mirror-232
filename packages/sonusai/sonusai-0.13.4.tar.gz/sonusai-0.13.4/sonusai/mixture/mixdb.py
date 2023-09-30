from dataclasses import dataclass
from dataclasses import field
from typing import Any

from sonusai.mixture.types import AudioF
from sonusai.mixture.types import AudioT
from sonusai.mixture.types import AudiosF
from sonusai.mixture.types import AudiosT
from sonusai.mixture.types import Augmentation
from sonusai.mixture.types import Augmentations
from sonusai.mixture.types import ClassCount
from sonusai.mixture.types import DataClassSonusAIMixin
from sonusai.mixture.types import Feature
from sonusai.mixture.types import GenMixData
from sonusai.mixture.types import GeneralizedIDs
from sonusai.mixture.types import ImpulseResponseData
from sonusai.mixture.types import ImpulseResponseFiles
from sonusai.mixture.types import Location
from sonusai.mixture.types import NoiseFiles
from sonusai.mixture.types import Optional
from sonusai.mixture.types import Segsnr
from sonusai.mixture.types import SpectralMasks
from sonusai.mixture.types import TargetFile
from sonusai.mixture.types import TargetFiles
from sonusai.mixture.types import Truth
from sonusai.mixture.types import TruthSettings
from sonusai.mixture.types import UniversalSNR


@dataclass
class MRecord(DataClassSonusAIMixin):
    name: Optional[Location] = None
    noise_augmentation_index: Optional[int] = None
    noise_file_index: Optional[int] = None
    noise_offset: Optional[int] = None
    noise_snr_gain: Optional[float] = None
    random_snr: Optional[bool] = None
    samples: Optional[int] = None
    snr: Optional[float] = None
    spectral_mask_index: Optional[int] = None
    spectral_mask_seed: Optional[int] = None
    target_augmentation_index: Optional[list[int]] = None
    target_file_index: Optional[list[int]] = None
    target_gain: Optional[list[float]] = None
    target_snr_gain: Optional[float] = None


MRecords = list[MRecord]


@dataclass
class MixtureDatabaseConfig(DataClassSonusAIMixin):
    asr_manifest: list[Location] = field(default_factory=list)
    class_balancing: Optional[bool] = False
    class_balancing_augmentation: Optional[Augmentation] = None
    class_labels: Optional[list[str]] = None
    class_weights_threshold: Optional[list[float]] = None
    feature: Optional[str] = None
    first_cba_index: Optional[int] = None
    ir_files: Optional[ImpulseResponseFiles] = None
    mixtures: Optional[MRecords] = None
    noise_augmentations: Optional[Augmentations] = None
    noise_mix_mode: Optional[str] = 'exhaustive'
    noises: Optional[NoiseFiles] = None
    num_classes: Optional[int] = None
    random_snrs: Optional[list[str]] = None
    seed: Optional[int] = 0
    snrs: Optional[list[float]] = None
    spectral_masks: Optional[SpectralMasks] = None
    target_augmentations: Optional[Augmentations] = None
    targets: Optional[TargetFiles] = None
    truth_mutex: Optional[bool] = None
    truth_reduction_function: Optional[str] = None
    truth_settings: Optional[TruthSettings] = None


@dataclass
class TransformConfig:
    N: int
    R: int
    bin_start: int
    bin_end: int
    ttype: str


@dataclass
class FeatureGeneratorConfig:
    feature_mode: str
    num_classes: int
    truth_mutex: bool


@dataclass
class FeatureGeneratorInfo:
    decimation: int
    stride: int
    step: int
    num_bands: int
    ft_config: TransformConfig
    eft_config: TransformConfig
    it_config: TransformConfig


def get_feature_generator_info(fg_config: FeatureGeneratorConfig) -> FeatureGeneratorInfo:
    from dataclasses import asdict

    from pyaaware import FeatureGenerator

    fg = FeatureGenerator(**asdict(fg_config))

    return FeatureGeneratorInfo(
        decimation=fg.decimation,
        stride=fg.stride,
        step=fg.step,
        num_bands=fg.num_bands,
        ft_config=TransformConfig(N=fg.ftransform_N,
                                  R=fg.ftransform_R,
                                  bin_start=fg.bin_start,
                                  bin_end=fg.bin_end,
                                  ttype=fg.ftransform_ttype),
        eft_config=TransformConfig(N=fg.eftransform_N,
                                   R=fg.eftransform_R,
                                   bin_start=fg.bin_start,
                                   bin_end=fg.bin_end,
                                   ttype=fg.eftransform_ttype),
        it_config=TransformConfig(N=fg.itransform_N,
                                  R=fg.itransform_R,
                                  bin_start=fg.bin_start,
                                  bin_end=fg.bin_end,
                                  ttype=fg.itransform_ttype)
    )


class MixtureDatabase:
    def __init__(self,
                 config: Location | MixtureDatabaseConfig,
                 location: Optional[Location] = None,
                 lazy_load: bool = True):

        self._location: Location

        if isinstance(config, MixtureDatabaseConfig):
            self._config: MixtureDatabaseConfig = config
            self._location = location
        else:
            self._config = _load_from_location(config)
            self._location = config

        self.fg_config = FeatureGeneratorConfig(feature_mode=self.feature,
                                                num_classes=self.num_classes,
                                                truth_mutex=self.truth_mutex)

        self.fg_info = get_feature_generator_info(self.fg_config)

        self._ir_data: Optional[list[ImpulseResponseData]] = None
        self._asr_manifest_data: Optional[dict[str, str]] = None

        if not lazy_load:
            self._ir_data = self.load_ir_data()
            self._asr_manifest_data = self.load_asr_data()

    @property
    def json(self) -> str:
        """Convert MixtureDatabase to JSON

        :return: JSON representation of database
        """
        return self._config.to_json(indent=2)

    def save(self) -> None:
        """Save the MixtureDatabase as a JSON file
        """
        from os.path import join

        json_name = join(self._location, 'mixdb.json')
        with open(file=json_name, mode='w') as file:
            file.write(self.json)

    @property
    def config(self) -> MixtureDatabaseConfig:
        return self._config

    @property
    def location(self) -> Location:
        return self._location

    @property
    def asr_manifest(self) -> list[Location]:
        return self._config.asr_manifest

    @asr_manifest.setter
    def asr_manifest(self, value: list[Location]) -> None:
        self._config.asr_manifest = value

    @property
    def class_balancing(self) -> bool:
        return self._config.class_balancing

    @class_balancing.setter
    def class_balancing(self, value: bool) -> None:
        self._config.class_balancing = value

    @property
    def class_balancing_augmentation(self) -> Augmentation:
        return self._config.class_balancing_augmentation

    @class_balancing_augmentation.setter
    def class_balancing_augmentation(self, value: Augmentation) -> None:
        self._config.class_balancing_augmentation = value

    @property
    def class_labels(self) -> list[str]:
        return self._config.class_labels

    @class_labels.setter
    def class_labels(self, value: list[str]) -> None:
        from sonusai import SonusAIError

        if value is not None and (not isinstance(value, list) or len(value) != self.num_classes):
            raise SonusAIError(f'invalid class_labels length')
        self._config.class_labels = value

    @property
    def class_weights_threshold(self) -> list[float]:
        return self._config.class_weights_threshold

    @class_weights_threshold.setter
    def class_weights_threshold(self, value: list[float]) -> None:
        from sonusai import SonusAIError

        if len(value) not in [1, self.num_classes]:
            raise SonusAIError(f'invalid class_weights_threshold length: {len(value)}')
        self._config.class_weights_threshold = value

    @property
    def noise_mix_mode(self) -> str:
        return self._config.noise_mix_mode

    @noise_mix_mode.setter
    def noise_mix_mode(self, value: str) -> None:
        self._config.noise_mix_mode = value

    @property
    def feature(self) -> str:
        return self._config.feature

    @feature.setter
    def feature(self, value: str) -> None:
        self._config.feature = value

    @property
    def fg_decimation(self) -> int:
        return self.fg_info.decimation

    @property
    def fg_stride(self) -> int:
        return self.fg_info.stride

    @property
    def fg_step(self) -> int:
        return self.fg_info.step

    @property
    def fg_num_bands(self) -> int:
        return self.fg_info.num_bands

    @property
    def ft_config(self) -> TransformConfig:
        return self.fg_info.ft_config

    @property
    def eft_config(self) -> TransformConfig:
        return self.fg_info.eft_config

    @property
    def it_config(self) -> TransformConfig:
        return self.fg_info.it_config

    @property
    def transform_frame_ms(self) -> float:
        from sonusai.mixture import SAMPLE_RATE

        return float(self.ft_config.R) / float(SAMPLE_RATE / 1000)

    @property
    def feature_ms(self) -> float:
        return self.transform_frame_ms * self.fg_decimation * self.fg_stride

    @property
    def feature_samples(self) -> int:
        return self.ft_config.R * self.fg_decimation * self.fg_stride

    @property
    def feature_step_ms(self) -> float:
        return self.transform_frame_ms * self.fg_decimation * self.fg_step

    @property
    def feature_step_samples(self) -> int:
        return self.ft_config.R * self.fg_decimation * self.fg_step

    @property
    def first_cba_index(self) -> int:
        return self._config.first_cba_index

    @first_cba_index.setter
    def first_cba_index(self, value: int) -> None:
        self._config.first_cba_index = value

    @property
    def ir_files(self) -> ImpulseResponseFiles:
        return self._config.ir_files

    @property
    def mixtures(self) -> MRecords:
        return self._config.mixtures

    @mixtures.setter
    def mixtures(self, value: MRecords) -> None:
        self._config.mixtures = value

    @property
    def noise_augmentations(self) -> Augmentations:
        return self._config.noise_augmentations

    @noise_augmentations.setter
    def noise_augmentations(self, value: Augmentations) -> None:
        self._config.noise_augmentations = value

    @property
    def noises(self) -> NoiseFiles:
        return self._config.noises

    @noises.setter
    def noises(self, value: NoiseFiles) -> None:
        self._config.noises = value

    @property
    def num_classes(self) -> int:
        return self._config.num_classes

    @num_classes.setter
    def num_classes(self, value: int) -> None:
        self._config.num_classes = value

    @property
    def random_snrs(self) -> list[str]:
        return self._config.random_snrs

    @random_snrs.setter
    def random_snrs(self, value: list[str]) -> None:
        self._config.random_snrs = value

    @property
    def seed(self) -> int:
        return self._config.seed

    @seed.setter
    def seed(self, value: int) -> None:
        self._config.seed = value

    @property
    def snrs(self) -> list[float]:
        return self._config.snrs

    @snrs.setter
    def snrs(self, value: list[float]) -> None:
        self._config.snrs = value

    @property
    def all_snrs(self) -> list[UniversalSNR]:
        all_snrs: list[UniversalSNR] = []
        for snr in self.snrs:
            all_snrs.append(UniversalSNR(is_random=False, raw_value=snr))
        for random_snr in self.random_snrs:
            all_snrs.append(UniversalSNR(is_random=True, raw_value=random_snr))
        return all_snrs

    @property
    def spectral_masks(self) -> SpectralMasks:
        return self._config.spectral_masks

    @spectral_masks.setter
    def spectral_masks(self, value: SpectralMasks) -> None:
        self._config.spectral_masks = value

    @property
    def target_augmentations(self) -> Augmentations:
        return self._config.target_augmentations

    @target_augmentations.setter
    def target_augmentations(self, value: Augmentations) -> None:
        self._config.target_augmentations = value

    @property
    def targets(self) -> TargetFiles:
        return self._config.targets

    @targets.setter
    def targets(self, value: TargetFiles) -> None:
        self._config.targets = value

    @property
    def truth_mutex(self) -> bool:
        return self._config.truth_mutex

    @truth_mutex.setter
    def truth_mutex(self, value: bool) -> None:
        self._config.truth_mutex = value

    @property
    def truth_reduction_function(self) -> str:
        return self._config.truth_reduction_function

    @truth_reduction_function.setter
    def truth_reduction_function(self, value: str) -> None:
        self._config.truth_reduction_function = value

    @property
    def truth_settings(self) -> TruthSettings:
        return self._config.truth_settings

    @truth_settings.setter
    def truth_settings(self, value: TruthSettings) -> None:
        self._config.truth_settings = value

    def augmented_noise_length(self, file_index: int,
                               augmentation_index: int) -> int:
        from sonusai.mixture import estimate_augmented_length_from_length

        return estimate_augmented_length_from_length(length=self.noises[file_index].samples,
                                                     tempo=self.noise_augmentations[augmentation_index].tempo)

    def raw_target_audio(self, file_index: int) -> AudioT:
        """Get raw target audio

        :param file_index: Target audio file index
        :return: Raw target audio
        """
        from sonusai.mixture import read_audio

        return read_audio(self.targets[file_index].name)

    def augmented_target_audio(self, file_index: int, augmentation_index: int) -> AudioT:
        """Get augmented target audio

        :param file_index: Target audio file index
        :param augmentation_index: Target augmentation index
        :return: Augmented target audio
        """
        from sonusai.mixture import apply_augmentation
        from sonusai.mixture import apply_ir
        from sonusai.mixture import read_audio

        audio = read_audio(self.targets[file_index].name)
        augmentation = self.target_augmentations[augmentation_index]
        audio = apply_augmentation(audio, augmentation, self.feature_step_samples)
        if augmentation.ir is not None:
            audio = apply_ir(audio, self.ir_data[int(augmentation.ir)])

        return audio

    def augmented_noise_audio(self, file_index: int, augmentation_index: int) -> AudioT:
        """Get augmented noise audio

        :param file_index: Noise audio file index
        :param augmentation_index: Noise augmentation index
        :return: Augmented noise audio
        """
        from sonusai.mixture import apply_augmentation
        from sonusai.mixture import apply_ir
        from sonusai.mixture import read_audio

        audio = read_audio(self.noises[file_index].name)
        augmentation = self.noise_augmentations[augmentation_index]
        audio = apply_augmentation(audio, augmentation)
        if augmentation.ir is not None:
            audio = apply_ir(audio, self.ir_data[int(augmentation.ir)])

        return audio

    @property
    def ir_data(self) -> list[ImpulseResponseData]:
        """Get the list of impulse response data, loading from disk if necessary

        :return: List of impulse response data
        """
        if self._ir_data is None:
            self._ir_data = self.load_ir_data()

        return self._ir_data

    def load_ir_data(self) -> list[ImpulseResponseData]:
        """Load all impulse response data into memory

        :return: List of impulse response data
        """
        from sonusai.mixture import read_ir

        return [read_ir(ir_file) for ir_file in self.ir_files]

    def target_asr_data(self, target: TargetFile) -> str | None:
        """Get the ASR data for the given target, loading from disk if necessary

        :param target: TargetFile
        :return: ASR text or None
        """
        from sonusai.mixture import tokenized_expand

        if self._asr_manifest_data is None:
            self._asr_manifest_data = self.load_asr_data()

        name, _ = tokenized_expand(target.name)
        return self._asr_manifest_data.get(name, None)

    def mixid_asr_data(self, mixid: int) -> list[str | None]:
        """Get the ASR data for the given mixid, loading from disk if necessary

        :param mixid: Mixture ID
        :return: List of ASR text or None
        """
        if self._asr_manifest_data is None:
            self._asr_manifest_data = self.load_asr_data()

        return [self.target_asr_data(self.targets[tfi]) for tfi in self.mixtures[mixid].target_file_index]

    def load_asr_data(self) -> dict[str, str]:
        """Load ASR data into memory

        Each line of a manifest file should be in the following format:

        {"audio_filepath": "/path/to/audio.wav", "text": "the transcription of the utterance", "duration": 23.147}

        The audio_filepath field should provide an absolute path to the audio file corresponding to the utterance. The
        text field should contain the full transcript for the utterance, and the duration field should reflect the
        duration of the utterance in seconds.

        Each entry in the manifest (describing one audio file) should be bordered by '{' and '}' and must be contained
        on one line. The fields that describe the file should be separated by commas, and have the form
        "field_name": value, as shown above.

        Since the manifest specifies the path for each utterance, the audio files do not have to be located in the same
        directory as the manifest, or even in any specific directory structure.

        The manifest dictionary consists of key/value pairs where the keys are target file names and the values are ASR
        text.
        """
        import json

        from sonusai import SonusAIError
        from sonusai.mixture import tokenized_expand
        from sonusai.mixture import Location

        expected_keys = ['audio_filepath', 'text', 'duration']

        def _error_preamble(e_name: Location, e_line_num: int) -> str:
            return f'Invalid entry in ASR manifest {e_name} line {e_line_num}'

        asr_manifest_data: dict[str, str] = {}

        for name in self._config.asr_manifest:
            expanded_name, _ = tokenized_expand(name)
            with open(file=expanded_name, mode='r') as f:
                line_num = 1
                for line in f:
                    result = json.loads(line.strip())

                    for key in expected_keys:
                        if key not in result:
                            SonusAIError(f'{_error_preamble(name, line_num)}: missing field "{key}"')

                    for key in result.keys():
                        if key not in expected_keys:
                            SonusAIError(f'{_error_preamble(name, line_num)}: unknown field "{key}"')

                    key, _ = tokenized_expand(result['audio_filepath'])
                    value = result['text']

                    if key in asr_manifest_data:
                        SonusAIError(f'{_error_preamble(name, line_num)}: entry already exists')

                    asr_manifest_data[key] = value

                    line_num += 1

        return asr_manifest_data

    @property
    def augmented_target_samples(self) -> int:
        from itertools import product

        from sonusai.mixture import estimate_augmented_length_from_length

        it = list(product(*[range(len(self.targets)), range(len(self.target_augmentations))]))
        return sum([estimate_augmented_length_from_length(
            length=self.targets[fi].samples,
            tempo=self.target_augmentations[ai].tempo,
            length_common_denominator=self.feature_step_samples) for fi, ai, in it])

    @property
    def augmented_noise_samples(self) -> int:
        from itertools import product

        it = list(product(*[range(len(self.noises)), range(len(self.noise_augmentations))]))
        return sum([self.augmented_noise_length(fi, ai) for fi, ai in it])

    def total_samples(self, mixids: GeneralizedIDs = '*') -> int:
        return sum([self.mixture_samples(mixid) for mixid in self.mixids_to_list(mixids)])

    def total_transform_frames(self, mixids: GeneralizedIDs = '*') -> int:
        return self.total_samples(mixids) // self.ft_config.R

    def total_feature_frames(self, mixids: GeneralizedIDs = '*') -> int:
        return self.total_samples(mixids) // self.feature_step_samples

    def mixture_samples(self, mixid: int) -> int:
        return self.mixtures[mixid].samples

    def mixture_transform_frames(self, mixid: int) -> int:
        return self.mixture_samples(mixid) // self.ft_config.R

    def mixture_feature_frames(self, mixid: int) -> int:
        return self.mixture_samples(mixid) // self.feature_step_samples

    def mixids_to_list(self, ids: Optional[GeneralizedIDs] = None) -> list[int]:
        """Resolve generalized mixture IDs to a list of integers

        :param ids: Generalized mixture IDs
        :return: List of mixture ID integers
        """
        return generic_ids_to_list(len(self.mixtures), ids)

    def mixture_metadata(self, mixid: int) -> str:
        """Create a string of metadata for a mixture ID

        :param mixid: Mixture ID
        :return: String of metadata
        """
        mrecord = self.mixtures[mixid]
        metadata = ''
        for ti in range(len(mrecord.target_file_index)):
            tfi = mrecord.target_file_index[ti]
            tai = mrecord.target_augmentation_index[ti]
            metadata += f'target {ti} name: {self.targets[tfi].name}\n'
            metadata += f'target {ti} augmentation: {self.target_augmentations[tai].to_dict()}\n'
            if self.target_augmentations[tai].ir is None:
                ir_name = None
            else:
                ir_name = self.ir_files[int(self.target_augmentations[tai].ir)]
            metadata += f'target {ti} ir: {ir_name}\n'
            metadata += f'target {ti} target_gain: {mrecord.target_gain[ti]}\n'
            truth_settings = self.targets[tfi].truth_settings
            for tsi in range(len(truth_settings)):
                metadata += f'target {ti} truth index {tsi}: {truth_settings[tsi].index}\n'
                metadata += f'target {ti} truth function {tsi}: {truth_settings[tsi].function}\n'
                metadata += f'target {ti} truth config {tsi}: {truth_settings[tsi].config}\n'
            metadata += f'target {ti} asr: {self.target_asr_data(self.targets[tfi])}\n'
        nfi = mrecord.noise_file_index
        nai = mrecord.noise_augmentation_index
        metadata += f'noise name: {self.noises[nfi].name}\n'
        metadata += f'noise augmentation: {self.noise_augmentations[nai].to_dict()}\n'
        if self.noise_augmentations[nai].ir is None:
            ir_name = None
        else:
            ir_name = self.ir_files[int(self.noise_augmentations[nai].ir)]
        metadata += f'noise ir: {ir_name}\n'
        metadata += f'noise offset: {mrecord.noise_offset}\n'
        metadata += f'snr: {mrecord.snr}\n'
        metadata += f'random_snr: {mrecord.random_snr}\n'
        metadata += f'samples: {mrecord.samples}\n'
        metadata += f'target_snr_gain: {mrecord.target_snr_gain}\n'
        metadata += f'noise_snr_gain: {mrecord.noise_snr_gain}\n'

        return metadata

    def write_mixture_metadata(self, mixid: int) -> None:
        """Write mixture metadata to a text file

        :param mixid: Mixture ID
        """
        from os.path import splitext

        with open(file=splitext(self.mixture_filename(mixid))[0] + '.txt', mode='w') as f:
            f.write(self.mixture_metadata(mixid))

    def mixture_filename(self, mixid: int) -> Location:
        """Get the HDF5 file name for the given mixture ID

        :param mixid: Mixture ID
        :return: File name
        """
        from os.path import join

        return join(self._location, self.mixtures[mixid].name) if self._location is not None else None

    @property
    def _mixid_width(self) -> int:
        from sonusai.utils import max_text_width

        return max_text_width(len(self.mixtures))

    def _generate_mixture_filename(self, mixid: int) -> str:
        """Generate a zero-padded mixture file name

        :param mixid: Mixture ID
        :return: Zero-padded mixture file name
        """
        return f'{mixid:0{self._mixid_width}}.h5'

    def read_mixture_data(self, mixid: int, items: list[str] | str) -> Any:
        """Read mixture data from a mixture HDF5 file

        :param mixid: Mixture ID
        :param items: String(s) of dataset(s) to retrieve
        :return: Data (or tuple of data)
        """
        from os.path import exists
        from typing import Any

        import h5py
        import numpy as np

        from sonusai import SonusAIError

        def _get_dataset(file: h5py.File, d_name: str) -> Any:
            if d_name in file:
                return np.array(file[d_name])
            return None

        if not isinstance(items, list):
            items = [items]

        name = self.mixture_filename(mixid)
        if exists(name):
            try:
                with h5py.File(name, 'r') as f:
                    result = ([_get_dataset(f, item) for item in items])
            except Exception as e:
                raise SonusAIError(f'Error reading {name}: {e}')
        else:
            result = ([None for _ in items])

        if len(items) == 1:
            result = result[0]

        return result

    def write_mixture_data(self, mixid: int, items: list[tuple[str, Any]] | tuple[str, Any]) -> None:
        """Write mixture data to a mixture HDF5 file

        :param mixid: Mixture ID
        :param items: Tuple(s) of (name, data)
        """
        import h5py

        if not isinstance(items, list):
            items = [items]

        with h5py.File(self.mixture_filename(mixid), 'a') as f:
            for item in items:
                if item[0] in f:
                    del f[item[0]]
                f.create_dataset(name=item[0], data=item[1])

    def mixture_targets(self,
                        mixid: int,
                        force: bool = False) -> AudiosT:
        """Get the list of augmented target audio data (one per target in the mixup) for the given mixid

        :param mixid: Mixture ID
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: List of augmented target audio data (one per target in the mixup)
        """
        from sonusai.mixture import apply_augmentation
        from sonusai.mixture import apply_gain
        from sonusai.mixture import pad_audio_to_length

        if not force:
            targets = self.read_mixture_data(mixid, 'targets')
            if targets is not None:
                return list(targets)

        mrecord = self.mixtures[mixid]
        targets = []
        for idx in range(len(mrecord.target_file_index)):
            target = self.raw_target_audio(mrecord.target_file_index[idx])
            target = apply_augmentation(audio=target,
                                        augmentation=self.target_augmentations[mrecord.target_augmentation_index[idx]],
                                        length_common_denominator=self.feature_step_samples)
            target = apply_gain(audio=target, gain=mrecord.target_snr_gain)
            target = pad_audio_to_length(audio=target, length=mrecord.samples)
            targets.append(target)

        return targets

    def mixture_targets_f(self,
                          mixid: int,
                          targets: Optional[AudiosT] = None,
                          force: bool = False) -> AudiosF:
        """Get the list of augmented target transform data (one per target in the mixup) for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: List of augmented target transform data (one per target in the mixup)
        """
        if targets is None:
            targets = self.mixture_targets(mixid=mixid, force=force)

        return [forward_transform(target, self.ft_config) for target in targets]

    def mixture_target(self,
                       mixid: int,
                       targets: Optional[AudiosT] = None,
                       force: bool = False) -> AudioT:
        """Get the augmented target audio data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented target audio data
        """
        import numpy as np

        from sonusai.mixture import apply_ir

        if not force:
            target = self.read_mixture_data(mixid, 'target')
            if target is not None:
                return target

        if targets is None:
            targets = self.mixture_targets(mixid=mixid, force=force)

        # Apply impulse responses to targets
        targets_ir = []
        for idx, target in enumerate(targets):
            ir_idx = self.target_augmentations[self.mixtures[mixid].target_augmentation_index[idx]].ir
            if ir_idx is not None:
                targets_ir.append(apply_ir(audio=target, ir=self.ir_data[int(ir_idx)]))
            else:
                targets_ir.append(target)
        targets = targets_ir

        return np.sum(targets, axis=0)

    def mixture_target_f(self,
                         mixid: int,
                         targets: Optional[AudiosT] = None,
                         target: Optional[AudioT] = None,
                         force: bool = False) -> AudioF:
        """Get the augmented target transform data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param target: Augmented target audio for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented target transform data
        """
        if target is None:
            target = self.mixture_target(mixid=mixid, targets=targets, force=force)

        return forward_transform(target, self.ft_config)

    def mixture_noise(self,
                      mixid: int,
                      force: bool = False) -> AudioT:
        """Get the augmented noise audio data for the given mixid

        :param mixid: Mixture ID
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented noise audio data
        """
        from sonusai.mixture import apply_gain
        from sonusai.mixture import get_next_noise

        if not force:
            noise = self.read_mixture_data(mixid, 'noise')
            if noise is not None:
                return noise

        mrecord = self.mixtures[mixid]
        noise = self.augmented_noise_audio(mrecord.noise_file_index, mrecord.noise_augmentation_index)
        noise = get_next_noise(audio=noise, offset=mrecord.noise_offset, length=mrecord.samples)
        noise = apply_gain(audio=noise, gain=mrecord.noise_snr_gain)

        return noise

    def mixture_noise_f(self,
                        mixid: int,
                        noise: Optional[AudioT] = None,
                        force: bool = False) -> AudioF:
        """Get the augmented noise transform for the given mixid

        :param mixid: Mixture ID
        :param noise: Augmented noise audio data for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Augmented noise transform data
        """
        if noise is None:
            noise = self.mixture_noise(mixid=mixid, force=force)

        return forward_transform(noise, self.ft_config)

    def mixture_mixture(self,
                        mixid: int,
                        targets: Optional[AudiosT] = None,
                        target: Optional[AudioT] = None,
                        noise: Optional[AudioT] = None,
                        force: bool = False) -> AudioT:
        """Get the mixture audio data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param target: Augmented target audio data for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Mixture audio data
        """
        if not force:
            mixture = self.read_mixture_data(mixid, 'mixture')
            if mixture is not None:
                return mixture

        if target is None:
            target = self.mixture_target(mixid=mixid, targets=targets)

        if noise is None:
            noise = self.mixture_noise(mixid=mixid)

        mixture = target + noise

        return mixture

    def mixture_mixture_f(self, mixid: int,
                          targets: Optional[AudiosT] = None,
                          target: Optional[AudioT] = None,
                          noise: Optional[AudioT] = None,
                          mixture: Optional[AudioT] = None,
                          force: bool = False) -> AudioF:
        """Get the mixture transform for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param target: Augmented target audio data for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param mixture: Mixture audio data for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Mixture transform data
        """
        if mixture is None:
            mixture = self.mixture_mixture(mixid=mixid, targets=targets, target=target, noise=noise, force=force)

        return forward_transform(mixture, self.ft_config)

    def mixture_truth_t(self,
                        mixid: int,
                        targets: Optional[AudiosT] = None,
                        noise: Optional[AudioT] = None,
                        force: bool = False) -> Truth:
        """Get the truth_t data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: truth_t data
        """
        import numpy as np

        from sonusai import SonusAIError
        from sonusai.mixture import TruthFunctionConfig
        from sonusai.mixture import truth_function

        if not force:
            truth_t = self.read_mixture_data(mixid, 'truth_t')
            if truth_t is not None:
                return truth_t

        if targets is None:
            targets = self.mixture_targets(mixid=mixid)

        if noise is None:
            noise = self.mixture_noise(mixid=mixid)

        mrecord = self.mixtures[mixid]
        if len(targets) != len(mrecord.target_file_index):
            raise SonusAIError('Number of target audio entries does not match number of targets')

        if not all(len(target_audio) == len(noise) for target_audio in targets):
            raise SonusAIError('Lengths of target audio do not match length of noise audio')

        truth_t = np.zeros((self.mixture_samples(mixid), self.num_classes), dtype=np.float32)
        for idx in range(len(targets)):
            for truth_setting in self.targets[mrecord.target_file_index[idx]].truth_settings:
                config = TruthFunctionConfig(
                    feature=self.feature,
                    index=truth_setting.index,
                    function=truth_setting.function,
                    config=truth_setting.config,
                    num_classes=self.num_classes,
                    mutex=self.truth_mutex,
                    target_gain=mrecord.target_gain[idx] * mrecord.target_snr_gain
                )
                truth_t += truth_function(target_audio=targets[idx], noise_audio=noise, config=config)

        return truth_t

    def mixture_segsnr_t(self,
                         mixid: int,
                         targets: Optional[AudiosT] = None,
                         target: Optional[AudioT] = None,
                         noise: Optional[AudioT] = None,
                         force: bool = False) -> Segsnr:
        """Get the segsnr_t data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param target: Augmented target audio data for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: segsnr_t data
        """
        import numpy as np
        from pyaaware import AawareForwardTransform

        from sonusai import SonusAIError

        if not force:
            segsnr_t = self.read_mixture_data(mixid, 'segsnr_t')
            if segsnr_t is not None:
                return segsnr_t

        if target is None:
            target = self.mixture_target(mixid=mixid, targets=targets)

        if noise is None:
            noise = self.mixture_noise(mixid=mixid)

        fft = AawareForwardTransform(N=self.ft_config.N,
                                     R=self.ft_config.R,
                                     bin_start=self.ft_config.bin_start,
                                     bin_end=self.ft_config.bin_end,
                                     ttype=self.ft_config.ttype)

        segsnr_t = np.empty(self.mixture_samples(mixid), dtype=np.float32)

        _, target_energy = fft.execute_all(target)
        _, noise_energy = fft.execute_all(noise)

        offsets = range(0, self.mixture_samples(mixid), self.ft_config.R)
        if len(target_energy) != len(offsets):
            raise SonusAIError(f'Number of frames in energy, {len(target_energy)},'
                               f' is not number of frames in mixture, {len(offsets)}')

        for idx, offset in enumerate(offsets):
            indices = slice(offset, offset + self.ft_config.R)

            if noise_energy[idx] == 0:
                snr = np.float32(np.inf)
            else:
                snr = np.float32(target_energy[idx] / noise_energy[idx])

            segsnr_t[indices] = snr

        return segsnr_t

    def mixture_segsnr(self,
                       mixid: int,
                       segsnr_t: Optional[Segsnr] = None,
                       targets: Optional[AudiosT] = None,
                       target: Optional[AudioT] = None,
                       noise: Optional[AudioT] = None,
                       force: bool = False) -> Segsnr:
        """Get the segsnr data for the given mixid

        :param mixid: Mixture ID
        :param segsnr_t: segsnr_t data for the given mixid
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param target: Augmented target audio data for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: segsnr data
        """
        if not force:
            segsnr = self.read_mixture_data(mixid, 'segsnr')
            if segsnr is not None:
                return segsnr

            segsnr_t = self.read_mixture_data(mixid, 'segsnr_t')
            if segsnr_t is not None:
                return segsnr_t[0::self.ft_config.R]

        if segsnr_t is None:
            segsnr_t = self.mixture_segsnr_t(mixid=mixid, targets=targets, target=target, noise=noise)

        segsnr = segsnr_t[0::self.ft_config.R]

        return segsnr

    def mixture_ft(self,
                   mixid: int,
                   targets: Optional[AudiosT] = None,
                   target: Optional[AudioT] = None,
                   noise: Optional[AudioT] = None,
                   mixture_f: Optional[AudioF] = None,
                   mixture: Optional[AudioT] = None,
                   truth_t: Optional[Truth] = None,
                   force: bool = False) -> tuple[Feature, Truth]:
        """Get the feature and truth_f data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param target: Augmented target audio data for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param mixture_f: Mixture transform data for the given mixid
        :param mixture: Mixture audio data for the given mixid
        :param truth_t: truth_t for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Tuple of (feature, truth_f) data
        """
        from dataclasses import asdict

        import numpy as np
        from pyaaware import FeatureGenerator

        from sonusai.mixture import apply_spectral_mask
        from sonusai.mixture import truth_reduction

        if not force:
            feature, truth_f = self.read_mixture_data(mixid, ['feature', 'truth_f'])
            if feature is not None and truth_f is not None:
                return feature, truth_f

        if mixture_f is None:
            mixture_f = self.mixture_mixture_f(mixid=mixid,
                                               targets=targets,
                                               target=target,
                                               noise=noise,
                                               mixture=mixture)

        if truth_t is None:
            truth_t = self.mixture_truth_t(mixid=mixid, targets=targets, noise=noise)

        mrecord = self.mixtures[mixid]

        transform_frames = self.mixture_transform_frames(mixid)
        feature_frames = self.mixture_feature_frames(mixid)

        if truth_t is None:
            truth_t = np.zeros((self.mixture_samples(mixid), self.num_classes), dtype=np.float32)

        feature = np.empty((feature_frames, self.fg_stride, self.fg_num_bands), dtype=np.float32)
        truth_f = np.empty((feature_frames, self.num_classes), dtype=np.complex64)

        fg = FeatureGenerator(**asdict(self.fg_config))
        feature_frame = 0
        for transform_frame in range(transform_frames):
            indices = slice(transform_frame * self.ft_config.R, (transform_frame + 1) * self.ft_config.R)
            fg.execute(mixture_f[transform_frame],
                       truth_reduction(truth_t[indices], self.truth_reduction_function))

            if fg.eof():
                feature[feature_frame] = fg.feature()
                truth_f[feature_frame] = fg.truth()
                feature_frame += 1

        if np.isreal(truth_f).all():
            truth_f = np.float32(np.real(truth_f))

        if mrecord.spectral_mask_index is not None:
            feature = apply_spectral_mask(feature=feature,
                                          spectral_mask=self.spectral_masks[mrecord.spectral_mask_index],
                                          seed=mrecord.spectral_mask_seed)

        return feature, truth_f

    def mixture_feature(self,
                        mixid: int,
                        targets: Optional[AudiosT] = None,
                        noise: Optional[AudioT] = None,
                        mixture: Optional[AudioT] = None,
                        truth_t: Optional[Truth] = None,
                        force: bool = False) -> Feature:
        """Get the feature data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param mixture: Mixture audio data for the given mixid
        :param truth_t: truth_t for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: Feature data
        """
        feature, _ = self.mixture_ft(mixid=mixid,
                                     targets=targets,
                                     noise=noise,
                                     mixture=mixture,
                                     truth_t=truth_t,
                                     force=force)
        return feature

    def mixture_truth_f(self,
                        mixid: int,
                        targets: Optional[AudiosT] = None,
                        noise: Optional[AudioT] = None,
                        mixture: Optional[AudioT] = None,
                        truth_t: Optional[Truth] = None,
                        force: bool = False) -> Truth:
        """Get the truth_f data for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio data (one per target in the mixup) for the given mixid
        :param noise: Augmented noise audio data for the given mixid
        :param mixture: Mixture audio data for the given mixid
        :param truth_t: truth_t for the given mixid
        :param force: Force computing data from original sources regardless of whether cached data exists
        :return: truth_f data
        """
        _, truth_f = self.mixture_ft(mixid=mixid,
                                     targets=targets,
                                     noise=noise,
                                     mixture=mixture,
                                     truth_t=truth_t,
                                     force=force)
        return truth_f

    def mixture_class_count(self,
                            mixid: int,
                            targets: Optional[AudiosT] = None,
                            noise: Optional[AudioT] = None,
                            truth_t: Optional[Truth] = None) -> ClassCount:
        """Compute the number of samples for which each truth index is active for the given mixid

        :param mixid: Mixture ID
        :param targets: List of augmented target audio (one per target in the mixup) for the given mixid
        :param noise: Augmented noise audio for the given mixid
        :param truth_t: truth_t for the given mixid
        :return: List of class counts
        """
        import numpy as np

        if truth_t is None:
            truth_t = self.mixture_truth_t(mixid=mixid, targets=targets, noise=noise)

        class_count = [0] * self.num_classes
        num_classes = self.num_classes
        if self.truth_mutex:
            num_classes -= 1
        for cl in range(num_classes):
            class_count[cl] = int(np.sum(truth_t[:, cl] >= self.class_weights_threshold[cl]))

        return class_count

    def generate_mrecord(self, mixid: int) -> tuple[MRecord, GenMixData]:
        import numpy as np

        from sonusai import SonusAIError
        from sonusai.mixture import apply_gain
        from sonusai.mixture import apply_ir
        from sonusai.mixture import get_next_noise

        mrecord = self.mixtures[mixid]
        if len(mrecord.target_file_index) != len(mrecord.target_augmentation_index):
            raise SonusAIError('target_file_index and target_augmentation_index are not the same length')

        noise_audio = self.augmented_noise_audio(mrecord.noise_file_index, mrecord.noise_augmentation_index)

        mrecord.name = self._generate_mixture_filename(mixid)
        targets = self._initialize_target_audio(mrecord=mrecord)
        noise = get_next_noise(audio=noise_audio, offset=mrecord.noise_offset, length=mrecord.samples)
        mrecord = self._initialize_mixture_gains(mrecord=mrecord, target_audios=targets, noise_audio=noise)
        targets = [apply_gain(audio=target, gain=mrecord.target_snr_gain) for target in targets]
        noise = apply_gain(audio=noise, gain=mrecord.noise_snr_gain)

        # Apply impulse response to targets
        targets_ir = []
        for idx, target in enumerate(targets):
            ir_idx = self.target_augmentations[mrecord.target_augmentation_index[idx]].ir
            if ir_idx is not None:
                targets_ir.append(apply_ir(audio=target, ir=self.ir_data[int(ir_idx)]))
            else:
                targets_ir.append(target)

        mixture = np.sum(targets_ir, axis=0) + noise

        return mrecord, GenMixData(mixture=mixture, targets=targets, noise=noise)

    def _initialize_target_audio(self, mrecord: MRecord) -> AudiosT:
        """Apply augmentation and update target metadata
        """
        from sonusai.mixture import pad_audio_to_length
        from sonusai.mixture.augmentation import apply_augmentation

        targets = []
        mrecord.target_gain = []
        for idx in range(len(mrecord.target_file_index)):
            target_augmentation = self.target_augmentations[mrecord.target_augmentation_index[idx]]

            targets.append(apply_augmentation(audio=self.raw_target_audio(mrecord.target_file_index[idx]),
                                              augmentation=target_augmentation,
                                              length_common_denominator=self.feature_step_samples))

            # target_gain is used to back out the gain augmentation in order to return the target audio
            # to its normalized level when calculating truth (if needed).
            if target_augmentation.gain is not None:
                target_gain = 10 ** (float(target_augmentation.gain) / 20)
            else:
                target_gain = 1
            mrecord.target_gain.append(target_gain)

        mrecord.samples = max([len(item) for item in targets])

        for idx in range(len(targets)):
            targets[idx] = pad_audio_to_length(audio=targets[idx], length=mrecord.samples)

        return targets

    def initialize_target(self, mrecord: MRecord) -> MRecord:
        """Apply augmentation and update target metadata
        """
        self._initialize_target_audio(mrecord)
        return mrecord

    def _initialize_mixture_gains(self,
                                  mrecord: MRecord,
                                  target_audios: AudiosT,
                                  noise_audio: AudioT) -> MRecord:
        import numpy as np

        from sonusai import SonusAIError
        from sonusai.utils import asl_p56
        from sonusai.utils import db_to_linear

        target_audio = np.sum(target_audios, axis=0)

        if mrecord.snr < -96:
            # Special case for zeroing out target data
            mrecord.target_snr_gain = 0
            mrecord.noise_snr_gain = 1
            # Setting target_gain to zero will cause the truth to be all zeros.
            mrecord.target_gain = [0] * len(mrecord.target_gain)
        elif mrecord.snr > 96:
            # Special case for zeroing out noise data
            mrecord.target_snr_gain = 1
            mrecord.noise_snr_gain = 0
        else:
            target_level_types = [target_file.target_level_type for target_file in
                                  [self.targets[index] for index in mrecord.target_file_index]]
            if not all(target_level_type == target_level_types[0] for target_level_type in target_level_types):
                raise SonusAIError(f'Not all target_level_types in mixup are the same')

            target_level_type = target_level_types[0]
            match target_level_type:
                case 'default':
                    target_energy = np.mean(np.square(target_audio))
                case 'speech':
                    target_energy = asl_p56(target_audio)
                case _:
                    raise SonusAIError(f'Unknown target_level_type: {target_level_type}')

            noise_energy = np.mean(np.square(noise_audio))
            if noise_energy == 0:
                noise_gain = 1
            else:
                noise_gain = np.sqrt(target_energy / noise_energy) / db_to_linear(mrecord.snr)

            # Check for noise_gain > 1 to avoid clipping
            if noise_gain > 1:
                mrecord.target_snr_gain = 1 / noise_gain
                mrecord.noise_snr_gain = 1
            else:
                mrecord.target_snr_gain = 1
                mrecord.noise_snr_gain = noise_gain

        # Check for clipping in mixture
        gain_adjusted_target_audio = target_audio * mrecord.target_snr_gain
        gain_adjusted_noise_audio = noise_audio * mrecord.noise_snr_gain
        mixture_audio = gain_adjusted_target_audio + gain_adjusted_noise_audio
        max_abs_audio = max(abs(mixture_audio))
        clip_level = db_to_linear(-0.25)
        if max_abs_audio > clip_level:
            # Clipping occurred; lower gains to bring audio within +/-1
            gain_adjustment = clip_level / max_abs_audio
            mrecord.target_snr_gain *= gain_adjustment
            mrecord.noise_snr_gain *= gain_adjustment

        return mrecord


def get_mrecords_from_mixids(mixdb: MixtureDatabase, mixids: Optional[GeneralizedIDs] = None) -> MRecords:
    """Get a list of MRecords for the given mixture IDs

    :param mixdb: Mixture database
    :param mixids: Mixture IDs
    :return: MRecords
    """
    from copy import deepcopy

    return [deepcopy(mixdb.mixtures[i]) for i in mixdb.mixids_to_list(mixids)]


def generic_ids_to_list(num_ids: int, ids: GeneralizedIDs = None) -> list[int]:
    """Resolve generalized IDs to a list of integers

    :param num_ids: Total number of indices
    :param ids: Generalized  IDs
    :return: List of ID integers
    """
    from sonusai import SonusAIError

    all_ids = list(range(num_ids))

    if ids is None:
        return all_ids

    if isinstance(ids, str):
        if ids == '*':
            return all_ids

        try:
            result = eval(f'{all_ids}[{ids}]')
            if not isinstance(result, list):
                result = [result]
            return result
        except NameError:
            raise SonusAIError(f'Empty ids {ids}')

    if isinstance(ids, range):
        result = list(ids)
    elif isinstance(ids, int):
        result = [ids]
    else:
        result = ids

    if not all(isinstance(x, int) and 0 <= x < num_ids for x in result):
        raise SonusAIError(f'Invalid entries in ids of {ids}')

    if not result:
        raise SonusAIError(f'Empty ids {ids}')

    return result


def _load_from_location(location: Location) -> MixtureDatabaseConfig:
    import json
    from os.path import exists
    from os.path import isdir
    from os.path import join

    from sonusai import SonusAIError

    if not isdir(location):
        raise SonusAIError(f'{location} is not a directory')

    filename = join(location, 'mixdb.json')
    if not exists(filename):
        raise SonusAIError(f'could not find mixture database in {location}')

    with open(file=filename, mode='r', encoding='utf-8') as f:
        return MixtureDatabaseConfig.from_dict(json.loads(f.read()))


def forward_transform(audio: AudioT, config: TransformConfig) -> AudioF:
    """Transform time domain data into frequency domain using the forward transform config from the feature

    A new transform is used for each call; i.e., state is not maintained between calls to forward_transform().

    :param audio: Time domain data [samples]
    :param config: Transform configuration
    :return: Frequency domain data [frames, bins]
    """
    from pyaaware import AawareForwardTransform

    from sonusai.mixture import calculate_transform_from_audio

    audio_f, _ = calculate_transform_from_audio(audio=audio,
                                                transform=AawareForwardTransform(N=config.N,
                                                                                 R=config.R,
                                                                                 bin_start=config.bin_start,
                                                                                 bin_end=config.bin_end,
                                                                                 ttype=config.ttype))
    return audio_f


def inverse_transform(transform: AudioF, config: TransformConfig, trim: bool = True) -> AudioT:
    """Transform frequency domain data into time domain using the inverse transform config from the feature

    A new transform is used for each call; i.e., state is not maintained between calls to inverse_transform().

    :param transform: Frequency domain data [frames, bins]
    :param config: Transform configuration
    :param trim: Removes starting samples so output waveform will be time-aligned with input waveform to the
                 transform
    :return: Time domain data [samples]
    """
    import numpy as np

    from pyaaware import AawareInverseTransform

    from sonusai.mixture import calculate_audio_from_transform

    audio, _ = calculate_audio_from_transform(data=transform,
                                              transform=AawareInverseTransform(N=config.N,
                                                                               R=config.R,
                                                                               bin_start=config.bin_start,
                                                                               bin_end=config.bin_end,
                                                                               ttype=config.ttype,
                                                                               gain=np.float32(1)),
                                              trim=trim)
    return audio


def check_audio_files_exist(mixdb: MixtureDatabase) -> None:
    """Walk through all the noise and target audio files in a mixture database ensuring that they exist
    """
    from os.path import exists

    from sonusai import SonusAIError
    from sonusai.mixture import tokenized_expand

    for file_index in range(len(mixdb.noises)):
        file_name, _ = tokenized_expand(mixdb.noises[file_index].name)
        if not exists(file_name):
            raise SonusAIError(f'Could not find {file_name}')

    for file_index in range(len(mixdb.targets)):
        file_name, _ = tokenized_expand(mixdb.targets[file_index].name)
        if not exists(file_name):
            raise SonusAIError(f'Could not find {file_name}')
