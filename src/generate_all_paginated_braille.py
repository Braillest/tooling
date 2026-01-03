import asyncio
import os
import sys

# experimental script

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

    text_directory = "/data/texts/"
    text_file_paths = [os.path.join(text_directory, f) for f in os.listdir(text_directory) if os.path.isfile(os.path.join(text_directory, f))]

    max_concurrent_tasks = 5
    semaphore = asyncio.Semaphore(max_concurrent_tasks)

    tasks = [run_script("/braillest/generate_paginated_braille.py", text_file_path, semaphore) for text_file_path in text_file_paths]
    results = await asyncio.gather(*tasks)

# Run the main function
asyncio.run(main())
