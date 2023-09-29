import logging
import pathlib
import unittest

from aurora.test_utils.synthetic.make_mth5_from_asc import create_test12rr_h5
from aurora.transfer_function.kernel_dataset import KernelDataset


class TestKernelDataset(unittest.TestCase):
    """ """
    @classmethod
    def setUpClass(self):
        self._mth5_path = create_test12rr_h5()
        self._kd = KernelDataset()
        self._kd.from_run_summary([self._mth5_path])

    def setUp(self):
        self._kd = KernelDataset()
        print("OK")

    def test_dot_dict(self):
        assert True

def main():
    # tmp = TestMetadataValuesSetCorrect()
    # tmp.setUp()
    # tmp.test_start_times_correct()
    unittest.main()


if __name__ == "__main__":
    main()

