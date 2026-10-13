import argparse
import asyncio
import os
import sys

# Handle command line arguments
parser = argparse.ArgumentParser(description="Translate, paginate, and generate page molds for a text file.")
parser.add_argument("text_file_path")
parser.add_argument("--crop", action="store_true", help="Trim unused blank area below the last braille line of each page (positive + matching negative).")
parser.add_argument("--neghole", action="store_true", help="Give each negative mold a through hole at every possible dot position.")
parser.add_argument("--paper-thickness", type=float, default=0.33, help="Paper or card thickness in mm used to size --neghole pockets. Default: 0.33")
parser.add_argument("--neghole-tolerance", type=float, default=0.25, help="Extra pocket diameter in mm for --neghole. Default: 0.25")
parser.add_argument("--crop-margin", type=float, default=10.0, help="Minimum distance in mm between the lowest dot and the cut. Default: 10")
args = parser.parse_args()

mold_args = []
if args.crop:
    mold_args += ["--crop", "--crop-margin", str(args.crop_margin)]
if args.neghole:
    mold_args += ["--neghole", "--paper-thickness", str(args.paper_thickness), "--neghole-tolerance", str(args.neghole_tolerance)]

async def run_script(script_name, file_path, semaphore, extra_args=[]):

    async with semaphore:

        process = await asyncio.create_subprocess_exec(
            "python", script_name, file_path, *extra_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[{file_path} STDOUT]: {stdout.decode()}")
        if stderr:
            print(f"[{file_path} STDERR]: {stderr.decode()}")

        return process.returncode

async def main():

    text_file_path = str(args.text_file_path)
    text_filename = os.path.basename(text_file_path)
    text_filename = os.path.splitext(text_filename)[0]
    paginated_braille_directory = "/data/5-paginated-braille/" + text_filename + "/"

    # Check if text_file_path exists.
    if not os.path.exists(text_file_path):
        print("Text file does not exist")
        print("Expected path: " + text_file_path)
        print("Current directory: " + os.getcwd())
        print("Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book")
        sys.exit(1)

    max_concurrent_tasks = os.cpu_count()
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    print("Generating paginated braille...")
    tasks = [run_script("/braillest/generate_paginated_braille.py", text_file_path, semaphore)]
    result = await asyncio.gather(*tasks)

    # Check if paginated_braille_directory was created/exists.
    if not os.path.exists(paginated_braille_directory):
        print("Paginated braille directory does not exist")
        print("Expected path: " + paginated_braille_directory)
        print("Current directory: " + os.getcwd())
        print("Please run this script at the root of the braillest/tooling repo after generating all files for creating molds for a book")
        sys.exit(1)

    print("Generating page molds...")
    paginated_braille_file_paths = [os.path.join(paginated_braille_directory, f) for f in os.listdir(paginated_braille_directory) if os.path.isfile(os.path.join(paginated_braille_directory, f))]
    tasks = [run_script("/braillest/generate_page_mold_set.py", paginated_braille_file, semaphore, mold_args) for paginated_braille_file in paginated_braille_file_paths]
    results = await asyncio.gather(*tasks)

# Run the main function
asyncio.run(main())
