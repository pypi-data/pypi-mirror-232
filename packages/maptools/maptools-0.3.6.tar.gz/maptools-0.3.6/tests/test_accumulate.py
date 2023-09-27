import os.path
import tempfile
import maptools


def test_accumulate(ideal_map_filename):
    _, output_map_filename = tempfile.mkstemp()

    maptools.accumulate(
        [ideal_map_filename] * 5,
        output_map_filename=output_map_filename,
    )

    assert os.path.exists(output_map_filename)
