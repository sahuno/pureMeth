"""
Utility functions for pureMeth package
"""

import os
import csv
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union
from collections import defaultdict


def generate_samples_yaml(
    directory: str, 
    file_extension: str, 
    output_filename: Optional[str] = None
) -> str:
    """
    Recursively search directory and generate samples_[date_time].yaml file
    
    Args:
        directory (str): Path to directory to search
        file_extension (str): File extension to search for (e.g., '.fast5', '.pod5')
        output_filename (str, optional): Custom output filename (without extension)
                                       If None, uses format 'samples_[datetime]'
    
    Returns:
        str: Path to generated YAML file
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If no files with specified extension found
    """
    # Validate directory exists
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Ensure file extension starts with dot
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Find all files with specified extension recursively
    sample_files = []
    for file_path in directory_path.rglob(f'*{file_extension}'):
        if file_path.is_file():
            sample_files.append(file_path)
    
    if not sample_files:
        raise ValueError(f"No files with extension '{file_extension}' found in {directory}")
    
    # Create samples dictionary
    samples_dict = {"samples": {}}
    
    for file_path in sorted(sample_files):
        # Use filename without extension as sample name
        sample_name = file_path.stem
        # Use absolute path for sample location
        samples_dict["samples"][sample_name] = str(file_path.absolute())
    
    # Generate output filename with timestamp if not provided
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"samples_{timestamp}"
    
    # Ensure .yaml extension
    if not output_filename.endswith('.yaml') and not output_filename.endswith('.yml'):
        output_filename += '.yaml'
    
    # Write YAML file to current working directory
    output_path = Path.cwd() / output_filename
    
    with open(output_path, 'w') as yaml_file:
        yaml.dump(samples_dict, yaml_file, default_flow_style=False, indent=2)
    
    print(f"Generated YAML file: {output_path}")
    print(f"Found {len(sample_files)} samples with extension '{file_extension}'")
    
    return str(output_path)


def list_sample_files(directory: str, file_extension: str) -> List[Path]:
    """
    List all files with specified extension in directory (recursive)
    
    Args:
        directory (str): Path to directory to search
        file_extension (str): File extension to search for
        
    Returns:
        List[Path]: List of file paths
    """
    directory_path = Path(directory)
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
        
    return list(directory_path.rglob(f'*{file_extension}'))


