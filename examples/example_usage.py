#!/usr/bin/env python3
"""
Example usage of pureMeth package
"""

from pureMeth.utils import generate_samples_yaml, list_sample_files, validate_samples_yaml
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


if __name__ == "__main__":
    print("pureMeth Usage Examples")
    print("=" * 50)
    
    # Note: Update the paths below to match your actual data location
    print("Note: Please update the data directory paths in this script")
    print("to point to your actual Oxford Nanopore data location.\n")
    
    example_basic_usage()
    example_with_different_extensions()
    example_custom_workflow()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("Remember to update the paths to your actual data directories.")