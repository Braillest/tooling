# A Note on Degenerate Facets 

When using the sphere or revolve functions, degenerate facets will be generated.
It is a known issue when converting parametric models using complicated geometry to STL files.

This issue will not be fixed in the near term.

Prusa slicer, the current slicer used by Braillest, handles these facets gracefully and automatically repairs the model upon importing/loading the model.
