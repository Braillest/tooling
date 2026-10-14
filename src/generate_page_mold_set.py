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
parser.add_argument("--neghole", action="store_true", help="Give the negative mold a through hole at every possible dot position (32x26 cells, 6 dots each) so one negative works with any positive page.")
parser.add_argument("--paper-thickness", type=float, default=0.33, help="Thickness in mm of the paper or card being embossed, used to size --neghole pockets. Default: 0.33 (110 lb index cardstock). Braille paper is about 0.25.")
parser.add_argument("--neghole-tolerance", type=float, default=0.25, help="Extra pocket diameter in mm for printer tolerance and plate misalignment. Default: 0.25")
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

# The negative mold is universal unless cropped or holed, in which case each page gets its own negative.
if crop_y is not None or args.neghole:

    print("Generating negative mold")
    start = time.time()

    # Universal holes: one through hole per possible dot position in the full cell grid, on the same grid as the dots.
    # Only whole cells above the crop line are included, so no hole is cut by the crop.
    # Each hole is a spherical pocket that clears the dot wrapped in paper (dot radius + paper thickness + tolerance),
    # centered on the dot's center, plus a dot sized throat through the top of the plate.
    # The negative rests on the paper, or on the rails if the paper is thinner than the rail step.
    universal_hole_coords = []
    if args.neghole:
        neghole_r = dot_r + args.paper_thickness + args.neghole_tolerance / 2
        throat_r = dot_r
        negative_bottom_z = positive_mold_backplate_d + max(args.paper_thickness, paper_d)
        # The dot is a hemisphere whose flat base is the bottom of its bounding box; its sphere center sits there.
        dot_sphere_center_z = positive_mold_backplate_d + (dot_d / 2) + dot_template.bounding_box().min.Z
        pocket_center_z = dot_sphere_center_z - negative_bottom_z
        # The pocket's widest point is usually below the plate, so check the opening at the paper face.
        face_r = math.sqrt(max(neghole_r ** 2 - pocket_center_z ** 2, 0)) if pocket_center_z < 0 else neghole_r
        if 2 * face_r > cell_spacing - 0.15:
            print(f"Warning: pocket opening {2 * face_r:.2f}mm leaves less than 0.15mm between pockets at {cell_spacing}mm dot spacing; neighboring pockets in a cell will merge at the paper face.")
        for row in range(cell_y_count):
            y_offset = (cell_y_count - row) * cell_h + cell_padding_y
            if crop_y is not None and y_offset - neghole_r < crop_y:
                continue
            for column in range(cell_x_count):
                x_offset = slot_w + paper_tolerance + (3 * cell_w) + cell_padding_x + column * cell_w
                for dx, dy in [(0, 2), (0, 1), (0, 0), (1, 2), (1, 1), (1, 0)]:
                    universal_hole_coords.append((x_offset + dx * cell_spacing, y_offset + dy * cell_spacing))
        print(f"Negative holes: {len(universal_hole_coords)} (pocket sphere diameter {2 * neghole_r:.2f}mm, opening at paper face {2 * face_r:.2f}mm, throat diameter {2 * throat_r:.2f}mm)")

    with BuildPart() as negative_mold:
        importer = Mesher()
        imported_mesh = importer.read(base_negative_mold_file_path)
        with Locations((negative_mold_w/2, negative_mold_h/2, 0)):
            add(imported_mesh)
        if crop_y is not None:
            with Locations((negative_mold_w/2, crop_y, -1)):
                Box(2 * negative_mold_w, 2 * negative_mold_h, 10, align=(Align.CENTER, Align.MIN, Align.MIN), mode=Mode.INTERSECT)
        if universal_hole_coords:
            pocket_template = Sphere(neghole_r, mode=Mode.PRIVATE)
            throat_template = Cylinder(throat_r, negative_mold_d + 2, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.PRIVATE)
            pockets = [loc * pocket_template for loc in Locations([(x, y, pocket_center_z) for x, y in universal_hole_coords])]
            throats = [loc * throat_template for loc in Locations([(x, y, -1) for x, y in universal_hole_coords])]
            add(Compound(children=pockets + throats), mode=Mode.SUBTRACT)

    negative_part = negative_mold.part
    if args.neghole:
        # Scale like the positive so every hole sits exactly over its dot position in the scaled positive.
        negative_part = negative_part.scale(scaling_factor)

    # Pockets need a finer mesh than the dots: a 0.1mm chord error would eat most of the clearance.
    export_stl(negative_part, negative_mold_file_path, tolerance=0.02 if args.neghole else 0.1, angular_tolerance=0.5 if args.neghole else 1)
    print(time.time() - start)
