import logging
import pathlib
import unittest

from aurora.pipelines.transfer_function_kernel import TransferFunctionKernel
from aurora.general_helper_functions import DotDict
from aurora.general_helper_functions import TEST_PATH


class TestTransferFunctionKernel(unittest.TestCase):
    """ """

    def setUp(self):
        self._tf = TransferFunctionKernel()

    def test_count_lines(self):
        tmp_file = TEST_PATH.joinpath("tmp.txt")
        n_lines_in = 42
        lines = n_lines_in * ["test\n"]
        f = open(tmp_file, "w")
        f.writelines(lines)
        f.close()
        n_lines_out = count_lines(tmp_file)
        assert n_lines_out == n_lines_in
        tmp_file.unlink()
        return

    def test_dot_dict(self):
        tmp = {}
        tmp["a"] = "aa"
        tmp["b"] = "bb"
        dot_dict = DotDict(tmp)
        assert dot_dict.a == tmp["a"]
        assert dot_dict.b == "bb"


def main():
    # tmp = TestMetadataValuesSetCorrect()
    # tmp.setUp()
    # tmp.test_start_times_correct()
    unittest.main()


if __name__ == "__main__":
    main()
