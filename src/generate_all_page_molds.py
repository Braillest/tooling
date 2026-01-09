import asyncio
import os
import sys

# Handle command line arguments
if len(sys.argv) != 2:
    print("Usage: python generate_all_page_molds.py <text_file_path>")
    sys.exit(1)

async def run_script(script_name, file_path, semaphore):

    async with semaphore:

        process = await asyncio.create_subprocess_exec(
            "python", script_name, file_path,
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

    text_file_path = str(sys.argv[-1])
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
    tasks = [run_script("/braillest/generate_page_mold_set.py", paginated_braille_file, semaphore) for paginated_braille_file in paginated_braille_file_paths]
    results = await asyncio.gather(*tasks)

# Run the main function
asyncio.run(main())
