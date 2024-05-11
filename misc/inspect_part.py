# Run with python -i to play with the symbol
import os
from pprint import pprint
import sys

from kiutils.symbol import Symbol, SymbolLib
from tqdm import tqdm

KICAD_REPO = "/home/troy/Downloads/pinout/kicad-symbols"
EXTENSION = '.kicad_sym'

def find_symbol(sym_lib, part):
    for s in sym_lib.symbols:
        if s.entryName == part:
            return s

    return None


def search_all_files(part):
    for filename in tqdm(os.listdir(KICAD_REPO)):
        if not filename.endswith(EXTENSION):
            continue

        f = os.path.join(KICAD_REPO, filename)

        sym_lib = SymbolLib.from_file(f)
        s = find_symbol(sym_lib, part)

        if s:
            return sym_lib, s

    return None, None

# Utility functions

def prop(symbol, key):
    matches = [p for p in symbol.properties if p.key == key]

    if not matches:
        return None

    if len(matches) > 1:
        raise RuntimeError(f"Got >1 matches for key {key}")

    return matches[0].value


def all_pins(symbol):
    return [p for u in symbol.units for p in u.pins]


def ppins(symbol):
    return [
        (p.number, p.name)
        for p in all_pins(symbol)
    ]


def footprint(symbol):
    return prop(symbol, 'Footprint')

# Main code

slib, sym = search_all_files(sys.argv[1])
pprint(sym)

