import os
import zipfile
import sys

# Validate that two arguments are provided.
if len(sys.argv) != 3:
    print("Usage: python zip_molds.py <input_dir> <output_dir>")
    sys.exit(1)

# Extract input and output directories from command line arguments.
INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]
BATCH_SIZE = 250

# Validate that input directory exists.
if not os.path.exists(INPUT_DIR):
    print(f"Input directory {INPUT_DIR} does not exist.")
    sys.exit(1)

# Validate that output directory exists.
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Get list of files in input directory.
files = [f for f in os.listdir(INPUT_DIR) if os.path.isfile(os.path.join(INPUT_DIR, f))]

# Create zip files.
for i in range(0, len(files), BATCH_SIZE):
    zip_name = os.path.join(OUTPUT_DIR, f"archive_{i // BATCH_SIZE + 1}.zip")
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in files[i:i + BATCH_SIZE]:
            zipf.write(os.path.join(INPUT_DIR, file), arcname=file)

# Print success message.
print(f"Successfully created {len(files) // BATCH_SIZE + 1} zip files.")
