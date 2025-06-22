import os
import csv
import argparse

def tum_norm_tsv(directory: str, extension: str, output_tsv_file: str):
    if not extension.startswith('.'):
        extension = '.' + extension

    header = ["patient", "sample", "condition", "path"]
    rows = []

    for root, _, files in os.walk(directory):
        for file_item in files: # Renamed 'file' to 'file_item' to avoid clash with 'file' type
            if file_item.endswith(extension):
                full_path = os.path.abspath(os.path.join(root, file_item))
                path_parts = full_path.split(os.sep)

                patient = "Unknown"
                sample = "Unknown"
                condition_val = "Unknown"
                
                condition_index = -1
                for i, part in enumerate(path_parts):
                    part_lower = part.lower()
                    if part_lower == "tumor":
                        condition_val = "Tumor"
                        condition_index = i
                        break 
                    elif part_lower == "normal":
                        condition_val = "Normal"
                        condition_index = i
                        break
                
                if condition_index != -1: # "tumor" or "normal" was found
                    # Patient extraction
                    if condition_index - 1 >= 0:
                        patient = path_parts[condition_index - 1]
                    # else: patient remains "Unknown"

                    # Sample extraction
                    # Check if there is a part after the condition_part
                    if condition_index + 1 < len(path_parts):
                        potential_sample_part_idx = condition_index + 1
                        # This is the part directly after "normal"/"tumor"
                        
                        # Check if this potential_sample_part is a directory.
                        # It's a directory if it's not the last part of the path (which is the filename).
                        filename_idx = len(path_parts) - 1
                        if potential_sample_part_idx < filename_idx:
                            sample = path_parts[potential_sample_part_idx]
                        else:
                            # The part after "normal"/"tumor" is the filename itself.
                            # So, there's no intermediate sample directory. Sample remains "Unknown".
                            pass # sample is already "Unknown"
                    # else: Path ends with "normal"/"tumor" or has no parts after it. Sample remains "Unknown".
                
                else: # "tumor" or "normal" NOT found, condition_val remains "Unknown"
                    # Fallback logic using path relative to the initial search directory
                    # os.path.normpath is used on 'directory' to handle potential trailing slashes an ensure clean relpath
                    relative_path = os.path.relpath(full_path, os.path.normpath(directory))
                    relative_path_parts = relative_path.split(os.sep)

                    # Expected structures relative to search directory:
                    # 1. patient_dir/file.ext (e.g., patient4_nodirs/patient4_file.bed)
                    #    Here, patient = patient_dir, sample = Unknown
                    # 2. patient_dir/sample_dir/file.ext (No intermediate dir like "other_condition")
                    #    Here, patient = patient_dir, sample = sample_dir
                    # 3. patient_dir/intermediate_dir/sample_dir/file.ext (e.g., patient3 path)
                    #    Here, patient = patient_dir, sample = sample_dir

                    if len(relative_path_parts) >= 2: # Minimum: patient_dir/file.ext
                        patient = relative_path_parts[0]
                        
                        if len(relative_path_parts) == 2: # Case 1: patient_dir/file.ext
                            sample = "Unknown"
                        elif len(relative_path_parts) >= 3: # Case 2 or 3: patient_dir/.../sample_dir/file.ext
                            # Sample is the directory containing the file, which is the second to last part.
                            sample = relative_path_parts[-2]
                        # else: sample remains "Unknown" if structure is odd (e.g. only 1 part, though >=2 handles this)
                    # else: path is too shallow (e.g. file directly in search_dir), patient/sample remain "Unknown"

                rows.append({
                    "patient": patient,
                    "sample": sample,
                    "condition": condition_val,
                    "path": full_path
                })

    with open(output_tsv_file, 'w', newline='') as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=header, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)

    print(f"Sample sheet created: {output_tsv_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a sample sheet TSV from a directory of files.")
    parser.add_argument("directory", type=str, help="Directory to search for files.")
    parser.add_argument("extension", type=str, help="File extension to search for (e.g., 'bed', '.txt').")
    parser.add_argument("output_file", type=str, help="Path to the output TSV file.")
    args = parser.parse_args()
    tum_norm_tsv(args.directory, args.extension, args.output_file)
