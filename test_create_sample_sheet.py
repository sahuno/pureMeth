import os
import csv
import unittest
import tempfile
import shutil
from create_sample_sheet import tum_norm_tsv

class TestTumNormTsv(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir) # Ensure cleanup

        # Create a structure similar to the example
        # /<temp_dir>/data_root/patient1/normal/sample1_N01/sample1_N01_file.bed
        # /<temp_dir>/data_root/patient1/tumor/sample1_T01/sample1_T01_file.bed
        # /<temp_dir>/data_root/patient2/normal/sample2_N01/sample2_N01_file.txt (wrong_ext)
        # /<temp_dir>/data_root/patient2/tumor/sample2_T01/sample2_T01_file.bed
        # /<temp_dir>/data_root/patient3/other_condition/sample3_X01/sample3_X01_file.bed (unknown condition)

        self.structure = {
            "data_root": {
                "patient1": {
                    "normal": {
                        "sample1_N01": ["sample1_N01_file.bed", "another_file.txt"]
                    },
                    "tumor": {
                        "sample1_T01": ["sample1_T01_file.bed"]
                    }
                },
                "patient2": {
                    "normal": {
                        "sample2_N01": ["sample2_N01_file.txt"] # Should be ignored by .bed search
                    },
                    "tumor": {
                        "sample2_T01": ["sample2_T01_file.bed"]
                    }
                },
                "patient3": {
                    "other_condition": { # This should result in 'Unknown' condition
                        "sample3_X01": ["sample3_X01_file.bed"]
                    }
                },
                "patient4_nodirs": ["patient4_file.bed"] # File directly under patient
            }
        }

        self._create_dir_structure(self.test_dir, self.structure)
        self.output_tsv_file = os.path.join(self.test_dir, "output.tsv")
        self.search_dir = os.path.join(self.test_dir, "data_root")


    def _create_dir_structure(self, base_path, structure_dict):
        for name, content in structure_dict.items():
            current_path = os.path.join(base_path, name)
            if isinstance(content, dict): # It's a directory
                os.makedirs(current_path, exist_ok=True)
                self._create_dir_structure(current_path, content)
            elif isinstance(content, list): # It's a list of files under directory 'name'
                # 'current_path' is base_path/name, this is the directory where files should reside
                os.makedirs(current_path, exist_ok=True) # Ensure this directory (e.g. .../sample1_N01) exists
                for file_name_in_list in content:
                    with open(os.path.join(current_path, file_name_in_list), 'w') as f:
                        f.write("dummy content") # Create the file inside 'current_path'

    def test_sample_sheet_creation(self):
        tum_norm_tsv(self.search_dir, ".bed", self.output_tsv_file)

        self.assertTrue(os.path.exists(self.output_tsv_file))

        expected_rows = [
            {
                "patient": "patient1", "sample": "sample1_N01", "condition": "Normal",
                "path": os.path.join(self.search_dir, "patient1", "normal", "sample1_N01", "sample1_N01_file.bed")
            },
            {
                "patient": "patient1", "sample": "sample1_T01", "condition": "Tumor",
                "path": os.path.join(self.search_dir, "patient1", "tumor", "sample1_T01", "sample1_T01_file.bed")
            },
            {
                "patient": "patient2", "sample": "sample2_T01", "condition": "Tumor",
                "path": os.path.join(self.search_dir, "patient2", "tumor", "sample2_T01", "sample2_T01_file.bed")
            },
            {
                "patient": "patient3", "sample": "sample3_X01", "condition": "Unknown", # because of 'other_condition'
                "path": os.path.join(self.search_dir, "patient3", "other_condition", "sample3_X01", "sample3_X01_file.bed")
            },
             {
                "patient": "patient4_nodirs", "sample": "Unknown", "condition": "Unknown", # No tumor/normal dirs
                "path": os.path.join(self.search_dir, "patient4_nodirs", "patient4_file.bed")
            }
        ]

        with open(self.output_tsv_file, 'r', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            actual_rows = list(reader)

        self.assertEqual(len(actual_rows), len(expected_rows))

        # Normalize paths for comparison and sort for consistent order
        for row in actual_rows:
            row['path'] = os.path.normpath(row['path'])
        for row in expected_rows:
            row['path'] = os.path.normpath(row['path'])

        # Sort based on path for consistent comparison
        actual_rows_sorted = sorted(actual_rows, key=lambda x: x['path'])
        expected_rows_sorted = sorted(expected_rows, key=lambda x: x['path'])


        for actual, expected in zip(actual_rows_sorted, expected_rows_sorted):
            self.assertEqual(actual['patient'], expected['patient'])
            self.assertEqual(actual['sample'], expected['sample'])
            self.assertEqual(actual['condition'], expected['condition'])
            self.assertEqual(actual['path'], expected['path'])

    def test_different_extension(self):
        # Test with '.txt' extension
        tum_norm_tsv(self.search_dir, ".txt", self.output_tsv_file)
        self.assertTrue(os.path.exists(self.output_tsv_file))

        expected_rows = [
            {
                "patient": "patient1", "sample": "sample1_N01", "condition": "Normal",
                "path": os.path.join(self.search_dir, "patient1", "normal", "sample1_N01", "another_file.txt")
            },
            {
                "patient": "patient2", "sample": "sample2_N01", "condition": "Normal", # This was .txt
                "path": os.path.join(self.search_dir, "patient2", "normal", "sample2_N01", "sample2_N01_file.txt")
            }
        ]

        with open(self.output_tsv_file, 'r', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            actual_rows = list(reader)

        self.assertEqual(len(actual_rows), len(expected_rows))

        for row in actual_rows:
            row['path'] = os.path.normpath(row['path'])
        for row in expected_rows:
            row['path'] = os.path.normpath(row['path'])

        actual_rows_sorted = sorted(actual_rows, key=lambda x: x['path'])
        expected_rows_sorted = sorted(expected_rows, key=lambda x: x['path'])

        for actual, expected in zip(actual_rows_sorted, expected_rows_sorted):
            self.assertEqual(actual['patient'], expected['patient'])
            self.assertEqual(actual['sample'], expected['sample'])
            self.assertEqual(actual['condition'], expected['condition'])
            self.assertEqual(actual['path'], expected['path'])

    def test_no_matching_files(self):
        tum_norm_tsv(self.search_dir, ".nonexistent", self.output_tsv_file)
        self.assertTrue(os.path.exists(self.output_tsv_file))
        with open(self.output_tsv_file, 'r', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            self.assertEqual(reader.fieldnames, ["patient", "sample", "condition", "path"])
            self.assertEqual(len(list(reader)), 0) # No data rows

    def test_extension_without_dot(self):
        # Test if providing extension 'bed' (no dot) works the same as '.bed'
        tum_norm_tsv(self.search_dir, "bed", self.output_tsv_file) # No dot
        self.assertTrue(os.path.exists(self.output_tsv_file))

        # Same expected as test_sample_sheet_creation
        with open(self.output_tsv_file, 'r', newline='') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            actual_rows = list(reader)
        self.assertEqual(len(actual_rows), 5) # From the .bed files

if __name__ == '__main__':
    unittest.main()
