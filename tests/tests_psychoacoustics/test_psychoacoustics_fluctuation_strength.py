from unittest.mock import patch

from ansys.dpf.core import Field, FieldsContainer
import numpy as np
import pytest

from ansys.dpf.sound.psychoacoustics import FluctuationStrength
from ansys.dpf.sound.pydpf_sound import PyDpfSoundException, PyDpfSoundWarning
from ansys.dpf.sound.signal_utilities import LoadWav

EXP_FS_1 = 1.0416046380996704
EXP_FS_2 = 0.9974160194396973
EXP_SPECIFIC_FS_1_0 = 0.09723643958568573
EXP_SPECIFIC_FS_1_9 = 0.15443961322307587
EXP_SPECIFIC_FS_1_40 = 0.17233367264270782
EXP_SPECIFIC_FS_2_15 = 0.26900193095207214
EXP_SPECIFIC_FS_2_17 = 0.2570513188838959
EXP_SPECIFIC_FS_2_40 = 0.11656410992145538
EXP_BARK_0 = 0.5
EXP_BARK_9 = 5.0
EXP_BARK_40 = 20.5
EXP_FREQ_0 = 56.417020507724274
EXP_FREQ_9 = 498.9473684210526
EXP_FREQ_40 = 6875.975124656844


@pytest.mark.dependency()
def test_fs_instantiation(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    assert fs_computer != None


@pytest.mark.dependency(depends=["test_fs_instantiation"])
def test_fs_process(dpf_sound_test_server):
    fs_computer = FluctuationStrength()

    # No signal -> error
    with pytest.raises(
        PyDpfSoundException,
        match="No signal for fluctuation strength computation. Use FluctuationStrength.signal.",
    ):
        fs_computer.process()

    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal as field container
    fs_computer.signal = fc
    # Compute: no error
    fs_computer.process()

    # Set signal as field
    fs_computer.signal = fc[0]
    # Compute: no error
    fs_computer.process()


@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_get_output(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use FluctuationStrength.process().",
    ):
        output = fs_computer.get_output()
    assert output == None

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    (fs, specific_fs) = fs_computer.get_output()
    assert fs != None
    assert type(fs) == FieldsContainer
    assert specific_fs != None
    assert type(specific_fs) == FieldsContainer


@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_get_fluctuation_strength(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use FluctuationStrength.process().",
    ):
        output = fs_computer.get_fluctuation_strength()
    assert output == None

    # Set signal as a field
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    # Request second channel's fluctuation strength while signal is a field (mono) -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        fs = fs_computer.get_fluctuation_strength(1)

    fs = fs_computer.get_fluctuation_strength(0)
    assert type(fs) == np.float64
    assert fs == pytest.approx(EXP_FS_1)

    # Set signal as a fields container
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    # Request second channel's fluctuation strength while signal is mono -> error
    with pytest.raises(
        PyDpfSoundException, match="Specified channel index \\(1\\) does not exist."
    ):
        fs = fs_computer.get_fluctuation_strength(1)

    fs = fs_computer.get_fluctuation_strength(0)
    assert type(fs) == np.float64
    assert fs == pytest.approx(EXP_FS_1)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_fluctuating_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    fs_computer.process()

    fs = fs_computer.get_fluctuation_strength(1)
    assert type(fs) == np.float64
    assert fs == pytest.approx(EXP_FS_2)


@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_get_specific_fluctuation_strength(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use FluctuationStrength.process().",
    ):
        output = fs_computer.get_specific_fluctuation_strength()
    assert output == None

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    specific_fs = fs_computer.get_specific_fluctuation_strength()

    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_1_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_1_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_1_40)

    # Add a second signal in the fields container
    # Note: No need to re-assign the signal property, as fc is simply an alias for it
    wav_loader = LoadWav(pytest.data_path_fluctuating_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute again
    fs_computer.process()

    specific_fs = fs_computer.get_specific_fluctuation_strength(1)

    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[15] == pytest.approx(EXP_SPECIFIC_FS_2_15)
    assert specific_fs[17] == pytest.approx(EXP_SPECIFIC_FS_2_17)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_2_40)


