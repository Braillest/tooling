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
paper_h = 280 / 2
paper_d = 0.2
paper_tolerance = 0.25

# Found standards, but low resolution. Reverse image searched using:
# - https://scripor.com/wp-content/uploads/2022/07/insert-ziar-a4-preview-724x1024.jpg
# Larger resultion found here:
# - https://editiadedimineata.ro/wp-content/uploads/2019/05/insert-ziar-a4-preview.jpg
cell_w = 11.1
cell_h = 11
cell_spacing_x = 2.3
cell_spacing_y = 2.5
cell_padding_x = (cell_w - (cell_spacing_x * 2)) / 2
cell_padding_y = (cell_h - (cell_spacing_y * 3)) / 2

pin_d = 1.2
slot_w = 5

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

left_cell_padding_count = 1
right_cell_padding_count = 1
top_cell_padding_count = 1
bottom_cell_padding_count = 1

max_cell_x_count = math.floor(paper_w / cell_w)
cell_x_count = max_cell_x_count - left_cell_padding_count - right_cell_padding_count

max_cell_y_count = math.floor(paper_h / cell_h)
cell_y_count = max_cell_y_count - top_cell_padding_count - bottom_cell_padding_count

print(cell_x_count, cell_y_count)

braille_molds_directory = "/data/braille-molds/scripor/"
os.makedirs(braille_molds_directory, exist_ok=True)
positive_mold_file_path = braille_molds_directory + "positive.stl"
negative_mold_file_path = braille_molds_directory + "negative.stl"
base_positive_mold_file_path = "/data/base-stls/Positive-Castle-Zip-Half-Mold-v9.8.stl"
base_negative_mold_file_path = "/data/base-stls/Negative-Castle-Zip-Half-Mold-v9.8.stl"

if not os.path.isfile(base_positive_mold_file_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), base_positive_mold_file_path)

if not os.path.isfile(base_negative_mold_file_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), base_negative_mold_file_path)

print("Generating feature coordinates")
start = time.time()

# Generate dot and hole locations
dot_coords = []
hole_coords = []

red = ((1,0), (0,1), (2,1), (0,3), (2,3))
orange = ((1,0), (1,1), (0,2), (2,2), (1,3))
yellow = ((1,0), (1,1), (2,1), (1,2), (2,2), (1,3), (2,3))
green = ((1,0), (1,1), (1,2), (0,3), (1,3), (2,3))
blue = ((1,0), (1,1), (2,1), (1,2), (2,2))
purple = ((1,0), (1,1), (0,2), (1,2), (2,2))
brown = ((1,0), (1,1), (0,2), (1,2), (2,2), (0,3), (1,3), (2,3))
grey = ((1,0), (0,1), (2,1), (1,2), (0,3), (2,3))
white = ((1,0), (1,1), (1,2), (1,3))
black = ((1,0), (0,1), (2,1), (0,2), (2,2), (0,3), (2,3))

for line_index in range(cell_y_count):
    x_offset = slot_w + paper_tolerance + (left_cell_padding_count * cell_w) + cell_padding_x
    y_offset = (cell_y_count - line_index) * cell_h + (top_cell_padding_count * cell_h) + cell_padding_y

    # red
    for dx, dy in red:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    # orange
    for dx, dy in orange:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    # yellow
    for dx, dy in yellow:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    # green
    for dx, dy in green:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    # blue
    for dx, dy in blue:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    # purple
    for dx, dy in purple:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    # brown
    for dx, dy in brown:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    # grey
    for dx, dy in grey:
        dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
        hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
    x_offset += cell_w

    for i in range(5):
        # black
        for dx, dy in black:
            dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
            hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
        x_offset += cell_w

    for i in range(5):
        # white
        for dx, dy in white:
            dot_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, positive_mold_backplate_d + (dot_d / 2)))
            hole_coords.append((x_offset + dx * cell_spacing_x, y_offset - dy * cell_spacing_y, 0))
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

    # Rotate about Y axis by 180 degrees
    negative_mold.part = negative_mold.part.rotate(Axis.Y, 180)

    # Account for mold shrinkage for dimensional accuracy
    scaled_mold = scale(negative_mold.part, scaling_factor)
    export_stl(scaled_mold, negative_mold_file_path, tolerance = 0.1, angular_tolerance = 1)

print(time.time() - start)
