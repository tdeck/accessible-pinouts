import sys
from typing import List, Optional
import pprint
import os
import datetime
import re

import jinja2
from markupsafe import Markup, escape
from kiutils.symbol import Symbol, SymbolLib
from tqdm import tqdm  # Cool progress bar thing, optional

from packages import *

KICAD_REPO = "/home/troy/Downloads/pinout/kicad-symbols"
SYM_EXTENSION = '.kicad_sym'
OUTDIR = '/home/troy/projects/static/blindmakers/content/pinouts'

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))


@jinja2.pass_eval_context
def nl2br(eval_ctx, value):
    return value.replace("\n", "<br>\n")

jinja_env.filters["nl2br"] = nl2br

template = jinja_env.get_template("template.html.jinja2")
template.globals['now'] = datetime.datetime.now()

def prop_value(symbol: Symbol, key: str):
    matches = [p for p in symbol.properties if p.key == key]

    if not matches:
        return None

    if len(matches) > 1:
        raise RuntimeError(f"Got >1 matches for key {key}")

    return matches[0].value


def process_symbol(symbol: Symbol) -> None:
    pin_units = [u for u in symbol.units if u.pins]
    if len(pin_units) != 1:
        return  # Need exactly one unit with pins; some have >1 IDK why yet

    footprint = prop_value(symbol, 'Footprint')
    if footprint is None or footprint not in PACKAGE_REGISTRY:
        return


    pins = [
        Pin(
            name=p.name,
            number=int(p.number),
        )
        for p in pin_units[0].pins
    ]

    pins.sort(key=lambda p: p.number)
    
    pkg = PACKAGE_REGISTRY[footprint]

    part_id = symbol.entryName

    try:
        part = Part(
            part_id=part_id,
            name=symbol.entryName, # TODO check for a better one
            desc=prop_value(symbol, 'Description'),
            pkg_desc=pkg.desc(),
            pin_groups=pkg.group_pins(pins),
        )

        with open(f"{OUTDIR}/{part_id}.html", 'w') as fh:
            fh.write(template.render(part=part))
    except AssertionError as e:
        print(f"Part {symbol.entryName} is weird!")


# Prepare the list of files to process

files = []
if len(sys.argv) > 1:
    files.append(f"{KICAD_REPO}/{sys.argv[1]}{SYM_EXTENSION}")
else:
    for filename in os.listdir(KICAD_REPO):
        if not filename.endswith(SYM_EXTENSION):
            continue

        files.append(os.path.join(KICAD_REPO, filename))

# Generate pinouts for all eligible parts in the catalog


for file in files:
    sym_lib = SymbolLib.from_file(file)

    for sym in sym_lib.symbols:
        process_symbol(sym)

