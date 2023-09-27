from dataclasses import dataclass
from typing import Optional
from typing import TypeAlias

import numpy as np
import numpy.typing as npt
from dataclasses_json import DataClassJsonMixin

AudioT: TypeAlias = npt.NDArray[np.float32]
AudiosT: TypeAlias = list[AudioT]

ListAudiosT: TypeAlias = list[AudiosT]

Truth: TypeAlias = npt.NDArray[np.float32]
Segsnr: TypeAlias = npt.NDArray[np.float32]

AudioF: TypeAlias = npt.NDArray[np.complex64]
AudiosF: TypeAlias = list[AudioF]

EnergyT: TypeAlias = npt.NDArray[np.float32]
EnergyF: TypeAlias = npt.NDArray[np.float32]

Feature: TypeAlias = npt.NDArray[np.float32]

Predict: TypeAlias = npt.NDArray[np.float32]

Location: TypeAlias = str

# Json type defined to maintain compatibility with DataClassJsonMixin
Json: TypeAlias = dict | list | str | int | float | bool | None


class DataClassSonusAIMixin(DataClassJsonMixin):
    def __str__(self):
        return f'{self.to_dict()}'

    # Override DataClassJsonMixin to remove dictionary keys with values of None
    def to_dict(self, encode_json=False) -> dict[str, Json]:
        def del_none(d):
            if isinstance(d, dict):
                for key, value in list(d.items()):
                    if value is None:
                        del d[key]
                    elif isinstance(value, dict):
                        del_none(value)
                    elif isinstance(value, list):
                        for item in value:
                            del_none(item)
            elif isinstance(d, list):
                for item in d:
                    del_none(item)
            return d

        return del_none(super().to_dict(encode_json))


@dataclass(frozen=True)
class TruthSetting(DataClassSonusAIMixin):
    config: Optional[dict] = None
    function: Optional[str] = None
    index: Optional[list[int]] = None


TruthSettings: TypeAlias = list[TruthSetting]
OptionalNumberStr: TypeAlias = Optional[float | int | str]
OptionalListNumberStr: TypeAlias = Optional[list[float | int | str]]


@dataclass
class Augmentation(DataClassSonusAIMixin):
    normalize: OptionalNumberStr = None
    pitch: OptionalNumberStr = None
    tempo: OptionalNumberStr = None
    gain: OptionalNumberStr = None
    eq1: OptionalListNumberStr = None
    eq2: OptionalListNumberStr = None
    eq3: OptionalListNumberStr = None
    lpf: OptionalNumberStr = None
    ir: OptionalNumberStr = None
    count: Optional[int] = None
    mixup: Optional[int] = 1


Augmentations: TypeAlias = list[Augmentation]


@dataclass
class TargetFile(DataClassSonusAIMixin):
    name: Location
    samples: int
    truth_settings: TruthSettings
    class_balancing_augmentation: Optional[Augmentation] = None
    target_level_type: Optional[str] = None

    @property
    def duration(self) -> float:
        from sonusai.mixture import SAMPLE_RATE

        return self.samples / SAMPLE_RATE


TargetFiles: TypeAlias = list[TargetFile]


@dataclass
class AugmentedTarget(DataClassSonusAIMixin):
    target_augmentation_index: int
    target_file_index: int


AugmentedTargets: TypeAlias = list[AugmentedTarget]


@dataclass
class NoiseFile(DataClassSonusAIMixin):
    name: Location
    samples: int
    augmentations: Optional[Augmentations] = None

    @property
    def duration(self) -> float:
        from sonusai.mixture import SAMPLE_RATE

        return self.samples / SAMPLE_RATE


NoiseFiles: TypeAlias = list[NoiseFile]
ClassCount: TypeAlias = list[int]

GeneralizedIDs: TypeAlias = str | int | list[int] | range


@dataclass(frozen=True)
class TruthFunctionConfig(DataClassSonusAIMixin):
    feature: str
    mutex: bool
    num_classes: int
    target_gain: float
    config: Optional[dict] = None
    function: Optional[str] = None
    index: Optional[list[int]] = None


@dataclass
class GenMixData:
    targets: AudiosT = None
    noise: AudioT = None
    mixture: AudioT = None
    truth_t: Optional[Truth] = None
    segsnr_t: Optional[Segsnr] = None


@dataclass
class GenFTData:
    feature: Optional[Feature] = None
    truth_f: Optional[Truth] = None
    segsnr: Optional[Segsnr] = None


@dataclass
class ImpulseResponseData:
    name: Location
    sample_rate: int
    data: AudioT

    @property
    def length(self) -> int:
        return len(self.data)


ImpulseResponseFiles: TypeAlias = list[Location]


@dataclass(frozen=True)
class SpectralMask:
    f_max_width: int
    f_num: int
    t_max_width: int
    t_num: int
    t_max_percent: int


SpectralMasks: TypeAlias = list[SpectralMask]


@dataclass(frozen=True)
class UniversalSNR:
    is_random: bool
    raw_value: float | str

    @property
    def value(self) -> float:
        from sonusai.mixture import evaluate_random_rule

        if self.is_random:
            return float(evaluate_random_rule(str(self.raw_value)))

        return float(self.raw_value)
