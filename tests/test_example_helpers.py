from ansys.sound.core.examples_helpers import (
    get_absolute_path_for_accel_with_rpm_wav,
    get_absolute_path_for_fluctuating_noise_wav,
    get_absolute_path_for_fluctuating_tone_wav,
    get_absolute_path_for_flute2_wav,
    get_absolute_path_for_flute_wav,
    get_absolute_path_for_rough_noise_wav,
    get_absolute_path_for_rough_tone_wav,
    get_absolute_path_for_sharp_noise_wav,
    get_absolute_path_for_sharper_noise_wav,
)


def test_data_path_flute_wav():
    p = get_absolute_path_for_flute_wav()
    assert p == "C:\\data\\flute.wav"


def test_data_path_flute2_wav():
    p = get_absolute_path_for_flute2_wav()
    assert p == "C:\\data\\flute2.wav"


def test_data_path_accel_with_rpm_wav():
    p = get_absolute_path_for_accel_with_rpm_wav()
    assert p == "C:\\data\\accel_with_rpm.wav"


def test_data_path_sharp_noise_wav():
    p = get_absolute_path_for_sharp_noise_wav()
    assert p == "C:\\data\\sharp_noise.wav"


def test_data_path_sharper_noise_wav():
    p = get_absolute_path_for_sharper_noise_wav()
    assert p == "C:\\data\\sharper_noise.wav"


def test_data_path_rough_noise_wav():
    p = get_absolute_path_for_rough_noise_wav()
    assert p == "C:\\data\\rough_noise.wav"


def test_data_path_rough_tone_wav():
    p = get_absolute_path_for_rough_tone_wav()
    assert p == "C:\\data\\rough_tone.wav"


def test_data_path_fluctuating_noise_wav():
    p = get_absolute_path_for_fluctuating_noise_wav()
    assert p == "C:\\data\\fluctuating_noise.wav"


def test_data_path_fluctuating_tone_wav():
    p = get_absolute_path_for_fluctuating_tone_wav()
    assert p == "C:\\data\\fluctuating_tone.wav"