def validate_samples_yaml(yaml_file: str) -> bool:
    """
    Validate that a samples YAML file has correct structure
    
    Args:
        yaml_file (str): Path to YAML file
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            return False
            
        if 'samples' not in data:
            return False
            
        if not isinstance(data['samples'], dict):
            return False
            
        # Check that all sample paths exist
        for sample_name, sample_path in data['samples'].items():
            if not Path(sample_path).exists():
                print(f"Warning: Sample file not found: {sample_path}")
                
        return True
        
    except Exception as e:
        print(f"Error validating YAML file: {e}")
        return False


def generate_tumor_normal_yaml(
    patient_bams: Dict[str, Dict[str, List[str]]], 
    output_filename: Optional[str] = None,
    file_extension: str = ".sorted.bam"
) -> str:
    """
    Generate tumor-normal samples YAML from patient BAM data structure
    
    Args:
        patient_bams (Dict): Dictionary with patient IDs as keys and sample types (TUMOR/NORMAL) as values
        output_filename (str, optional): Custom output filename (without extension)
        file_extension (str): File extension to remove from sample names (default: ".sorted.bam")
    
    Returns:
        str: Path to generated YAML file
        
    Example:
        patient_bams = {
            'SHAH_H000033': {
                'TUMOR': ['/path/to/tumor.sorted.bam'],
                'NORMAL': ['/path/to/normal.sorted.bam']
            }
        }
    """
    yaml_structure = {'SAMPLES': {}}
    
    for patient_id, sample_types in patient_bams.items():
        patient_data = {}
        for sample_type, bam_paths in sample_types.items():
            if bam_paths:  # Only add if there are BAM files
                patient_data[sample_type] = {}
                for bam_path in bam_paths:
                    # Extract sample name from the BAM file path
                    filename = os.path.basename(bam_path)
                    sample_name = filename.replace(file_extension, '')
                    patient_data[sample_type][sample_name] = bam_path
        
        # Add patient data directly under patient ID
        yaml_structure['SAMPLES'][patient_id] = patient_data
    
    # Generate output filename with timestamp if not provided
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"tumor_normal_samples_{timestamp}"
    
    # Ensure .yaml extension
    if not output_filename.endswith('.yaml') and not output_filename.endswith('.yml'):
        output_filename += '.yaml'
    
    # Write YAML file to current working directory
    output_path = Path.cwd() / output_filename
    
    # Custom representer to format the output nicely
    def dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items()
        )
    
    yaml.add_representer(dict, dict_representer)
    
    with open(output_path, 'w') as f:
        yaml.dump(yaml_structure, f, default_flow_style=False, sort_keys=False, indent=2)
    
    # Count samples
    total_patients = len(patient_bams)
    total_samples = sum(len(types) for types in patient_bams.values() for types in types.values())
    
    print(f"Generated tumor-normal YAML file: {output_path}")
    print(f"Processed {total_patients} patients with {total_samples} total samples")
    
    return str(output_path)


def create_patient_bams_from_directory(
    directory: str,
    patient_pattern: str = "SHAH_H",
    tumor_pattern: str = "_T",
    normal_pattern: str = "_N",
    file_extension: str = ".sorted.bam"
) -> Dict[str, Dict[str, List[str]]]:
    """
    Create patient_bams dictionary from directory containing BAM files
    
    Args:
        directory (str): Directory containing BAM files
        patient_pattern (str): Pattern to identify patient ID in filename
        tumor_pattern (str): Pattern to identify tumor samples
        normal_pattern (str): Pattern to identify normal samples
        file_extension (str): File extension for BAM files
        
    Returns:
        Dict: patient_bams structure suitable for generate_tumor_normal_yaml
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    patient_bams = defaultdict(lambda: defaultdict(list))
    
    # Find all BAM files
    bam_files = list(directory_path.rglob(f'*{file_extension}'))
    
    for bam_file in bam_files:
        filename = bam_file.name
        
        # Extract patient ID (assuming it starts after patient_pattern)
        if patient_pattern in filename:
            patient_start = filename.find(patient_pattern)
            patient_id_part = filename[patient_start:]
            
            # Extract patient ID (until first underscore after pattern)
            patient_id = patient_id_part.split('_')[0] + '_' + patient_id_part.split('_')[1]
            
            # Determine sample type
            if tumor_pattern in filename:
                sample_type = 'TUMOR'
            elif normal_pattern in filename:
                sample_type = 'NORMAL'
            else:
                continue  # Skip files that don't match tumor/normal pattern
            
            patient_bams[patient_id][sample_type].append(str(bam_file.absolute()))
    
    return dict(patient_bams)


