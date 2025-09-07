import sys
import os
import errno
import math
import time
from build123d import *

# Control globals
scaling_factor = 1.005
space_character = "\u2800"

paper_w = 216
paper_h = 280
paper_d = 0.2
paper_tolerance = 0.25

cell_w = 6
cell_h = 10
cell_padding_x = 1.75
cell_padding_y = 2.5
cell_spacing = 2.5

pin_w = 4.5
pin_h = 9.8
pin_d = 1.2

slot_w = 5
slot_h = 10
slot_d = pin_d

dot_r = 0.75
dot_d = 0.5 + paper_d

hole_r = 0.95
hole_d = dot_d + paper_d

negative_mold_w = slot_w + paper_tolerance + paper_w + paper_tolerance + slot_w
negative_mold_h = paper_h
negative_mold_d = pin_d

positive_mold_w = slot_w + paper_tolerance + paper_w + paper_tolerance + slot_w
positive_mold_h = paper_h
positive_mold_backplate_d = 1.0
positive_mold_rail_d = positive_mold_backplate_d + paper_d
positive_mold_d = positive_mold_rail_d + negative_mold_d

left_cell_padding_count = 3
right_cell_padding_count = 1
top_cell_padding_count = 1
bottom_cell_padding_count = 1

max_cell_x_count = math.floor(paper_w / cell_w)
cell_x_count = max_cell_x_count - left_cell_padding_count - right_cell_padding_count

max_cell_y_count = math.floor(paper_h / cell_h)
cell_y_count = max_cell_y_count - top_cell_padding_count - bottom_cell_padding_count

print(cell_x_count, cell_y_count)

braille_file_path = str(sys.argv[-1])
page_number = os.path.basename(braille_file_path)
page_number = os.path.splitext(page_number)[0]
book_name = os.path.dirname(braille_file_path)
book_name = os.path.basename(book_name)
braille_molds_directory = "/data/braille-molds/" + book_name + "/"
os.makedirs(braille_molds_directory, exist_ok=True)
positive_mold_file_path = braille_molds_directory + page_number + "-positive.stl"
negative_mold_file_path = braille_molds_directory + page_number + "-negative.stl"
base_positive_mold_file_path = "/data/base-stls/Positive-Castle-Zip-Mold-v9.8.stl"
base_negative_mold_file_path = "/data/base-stls/Negative-Castle-Zip-Mold-v9.8.stl"

if not os.path.isfile(braille_file_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), braille_file_path)

print("Reading in file")
start = time.time()

with open(braille_file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

print(time.time() - start)
print("Generating feature coordinates")
start = time.time()

# Generate dot and hole locations
dot_coords = []
hole_coords = []
for line_index, line in enumerate(lines[0:cell_y_count]):
    x_offset = slot_w + paper_tolerance + (3 * cell_w) + cell_padding_x
    y_offset = (cell_y_count - line_index) * cell_h + cell_padding_y
    text = line.rstrip()

    for character in text:
        delta = ord(character) - ord(space_character)
        binary = f"{delta:06b}"[::-1]
        for i, (dx, dy) in enumerate([(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)]):
            if binary[i] == "1":
                dot_coords.append((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, positive_mold_backplate_d + (dot_d / 2)))
                hole_coords.append((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing, 0))
        x_offset += cell_w

print(time.time() - start)
print("Generating positive mold")
start = time.time()

with BuildPart() as positive_mold:

    importer = Mesher()
    imported_mesh = importer.read(base_positive_mold_file_path)

    # Add to BuildPart
    with Locations((positive_mold_w/2, positive_mold_h/2, 0)):
        add(imported_mesh)

    # Add dots
    with Locations(dot_coords):
        Sphere(dot_r, arc_size1=0, mode=Mode.ADD)

    # Account for mold shrinkage for dimensional accuracy
    scaled_mold = scale(positive_mold.part, scaling_factor)
    export_stl(scaled_mold, positive_mold_file_path, tolerance = 0.1, angular_tolerance = 1)

print(time.time() - start)
print("Generating negative mold")
start = time.time()

with BuildPart() as negative_mold:

    # imported_mesh = import_stl(base_negative_mold_file_path)
    importer = Mesher()
    imported_mesh = importer.read(base_negative_mold_file_path)

    # Rotate about Y axis by 180 degrees
    target_location = Location(
        (negative_mold_w/2, negative_mold_h/2, negative_mold_d),
        (0, 180, 0)
    )

    # Add to BuildPart
    with Locations(target_location):
        add(imported_mesh)

    # Subtract holes
    with Locations(hole_coords):
        Hole(hole_r, hole_d, mode=Mode.SUBTRACT)

    # Account for mold shrinkage for dimensional accuracy
    scaled_mold = scale(negative_mold.part, scaling_factor)
    export_stl(scaled_mold, negative_mold_file_path, tolerance = 0.1, angular_tolerance = 1)

print(time.time() - start)
