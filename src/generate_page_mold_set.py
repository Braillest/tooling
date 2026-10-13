import argparse
import sys
import os
import errno
import math
import time
from build123d import *

# Handle command line arguments
parser = argparse.ArgumentParser(description="Generate the mold set for a single paginated braille page.")
parser.add_argument("braille_file_path")
parser.add_argument("--crop", action="store_true", help="Trim the unused blank area below the last braille line from the positive mold and write a matching cropped negative mold.")
parser.add_argument("--crop-margin", type=float, default=10.0, help="Minimum distance in mm between the lowest dot and the cut. The cut snaps down to the castle zip grid. Default: 10")
args = parser.parse_args()

# Validate argument file exists.
if not os.path.isfile(args.braille_file_path):
    print("File does not exist: " + args.braille_file_path)
    sys.exit(1)

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

braille_file_path = str(args.braille_file_path)
page_number = os.path.basename(braille_file_path)
page_number = os.path.splitext(page_number)[0]
book_name = os.path.dirname(braille_file_path)
book_name = os.path.basename(book_name)
braille_molds_directory = "/data/6-braille-molds/" + book_name + "/"
os.makedirs(braille_molds_directory, exist_ok=True)
positive_mold_file_path = braille_molds_directory + page_number + "-positive.stl"
negative_mold_file_path = braille_molds_directory + page_number + "-negative.stl"
base_positive_mold_file_path = "/data/0-base-stls/Positive-Castle-Zip-Mold-v9.8.stl"
base_negative_mold_file_path = "/data/0-base-stls/Negative-Castle-Zip-Mold-v9.8.stl"

if not os.path.isfile(braille_file_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), braille_file_path)

for base_mold_file_path in [base_positive_mold_file_path, base_negative_mold_file_path]:
    if not os.path.isfile(base_mold_file_path):
        print("Base mold not found: " + base_mold_file_path)
        print("Run ./scripts/restore-base-stls.sh from the root of the repo to restore the v9.8 base molds from git history.")
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), base_mold_file_path)

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

# Determine crop line.
# The castle zip teeth (positive) and notches (negative) alternate every 10mm along the long edges,
# starting at the bottom edge of the mold. Cutting on that grid keeps the teeth and notches paired.
# Paper is aligned to the top of the mold, so only the bottom is trimmed.
crop_grid = 10
crop_y = None
if args.crop and dot_coords:
    lowest_dot_edge = min(y for _, y, _ in dot_coords) - dot_r
    crop_y = math.floor((lowest_dot_edge - args.crop_margin) / crop_grid) * crop_grid
    if crop_y <= 0:
        crop_y = None
    else:
        print(f"Cropping molds at y={crop_y}mm ({positive_mold_h - crop_y}mm of {positive_mold_h}mm kept)")

print("Generating dots")
dot_template = Sphere(dot_r, arc_size1=0)
dot_list = [loc * dot_template for loc in Locations(dot_coords)]
dot_object = Compound(children=dot_list)
print(time.time() - start)

print("Generating positive mold")
start = time.time()

with BuildPart() as positive_mold:

    print("Importing positive mold")
    start = time.time()
    importer = Mesher()
    imported_mesh = importer.read(base_positive_mold_file_path)
    with Locations((positive_mold_w/2, positive_mold_h/2, 0)):
        add(imported_mesh)
    print(time.time() - start)

    print("Adding dots")
    start = time.time()
    add(dot_object, mode=Mode.ADD)
    print(time.time() - start)

    if crop_y is not None:
        print("Cropping mold")
        with Locations((positive_mold_w/2, crop_y, -1)):
            Box(2 * positive_mold_w, 2 * positive_mold_h, 10, align=(Align.CENTER, Align.MIN, Align.MIN), mode=Mode.INTERSECT)

    print("Scaling mold")
    start = time.time()
    scaled_mold = positive_mold.part.scale(scaling_factor)
    print(time.time() - start)

    print("Exporting mold")
    start = time.time()
    export_stl(scaled_mold, positive_mold_file_path, tolerance=0.1, angular_tolerance=1)
    print(time.time() - start)

# The negative mold is universal unless cropped, in which case each page gets a matching cropped negative.
if crop_y is not None:

    print("Generating cropped negative mold")
    start = time.time()

    with BuildPart() as negative_mold:
        importer = Mesher()
        imported_mesh = importer.read(base_negative_mold_file_path)
        with Locations((negative_mold_w/2, negative_mold_h/2, 0)):
            add(imported_mesh)
        with Locations((negative_mold_w/2, crop_y, -1)):
            Box(2 * negative_mold_w, 2 * negative_mold_h, 10, align=(Align.CENTER, Align.MIN, Align.MIN), mode=Mode.INTERSECT)

    export_stl(negative_mold.part, negative_mold_file_path, tolerance=0.1, angular_tolerance=1)
    print(time.time() - start)
