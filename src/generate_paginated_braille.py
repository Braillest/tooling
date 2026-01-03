import louis
import os
import re
import sys
import time

# Handle command line arguments
if len(sys.argv) != 2:
    print("Usage: python generate_paginated_braille.py <text_file_path>")
    sys.exit(1)

# Control variables
character_x_count = 32
character_y_count = 26
space_character = "\u2800"
text_file_path = str(sys.argv[-1])
braille_directory = "/data/braille/"
formatted_braille_directory = "/data/formatted-braille/"
paginated_braille_directory = "/data/paginated-braille/"
back_translation_directory = "/data/back-translations/"
remove_trailing_whitespace = True
translation_table = ["braille-patterns.cti", "en-ueb-g2.ctb"]

# Validate provided file
if not os.path.exists(text_file_path) or not os.path.isfile(text_file_path):
    print(f"{text_file_path} was not found")
    pass

# Create directory for paginated braille files
filename = os.path.basename(text_file_path)
filename = os.path.splitext(filename)[0]
paginated_braille_directory += filename + "/"
os.makedirs(paginated_braille_directory, exist_ok=True)

# Update remainder paths
braille_path = braille_directory + filename + ".txt"
back_translation_path = back_translation_directory + filename + ".txt"
formatted_braille_path = formatted_braille_directory + filename + ".txt"

# Translate text to braille
print("Translating text to braille")
start_time = time.time()

with open(text_file_path, "r") as text_file:
    text_lines = text_file.readlines()
    with open(braille_path, "w") as braille_file:
        for line in text_lines:
            if remove_trailing_whitespace:
                line = line.rstrip()
            braille_file.write(louis.translateString(translation_table, line) + "\n")

# Backtranslate braille to text
print(time.time() - start_time)
print("Backtranslating braille to text")
start_time = time.time()

braille_lines = None
with open(braille_path, "r") as braille_file:
    braille_lines = braille_file.readlines()
    with open(back_translation_path, "w") as back_translation_file:
        for line in braille_lines:
            if remove_trailing_whitespace:
                line = line.rstrip()
            back_translation_file.write(louis.backTranslateString(translation_table, line) + "\n")

# Format braille
print(time.time() - start_time)
print("Formatting braille")
start_time = time.time()

pattern = r"([^\n]+(?:\n[^\n]+)*)"
text = "".join(braille_lines)
matches = re.finditer(pattern, text)
offset = 0

for match in matches:

    # Convert list of text to string
    match_text = match.group(0).replace("\n", space_character)
    match_words = match_text.split(space_character)
    current_line = ""
    wrapped_lines = []

    # Iterate through each word
    for word in match_words:

        word_len = len(word)

        # Incoming word can fit case
        if len(current_line) + word_len + 1 <= character_x_count:

            # If it's not the first word, prepend a space
            if current_line:
                current_line += space_character

            current_line += word

        # Incoming word cannot fit case
        else:

            # Special conditional for braille line break
            if word_len < character_x_count:
                wrapped_lines.append(current_line)

            current_line = word

    # Add the last line if exists
    if current_line:
        wrapped_lines.append(current_line)

    wrapped_text = "\n".join(wrapped_lines)
    start = match.start() + offset
    end = match.end() + offset
    text = text[:start] + wrapped_text + text[end:]
    delta = len(wrapped_text) - len(match_text)
    offset += delta

local_braille_lines = text.split("\n")
with open(formatted_braille_path, "w") as formatted_braille_file:
    for line in local_braille_lines:
        formatted_braille_file.write(line + "\n")

# Paginate braille
print(time.time() - start_time)
print("Paginating braille")
start_time = time.time()

pages = []
current_page = []
current_page_size = 0

# TODO:
# Alter pagination to prevent dividing table of contents lines from their page number / page breaking within a line

with open(formatted_braille_path, "r") as formatted_braille_file:
    formatted_braille_lines = formatted_braille_file.readlines()
    for line_index, line in enumerate(formatted_braille_lines):

        if line.strip() != '' or current_page:
            current_page_size += 1
            current_page.append(line)

        if len(current_page) >= character_y_count:

            # Chunk text
            pattern = r"([^\n]+(?:\n[^\n]+)*)"
            text = "".join(current_page)
            matches = list(re.finditer(pattern, text))
            last_match_text = matches[-1].group(0).replace("\n", space_character)
            line_break_string = "⠿" * character_x_count

            # Handle case that line break occurs at end of page.
            if line_break_string in last_match_text:

                # Remove line_break_string from current page,
                # Add current page to output
                # Start new page with line_break_string
                current_page = current_page[:current_page_size - 1]
                pages.append(current_page)
                current_page = [line]
                current_page_size = 1
                continue

            # Add page, reset current page
            pages.append(current_page)
            current_page = []
            current_page_size = 0

if current_page:
    pages.append(current_page)

# Write pages to dir
for index, page in enumerate(pages):
    with open(f"{paginated_braille_directory}{(index + 1):04d}.txt", "w") as out_file:
        for line in page:
            out_file.write(line)

print(time.time() - start_time)
