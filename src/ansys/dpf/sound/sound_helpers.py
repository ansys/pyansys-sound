"""Sound helpers."""
__all__ = ("load_wav_signal", "write_wav_signal")

from ansys.dpf.core import DataSources, Operator, fields_container


def load_wav_signal(
    input_path: str = "",
) -> fields_container:
    """Load a wav file from its input path.

    Load a .wav file stored in memory using DPF Sound capabilities

    Parameters
    ----------
    input_path:
        The input path of the .wav file.
    """
    op_load_wav = Operator("load_wav_sas")  # For loading WAVs

    # Loading a WAV file
    data_source_in = DataSources()

    # Creating input path
    data_source_in.add_file_path(input_path, ".wav")

    # Loading wav file and storing it into a container
    op_load_wav.connect(0, data_source_in)

    # Obtaining the output as a fieldsContainer
    fc_signal = op_load_wav.get_output(0, "fields_container")
    return fc_signal


def write_wav_signal(
    output_path: str = "",
    data: fields_container = None,
    bit_depth: str = "int16",
) -> None:
    """Write a wav file with its output path and its bit depth.

    Load a .wav file stored in memory using DPF Sound capabilities

    Parameters
    ----------
    output_path:
        Path of the wav file to save.
    data:
        Signal to save: fields_container with each channel as a field.
    bit_depth:
        Bit depth. Supported values are: 'float32', 'int32', 'int16', 'int8'.
        This means that the samples will be respectively coded into the wav file
        using 32 bits (32-bit IEEE Float), 32 bits (int), 16 bits (int) or 8 bits (int).
    """
    op_write_wav = Operator("write_wav_sas")  # For writing WAV

    data_source_out = DataSources()
    data_source_out.add_file_path(output_path, ".wav")

    op_write_wav.connect(0, data)
    op_write_wav.connect(1, data_source_out)
    op_write_wav.connect(2, bit_depth)

    op_write_wav.run()

    return
