#!/usr/bin/env python3
"""
Example usage of pureMeth package
"""

from pureMeth.utils import (
    generate_samples_yaml, 
    list_sample_files, 
    validate_samples_yaml,
    generate_tumor_normal_yaml,
    create_patient_bams_from_directory,
    validate_tumor_normal_yaml
)
from pathlib import Path


def example_basic_usage():
    """Basic example of generating samples YAML"""
    print("=== Basic Usage Example ===")
    
    # Example: Search for .fast5 files in a directory
    data_directory = "/path/to/your/nanopore/data"
    
    try:
        # Generate samples YAML file
        yaml_file = generate_samples_yaml(
            directory=data_directory,
            file_extension=".fast5",
            output_filename="my_samples"
        )
        
        print(f"Generated YAML file: {yaml_file}")
        
        # Validate the generated file
        if validate_samples_yaml(yaml_file):
            print("✓ YAML file is valid")
        else:
            print("✗ YAML file validation failed")
            
    except FileNotFoundError:
        print(f"Directory not found: {data_directory}")
        print("Please update the data_directory path to point to your actual data")
    except ValueError as e:
        print(f"Error: {e}")


def example_with_different_extensions():
    """Example with different file extensions"""
    print("\n=== Different File Extensions Example ===")
    
    extensions = [".fast5", ".pod5", ".bam", ".sam"]
    data_directory = "/path/to/your/nanopore/data"
    
    for ext in extensions:
        try:
            files = list_sample_files(data_directory, ext)
            print(f"Found {len(files)} files with extension '{ext}'")
            
            if files:
                # Generate YAML for this extension
                yaml_file = generate_samples_yaml(
                    directory=data_directory,
                    file_extension=ext,
                    output_filename=f"samples_{ext[1:]}"  # Remove the dot
                )
                print(f"Generated: {yaml_file}")
                
        except Exception as e:
            print(f"Error processing {ext}: {e}")


def example_custom_workflow():
    """Example of a custom workflow"""
    print("\n=== Custom Workflow Example ===")
    
    # Define your data structure
    base_dir = "/path/to/project"
    subdirs = ["run1", "run2", "run3"]
    
    for subdir in subdirs:
        full_path = f"{base_dir}/{subdir}"
        try:
            # Generate samples for each run
            yaml_file = generate_samples_yaml(
                directory=full_path,
                file_extension=".fast5",
                output_filename=f"samples_{subdir}"
            )
            
            print(f"Generated samples file for {subdir}: {yaml_file}")
            
        except Exception as e:
            print(f"Skipping {subdir}: {e}")


def example_tumor_normal_yaml():
    """Example of tumor-normal YAML generation"""
    print("\n=== Tumor-Normal YAML Example ===")
    
    # Example 1: From predefined patient_bams structure
    patient_bams = {
        'SHAH_H000033': {
            'TUMOR': ['/data/analyses/SHAH_H000033_T16_04_WG01_R1.sorted.bam'],
            'NORMAL': ['/data/analyses/SHAH_H000033_N03_01_WG01_R1.sorted.bam']
        },
        'SHAH_H000024': {
            'TUMOR': [
                '/data/analyses/SHAH_H000024_T08_04_WG01_R1.sorted.bam',
                '/data/analyses/SHAH_H000024_T02_04_WG01_R1.sorted.bam'
            ],
            'NORMAL': ['/data/analyses/SHAH_H000024_N03_01_WG01_R1.sorted.bam']
        }
    }
    
    try:
        # Generate tumor-normal YAML
        yaml_file = generate_tumor_normal_yaml(
            patient_bams=patient_bams,
            output_filename="tumor_normal_samples"
        )
        print(f"Generated tumor-normal YAML: {yaml_file}")
        
        # Validate the generated YAML
        if validate_tumor_normal_yaml(yaml_file):
            print("✓ Tumor-normal YAML is valid")
        else:
            print("✗ Tumor-normal YAML validation failed")
            
    except Exception as e:
        print(f"Error generating tumor-normal YAML: {e}")


def example_tumor_normal_from_directory():
    """Example of creating tumor-normal YAML from directory"""
    print("\n=== Tumor-Normal from Directory Example ===")
    
    bam_directory = "/path/to/bam/files"
    
    try:
        # Create patient_bams structure from directory
        patient_bams = create_patient_bams_from_directory(
            directory=bam_directory,
            patient_pattern="SHAH_H",
            tumor_pattern="_T",
            normal_pattern="_N",
            file_extension=".sorted.bam"
        )
        
        print(f"Found {len(patient_bams)} patients")
        for patient_id, samples in patient_bams.items():
            tumor_count = len(samples.get('TUMOR', []))
            normal_count = len(samples.get('NORMAL', []))
            print(f"  {patient_id}: {tumor_count} tumor, {normal_count} normal")
        
        # Generate YAML from discovered samples
        if patient_bams:
            yaml_file = generate_tumor_normal_yaml(
                patient_bams=patient_bams,
                output_filename="discovered_tumor_normal_samples"
            )
            print(f"Generated YAML: {yaml_file}")
        else:
            print("No tumor-normal samples found in directory")
            
    except FileNotFoundError:
        print(f"Directory not found: {bam_directory}")
        print("Please update the bam_directory path to point to your BAM files")
    except Exception as e:
        print(f"Error: {e}")


def example_custom_tumor_normal_patterns():
    """Example with custom tumor-normal patterns"""
    print("\n=== Custom Tumor-Normal Patterns Example ===")
    
    # Example with different naming conventions
    custom_patient_bams = {
        'PATIENT_001': {
            'TUMOR': ['/data/PATIENT_001_tumor_sample1.bam'],
            'NORMAL': ['/data/PATIENT_001_normal_sample1.bam']
        },
        'PATIENT_002': {
            'TUMOR': [
                '/data/PATIENT_002_tumor_primary.bam',
                '/data/PATIENT_002_tumor_metastasis.bam'
            ],
            'NORMAL': ['/data/PATIENT_002_normal_blood.bam']
        }
    }
    
    try:
        # Generate YAML with custom file extension
        yaml_file = generate_tumor_normal_yaml(
            patient_bams=custom_patient_bams,
            output_filename="custom_tumor_normal",
            file_extension=".bam"  # Different extension
        )
        
        print(f"Generated custom tumor-normal YAML: {yaml_file}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("pureMeth Usage Examples")
    print("=" * 50)
    
    # Note: Update the paths below to match your actual data location
    print("Note: Please update the data directory paths in this script")
    print("to point to your actual Oxford Nanopore data location.\n")
    
    example_basic_usage()
    example_with_different_extensions()
    example_custom_workflow()
    
    # Tumor-normal examples
    example_tumor_normal_yaml()
    example_tumor_normal_from_directory() 
    example_custom_tumor_normal_patterns()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("Remember to update the paths to your actual data directories.")