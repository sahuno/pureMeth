"""
Utility functions for pureMeth package
"""

import os
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


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