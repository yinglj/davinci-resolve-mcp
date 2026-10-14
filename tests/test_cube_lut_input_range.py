"""A 3D .cube that declares LUT_3D_INPUT_RANGE must still be readable.

Blackmagic's LUT README (docs/notes/lut-notes.md) gives `LUT_3D_INPUT_RANGE
MIN_VAL MAX_VAL` as a 3D header keyword. read_cube took the line for a data row
and refused the whole file as a "non-numeric entry", so neither the summary nor
the attenuation tool could open it.
"""
import os
import tempfile
import unittest
from unittest.mock import patch

from src.granular import graph as granular
from src.utils import cube_lut, lut_files

RANGED_CUBE = """TITLE "ranged"
LUT_3D_SIZE 2
LUT_3D_INPUT_RANGE 0.0 1.0
0.0 0.0 0.0
1.0 0.0 0.0
0.0 1.0 0.0
1.0 1.0 0.0
0.0 0.0 1.0
1.0 0.0 1.0
0.0 1.0 1.0
1.0 1.0 1.0
"""


class InputRangeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        patcher = patch.object(lut_files, "master_lut_dir", return_value=self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, relative, text):
        path = os.path.join(self.root, relative)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_summary_reads_the_range_as_the_domain(self):
        self.write("ranged.cube", RANGED_CUBE)
        summary = lut_files.read_lut_summary("ranged.cube")
        self.assertTrue(summary["parsed"])
        self.assertEqual(summary["size"], 2)
        self.assertEqual(summary["domain_min"], [0.0, 0.0, 0.0])
        self.assertEqual(summary["domain_max"], [1.0, 1.0, 1.0])

    def test_attenuate_tool_accepts_a_unit_input_range(self):
        self.write("ranged.cube", RANGED_CUBE)
        result = granular.attenuate_lut_file("ranged.cube", 0.5, "ranged_half.cube")
        self.assertTrue(result.get("success"), result)
        written = cube_lut.read_cube(os.path.join(lut_files.writable_dir(), "ranged_half.cube"))
        self.assertEqual(written["size"], 2)

    def test_non_unit_input_range_is_still_refused_for_attenuation(self):
        self.write("wide.cube", RANGED_CUBE.replace("0.0 1.0\n", "0.0 4.0\n", 1))
        self.assertEqual(lut_files.read_lut_summary("wide.cube")["domain_max"], [4.0, 4.0, 4.0])
        with self.assertRaises(cube_lut.CubeLutError):
            lut_files.attenuate_lut("wide.cube", 0.5, "wide_half.cube")


if __name__ == "__main__":
    unittest.main()