def validate_tumor_normal_yaml(yaml_file: str) -> bool:
    """
    Validate tumor-normal YAML file structure
    
    Args:
        yaml_file (str): Path to YAML file
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            return False
            
        if 'SAMPLES' not in data:
            return False
            
        if not isinstance(data['SAMPLES'], dict):
            return False
        
        # Validate structure for each patient
        for patient_id, patient_data in data['SAMPLES'].items():
            if not isinstance(patient_data, dict):
                return False
            
            for sample_type, samples in patient_data.items():
                if sample_type not in ['TUMOR', 'NORMAL']:
                    print(f"Warning: Unexpected sample type '{sample_type}' for patient {patient_id}")
                
                if not isinstance(samples, dict):
                    return False
                
                # Check that sample files exist
                for sample_name, sample_path in samples.items():
                    if not Path(sample_path).exists():
                        print(f"Warning: Sample file not found: {sample_path}")
        
        return True
        
    except Exception as e:
        print(f"Error validating tumor-normal YAML file: {e}")
        return False


def generate_samples_tsv(
    directory: str,
    file_extension: str,
    output_filename: Optional[str] = None,
    condition_patterns: Optional[Dict[str, List[str]]] = None
) -> str:
    """
    Generate TSV file with sample metadata from directory structure
    
    Args:
        directory (str): Directory to search for files
        file_extension (str): File extension to search for (e.g., '.bed', '.bam')
        output_filename (str, optional): Custom output filename (without extension)
                                       If None, uses format 'samples_[datetime].tsv'
        condition_patterns (Dict[str, List[str]], optional): Dictionary mapping condition names to patterns
                                                           Default: {'Tumor': ['tumor'], 'Normal': ['normal']}
    
    Returns:
        str: Path to generated TSV file
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        ValueError: If no files with specified extension found
    """
    
    # Validate directory exists
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Ensure file extension starts with dot
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Set default condition patterns if not provided
    if condition_patterns is None:
        condition_patterns = {
            'Tumor': ['tumor'],
            'Normal': ['normal']
        }
    
    header = ["patient", "sample", "condition", "path"]
    rows = []
    
    # Find all files with specified extension
    for file_path in directory_path.rglob(f'*{file_extension}'):
        if file_path.is_file():
            full_path = str(file_path.absolute())
            path_parts = full_path.split(os.sep)
            
            patient = "Unknown"
            sample = "Unknown"
            condition_val = "Unknown"
            
            # Try to find condition in path
            condition_index = -1
            for i, part in enumerate(path_parts):
                part_lower = part.lower()
                for condition, patterns in condition_patterns.items():
                    if any(pattern.lower() in part_lower for pattern in patterns):
                        condition_val = condition
                        condition_index = i
                        break
                if condition_index != -1:
                    break
            
            if condition_index != -1:  # Condition was found
                # Patient extraction - look for directory before condition
                if condition_index - 1 >= 0:
                    patient = path_parts[condition_index - 1]
                
                # Sample extraction - look for directory after condition
                if condition_index + 1 < len(path_parts) - 1:  # -1 to exclude filename
                    sample = path_parts[condition_index + 1]
            
            else:  # Condition not found, use fallback logic
                # Get path relative to search directory
                relative_path = os.path.relpath(full_path, os.path.normpath(str(directory)))
                relative_path_parts = relative_path.split(os.sep)
                
                if len(relative_path_parts) >= 2:  # At least patient_dir/file.ext
                    patient = relative_path_parts[0]
                    
                    if len(relative_path_parts) >= 3:  # patient_dir/.../sample_dir/file.ext
                        # Sample is the directory containing the file
                        sample = relative_path_parts[-2]
            
            rows.append({
                "patient": patient,
                "sample": sample,
                "condition": condition_val,
                "path": full_path
            })
    
    if not rows:
        raise ValueError(f"No files with extension '{file_extension}' found in {directory}")
    
    # Generate output filename with timestamp if not provided
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"samples_{timestamp}"
    
    # Ensure .tsv extension
    if not output_filename.endswith('.tsv'):
        output_filename += '.tsv'
    
    # Write TSV file to current working directory
    output_path = Path.cwd() / output_filename
    
    with open(output_path, 'w', newline='') as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=header, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Generated TSV file: {output_path}")
    print(f"Found {len(rows)} samples with extension '{file_extension}'")
    
    return str(output_path)


def create_patient_samples_from_directory(
    directory: str,
    file_extension: str,
    patient_pattern: Optional[str] = None,
    condition_patterns: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Create patient samples dictionary from directory structure
    
    Args:
        directory (str): Directory containing sample files
        file_extension (str): File extension to search for
        patient_pattern (str, optional): Pattern to identify patient ID in path
        condition_patterns (Dict[str, List[str]], optional): Dictionary mapping condition names to patterns
        
    Returns:
        Dict: Nested dictionary structure {patient: {condition: {sample: path}}}
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    # Ensure file extension starts with dot
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension
    
    # Set default condition patterns if not provided
    if condition_patterns is None:
        condition_patterns = {
            'TUMOR': ['tumor'],
            'NORMAL': ['normal']
        }
    
    patient_samples = defaultdict(lambda: defaultdict(dict))
    
    # Find all files with specified extension
    for file_path in directory_path.rglob(f'*{file_extension}'):
        if file_path.is_file():
            full_path = str(file_path.absolute())
            path_parts = full_path.split(os.sep)
            
            patient = None
            condition = None
            sample = file_path.stem  # Default sample name is filename without extension
            
            # Try to find condition in path
            for i, part in enumerate(path_parts):
                part_lower = part.lower()
                for cond_name, patterns in condition_patterns.items():
                    if any(pattern.lower() in part_lower for pattern in patterns):
                        condition = cond_name
                        
                        # Extract patient ID (directory before condition)
                        if i - 1 >= 0:
                            patient = path_parts[i - 1]
                        
                        # Extract sample name (directory after condition, if exists)
                        if i + 1 < len(path_parts) - 1:
                            sample = path_parts[i + 1]
                        
                        break
                
                if condition:
                    break
            
            # If patient pattern provided and patient not found, try pattern matching
            if patient_pattern and not patient:
                for part in path_parts:
                    if patient_pattern in part:
                        patient = part
                        break
            
            # Only add if we found both patient and condition
            if patient and condition:
                patient_samples[patient][condition][sample] = full_path
    
    return dict(patient_samples)