@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_get_bark_band_indexes(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use FluctuationStrength.process().",
    ):
        output = fs_computer.get_bark_band_indexes()
    assert output == None

    # Set signal as a fields container
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    bark_band_indexes = fs_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)

    # Set signal as a field
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    bark_band_indexes = fs_computer.get_bark_band_indexes()
    assert type(bark_band_indexes) == np.ndarray
    assert len(bark_band_indexes) == 47
    assert bark_band_indexes[0] == pytest.approx(EXP_BARK_0)
    assert bark_band_indexes[9] == pytest.approx(EXP_BARK_9)
    assert bark_band_indexes[40] == pytest.approx(EXP_BARK_40)


@pytest.mark.dependency(depends=["test_fs_get_bark_band_indexes"])
def test_fs_get_bark_band_frequencies(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    # assert pytest.data_path_flute_in_container == 'toto'
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    bark_band_frequencies = fs_computer.get_bark_band_frequencies()
    assert type(bark_band_frequencies) == np.ndarray
    assert len(bark_band_frequencies) == 47
    assert bark_band_frequencies[0] == pytest.approx(EXP_FREQ_0)
    assert bark_band_frequencies[9] == pytest.approx(EXP_FREQ_9)
    assert bark_band_frequencies[40] == pytest.approx(EXP_FREQ_40)


@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_get_output_as_nparray_from_fields_container(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Fluctuation strength not calculated yet -> warning
    with pytest.warns(
        PyDpfSoundWarning,
        match="Output has not been processed yet, use FluctuationStrength.process().",
    ):
        output = fs_computer.get_output_as_nparray()
    assert output == None

    # Set signal
    fs_computer.signal = fc

    # Compute
    fs_computer.process()

    (fs, specific_fs) = fs_computer.get_output_as_nparray()

    assert type(fs) == np.ndarray
    assert len(fs) == 1
    assert fs[0] == pytest.approx(EXP_FS_1)
    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_1_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_1_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_1_40)


@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_get_output_as_nparray_from_field(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    (fs, specific_fs) = fs_computer.get_output_as_nparray()

    assert type(fs) == np.ndarray
    assert len(fs) == 1
    assert fs[0] == pytest.approx(EXP_FS_1)
    assert type(specific_fs) == np.ndarray
    assert len(specific_fs) == 47
    assert specific_fs[0] == pytest.approx(EXP_SPECIFIC_FS_1_0)
    assert specific_fs[9] == pytest.approx(EXP_SPECIFIC_FS_1_9)
    assert specific_fs[40] == pytest.approx(EXP_SPECIFIC_FS_1_40)


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_plot_from_fields_container(mock_show, dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc

    # Fluctuation strength not computed yet -> error
    with pytest.raises(
        PyDpfSoundException,
        match="Output has not been processed yet, use FluctuationStrength.process().",
    ):
        fs_computer.plot()

    # Compute
    fs_computer.process()

    # Plot
    fs_computer.plot()

    # Add a second signal in the fields container
    wav_loader = LoadWav(pytest.data_path_fluctuating_tone_in_container)
    wav_loader.process()
    fc.add_field({"channel_number": 1}, wav_loader.get_output()[0])

    # Compute
    fs_computer.process()

    # Plot
    fs_computer.plot()


@patch("matplotlib.pyplot.show")
@pytest.mark.dependency(depends=["test_fs_process"])
def test_fs_plot_from_field(mock_show, dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    # Get a signal
    wav_loader = LoadWav(pytest.data_path_fluctuating_noise_in_container)
    wav_loader.process()
    fc = wav_loader.get_output()

    # Set signal
    fs_computer.signal = fc[0]

    # Compute
    fs_computer.process()

    # Plot
    fs_computer.plot()


@pytest.mark.dependency(depends=["test_fs_instantiation"])
def test_fs_set_get_signal(dpf_sound_test_server):
    fs_computer = FluctuationStrength()
    fc = FieldsContainer()
    fc.labels = ["channel"]
    f = Field()
    f.data = 42 * np.ones(3)
    fc.add_field({"channel": 0}, f)
    fc.name = "testField"
    fs_computer.signal = fc
    fc_from_get = fs_computer.signal

    assert fc_from_get.name == "testField"
    assert len(fc_from_get) == 1
    assert fc_from_get[0].data[0, 2] == 42