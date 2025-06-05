"""
Tests for pureMeth utils module
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml
from pureMeth.utils import (
    generate_samples_yaml, 
    list_sample_files, 
    validate_samples_yaml,
    generate_tumor_normal_yaml,
    create_patient_bams_from_directory,
    validate_tumor_normal_yaml
)


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


class TestTumorNormalYaml:
    
    def test_generate_tumor_normal_yaml_basic(self):
        """Test basic tumor-normal YAML generation"""
        patient_bams = {
            'SHAH_H000033': {
                'TUMOR': ['/path/to/SHAH_H000033_T16_04_WG01_R1.sorted.bam'],
                'NORMAL': ['/path/to/SHAH_H000033_N03_01_WG01_R1.sorted.bam']
            },
            'SHAH_H000024': {
                'TUMOR': [
                    '/path/to/SHAH_H000024_T08_04_WG01_R1.sorted.bam',
                    '/path/to/SHAH_H000024_T02_04_WG01_R1.sorted.bam'
                ],
                'NORMAL': ['/path/to/SHAH_H000024_N03_01_WG01_R1.sorted.bam']
            }
        }
        
        output_file = generate_tumor_normal_yaml(patient_bams, 'test_tumor_normal')
        
        # Verify output file exists
        assert Path(output_file).exists()
        
        # Verify YAML content
        with open(output_file, 'r') as f:
            data = yaml.safe_load(f)
        
        assert 'SAMPLES' in data
        assert 'SHAH_H000033' in data['SAMPLES']
        assert 'SHAH_H000024' in data['SAMPLES']
        assert 'TUMOR' in data['SAMPLES']['SHAH_H000033']
        assert 'NORMAL' in data['SAMPLES']['SHAH_H000033']
        assert len(data['SAMPLES']['SHAH_H000024']['TUMOR']) == 2
        
        # Clean up
        os.unlink(output_file)


class TestGenerateSamplesYamlFromTsv:
    def test_generate_samples_yaml_from_tsv_basic(self, tmp_path):
        """Generate YAML from a two column TSV."""
        tsv_content = "\n".join([
            "sample1\t/path/one.fast5",
            "sample2\t/path/two.fast5",
        ])
        tsv_file = tmp_path / "samples.tsv"
        tsv_file.write_text(tsv_content)

        from pureMeth.utils import generate_samples_yaml_from_tsv

        yaml_file = generate_samples_yaml_from_tsv(str(tsv_file))

        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        assert data == {
            "samples": {
                "sample1": "/path/one.fast5",
                "sample2": "/path/two.fast5",
            }
        }

        os.unlink(yaml_file)
    
    def test_create_patient_bams_from_directory(self):
        """Test creating patient_bams structure from directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test BAM files
            test_files = [
                'SHAH_H000033_T16_04_WG01_R1.sorted.bam',
                'SHAH_H000033_N03_01_WG01_R1.sorted.bam',
                'SHAH_H000024_T08_04_WG01_R1.sorted.bam',
                'SHAH_H000024_N03_01_WG01_R1.sorted.bam'
            ]
            
            for file_name in test_files:
                (Path(temp_dir) / file_name).touch()
            
            patient_bams = create_patient_bams_from_directory(temp_dir)
            
            assert 'SHAH_H000033' in patient_bams
            assert 'SHAH_H000024' in patient_bams
            assert 'TUMOR' in patient_bams['SHAH_H000033']
            assert 'NORMAL' in patient_bams['SHAH_H000033']
            assert len(patient_bams['SHAH_H000033']['TUMOR']) == 1
            assert len(patient_bams['SHAH_H000033']['NORMAL']) == 1
    
    def test_validate_tumor_normal_yaml_valid(self):
        """Test validation of valid tumor-normal YAML"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create sample BAM files
            tumor_bam = Path(temp_dir) / 'tumor.sorted.bam'
            normal_bam = Path(temp_dir) / 'normal.sorted.bam'
            tumor_bam.touch()
            normal_bam.touch()
            
            # Create valid tumor-normal YAML
            yaml_content = {
                'SAMPLES': {
                    'PATIENT_001': {
                        'TUMOR': {
                            'tumor_sample': str(tumor_bam)
                        },
                        'NORMAL': {
                            'normal_sample': str(normal_bam)
                        }
                    }
                }
            }
            
            yaml_file = Path(temp_dir) / 'test_tumor_normal.yaml'
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            assert validate_tumor_normal_yaml(str(yaml_file)) is True
    
    def test_validate_tumor_normal_yaml_invalid_structure(self):
        """Test validation of invalid tumor-normal YAML structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid YAML (missing 'SAMPLES' key)
            yaml_content = {'DATA': {'PATIENT_001': {}}}
            
            yaml_file = Path(temp_dir) / 'test_invalid.yaml'
            with open(yaml_file, 'w') as f:
                yaml.dump(yaml_content, f)
            
            assert validate_tumor_normal_yaml(str(yaml_file)) is False
    
    def test_generate_tumor_normal_yaml_with_custom_extension(self):
        """Test tumor-normal YAML generation with custom file extension"""
        patient_bams = {
            'PATIENT_001': {
                'TUMOR': ['/path/to/tumor.bam'],
                'NORMAL': ['/path/to/normal.bam']
            }
        }
        
        output_file = generate_tumor_normal_yaml(
            patient_bams, 
            'test_custom_ext',
            file_extension='.bam'
        )
        
        # Verify output file exists
        assert Path(output_file).exists()
        
        # Verify YAML content has correct sample names
        with open(output_file, 'r') as f:
            data = yaml.safe_load(f)
        
        tumor_samples = data['SAMPLES']['PATIENT_001']['TUMOR']
        normal_samples = data['SAMPLES']['PATIENT_001']['NORMAL']
        
        # Should have .bam extension removed from sample names
        assert 'tumor' in tumor_samples
        assert 'normal' in normal_samples
        
        # Clean up
        os.unlink(output_file)


class TestGenerateSamplesYamlFromTsv:
    def test_generate_samples_yaml_from_tsv_basic(self, tmp_path):
        """Generate YAML from a two column TSV."""
        tsv_content = "\n".join([
            "sample1\t/path/one.fast5",
            "sample2\t/path/two.fast5",
        ])
        tsv_file = tmp_path / "samples.tsv"
        tsv_file.write_text(tsv_content)

        from pureMeth.utils import generate_samples_yaml_from_tsv

        yaml_file = generate_samples_yaml_from_tsv(str(tsv_file))

        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        assert data == {
            "samples": {
                "sample1": "/path/one.fast5",
                "sample2": "/path/two.fast5",
            }
        }

        os.unlink(yaml_file)

