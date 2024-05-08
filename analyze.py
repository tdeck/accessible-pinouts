# This script helps me analyze the whole library to look for patterns in data representation

from typing import Optional, Set
import os
from pprint import pprint

from kiutils.symbol import Symbol, SymbolLib
from tqdm import tqdm  # Cool progress bar thing, optional

KICAD_REPO = "/home/troy/Downloads/pinout/kicad-symbols"
EXTENSION = '.kicad_sym'
END_EARLY = False

def prop_value(symbol: Symbol, key: str):
    matches = [p for p in symbol.properties if p.key == key]

    if not matches:
        return None

    if len(matches) > 1:
        raise RuntimeError(f"Got >1 matches for key {key}")

    return matches[0].value

def get_footprints(accumulator: Optional[Set[str]], symbol: Symbol) -> Optional[Set[str]]:
    # Actually this is all listed here: https://kicad.github.io/footprints/Package_DIP
    if accumulator is None:
        accumulator = set()

    accumulator.add(prop_value(symbol, "Footprint"))

    return accumulator


def get_parts_with_named_pins(accumulator: Optional[Set[str]], symbol: Symbol) -> Optional[Set[str]]:
    if accumulator is None:
        accumulator = set()

    pin_unit = any((True for u in symbol.units if u.pins))

    if pin_unit:
        footprint = prop_value(symbol, "Footprint")

        accumulator.add(symbol.entryName + '::' + str(footprint))

    return accumulator


target_fn = get_parts_with_named_pins
acc = None

i = 1
for filename in tqdm(os.listdir(KICAD_REPO)):
    if not filename.endswith(EXTENSION):
        continue

    if END_EARLY and i > 5:
        break

    f = os.path.join(KICAD_REPO, filename)

    sym_lib = SymbolLib.from_file(f)

    for sym in sym_lib.symbols:
        acc = target_fn(acc, sym)

    i += 1

pprint(acc)
