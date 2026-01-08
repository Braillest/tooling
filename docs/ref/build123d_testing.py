from build123d import *
from time import time

# Create box.
length, width, thickness = 100, 100, 10
# box = Box(length, width, thickness, align=(Align.MIN, Align.MIN, Align.MIN))
box = Box(length, width, thickness)
box.position = (length / 2, width / 2, thickness / 2)

# Create a sphere.
radius = 0.75
sample_sphere = Sphere(radius, arc_size1=0, align=(Align.CENTER, Align.CENTER, Align.MIN))

# Create a list of positions where the sphere is placed such that the center of the sphere intersects the top Z axis of the box and is placed every 10 x any y units.
start_time = time()
x_offset = 5
y_offset = 5
sphere_instances = [sample_sphere.located(Location((x + x_offset, y + y_offset, thickness + 1))) for x in range(0, length, 10) for y in range(0, width, 10)]
end_time = time()
print(f"Time taken to create list of sphere instances:\n{end_time - start_time} seconds\n")

# Benchmark the creation of the spheres.
start_time = time()
spheres = Compound(sphere_instances)
end_time = time()
print(f"Time taken to create compound of spheres:\n{end_time - start_time} seconds\n")

# Combine the box and the spheres.
start_time = time()
final_object = box + spheres
end_time = time()
print(f"Time taken to combine box and spheres:\n{end_time - start_time} seconds\n")

# Export the final object.
start_time = time()
export_stl(sample_sphere, "final_object.stl", tolerance=0.1, angular_tolerance=1)
end_time = time()
print(f"Time taken to export final object:\n{end_time - start_time} seconds\n")
