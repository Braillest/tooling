# A Note on Angular Tolerance

Increasing angular_tolerance slightly reduces the triangle count, file size, and export time, but at the cost of quality.

Experiments show that angular_tolerance = 1 is a good balance between quality and performance.
An angular_tolerance of 1.5 does not yield a spherical gcode.
