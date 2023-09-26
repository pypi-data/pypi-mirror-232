from sonusai.mixture.mixdb import MRecord
from sonusai.mixture.mixdb import MixtureDatabase
from sonusai.mixture.types import AudioT
from sonusai.mixture.types import AudiosT


def _initialize_target_audio(mixdb: MixtureDatabase, mrecord: MRecord) -> AudiosT:
    """Apply augmentation and update target metadata
    """
    from sonusai.mixture import pad_audio_to_length
    from sonusai.mixture.augmentation import apply_augmentation

    targets = []
    mrecord.target_gain = []
    for idx in range(len(mrecord.target_file_index)):
        target_augmentation = mixdb.target_augmentations[mrecord.target_augmentation_index[idx]]

        targets.append(apply_augmentation(audio=mixdb.raw_target_audio(mrecord.target_file_index[idx]),
                                          augmentation=target_augmentation,
                                          length_common_denominator=mixdb.feature_step_samples))

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


def initialize_target(mixdb: MixtureDatabase, mrecord: MRecord) -> MRecord:
    """Apply augmentation and update target metadata
    """
    _initialize_target_audio(mixdb, mrecord)
    return mrecord


def _initialize_mixture_gains(mixdb: MixtureDatabase,
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
                              [mixdb.targets[index] for index in mrecord.target_file_index]]
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
