"""
Tests for pureMeth utils module
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml
from pureMeth.utils import generate_samples_yaml, list_sample_files, validate_samples_yaml


class TestGenerateSamplesYaml:
    
    def test_generate_samples_yaml_basic(self):
        """Test basic functionality of generate_samples_yaml"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = ['sample1.fast5', 'sample2.fast5', 'subdir/sample3.fast5']
            for file_path in test_files:
                full_path = Path(temp_dir) / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.touch()
            
            # Generate YAML
            output_file = generate_samples_yaml(temp_dir, '.fast5', 'test_samples')
            
            # Verify output file exists
            assert Path(output_file).exists()
            
            # Verify YAML content
            with open(output_file, 'r') as f:
                data = yaml.safe_load(f)
            
            assert 'samples' in data
            assert len(data['samples']) == 3
            assert 'sample1' in data['samples']
            assert 'sample2' in data['samples']
            assert 'sample3' in data['samples']
            
            # Clean up
            os.unlink(output_file)
    
    def test_generate_samples_yaml_nonexistent_directory(self):
        """Test error handling for nonexistent directory"""
        with pytest.raises(FileNotFoundError):
            generate_samples_yaml('/nonexistent/directory', '.fast5')
    
    def test_generate_samples_yaml_no_files_found(self):
        """Test error handling when no files with extension found"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError):
                generate_samples_yaml(temp_dir, '.fast5')
    
    def test_file_extension_normalization(self):
        """Test that file extensions are normalized (adding dot if missing)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = Path(temp_dir) / 'sample.pod5'
            test_file.touch()
            
            # Test with extension without dot
            output_file = generate_samples_yaml(temp_dir, 'pod5', 'test_samples')
            
            # Verify file was found
            with open(output_file, 'r') as f:
                data = yaml.safe_load(f)
            
            assert len(data['samples']) == 1
            
            # Clean up
            os.unlink(output_file)


class TestListSampleFiles:
    
    def test_list_sample_files(self):
        """Test listing sample files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = ['sample1.fast5', 'sample2.fast5', 'other.txt']
            for file_name in test_files:
                (Path(temp_dir) / file_name).touch()
            
            files = list_sample_files(temp_dir, '.fast5')
            
            assert len(files) == 2
            assert all(f.suffix == '.fast5' for f in files)


class TestValidateSamplesYaml:
    
    def test_validate_samples_yaml_valid(self):
        """Test validation of valid YAML file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample files
            sample1 = Path(temp_dir) / 'sample1.fast5'
            sample2 = Path(temp_dir) / 'sample2.fast5'
            sample1.touch()
            sample2.touch()
            
            # Create valid YAML
            yaml_content = {
                'samples': {
                    'sample1': str(sample1),
                    'sample2': str(sample2)
                }
            }
            
            yaml_file = Path(temp_dir) / 'test.yaml'
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            assert validate_samples_yaml(str(yaml_file)) is True
    
    def test_validate_samples_yaml_invalid_structure(self):
        """Test validation of invalid YAML structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid YAML (missing 'samples' key)
            yaml_content = {'data': {'sample1': '/path/to/file'}}
            
            yaml_file = Path(temp_dir) / 'test.yaml'
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            assert validate_samples_yaml(str(yaml_file)) is False