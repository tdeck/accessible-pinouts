This is an unpolished set of scripts that can read a folder full of KiCAD symbols and generate pin listings using a Jinja template.

The actual business logic happens in generate.py. To run it, you must update the OUTDIR variable in generate.py and the repo paths in repos.py.

`process_part_instance()` will be called once for each combination of part pins + footprint name. The footprint name may come from the `Footprint` property of the part in the KiCAD library, or it may be split from the `ki_fp_filters` property. These two have different formats.

Only parts with a known footprint (in packages.py) get a generated output. The footprint type is used to look up the description of the package's pin ordering and how to identify pin 1, which is passed to the template.

Parts that don't match expectations for some reason will be rejected. For example, DIP parts with an uneven number of pins, or parts with more pins than expected for TO-92 or TO-220 parts. Parts with no footprint will also be rejected.
