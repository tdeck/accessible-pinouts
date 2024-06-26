# This script helps me analyze the whole library to look for patterns in data representation

from typing import Optional, Set, List, Dict
import os
from pprint import pprint
from collections import Counter

from kiutils.symbol import Symbol, SymbolLib
from tqdm import tqdm  # Cool progress bar thing, optional

KICAD_REPO = '/home/troy/Downloads/pinout/kicad-symbols'
SYM_EXTENSION = '.kicad_sym'
END_EARLY = False

def prop_value(symbol: Symbol, key: str):
    matches = [p for p in symbol.properties if p.key == key]

    if not matches:
        return None

    if len(matches) > 1:
        raise RuntimeError(f"Got >1 matches for key {key}")

    return matches[0].value

def prop_dict(symbol: Symbol)-> Dict[str, str]:
    return {
        p.key: p.value for p in symbol.properties
    }

def get_footprints(accumulator: Optional[Counter], symbol: Symbol, **kwargs) -> Optional[Set[str]]:
    # Actually this is all listed here: https://kicad.github.io/footprints/Package_DIP
    if accumulator is None:
        accumulator = Counter()

    accumulator[prop_value(symbol, "Footprint")] += 1

    return accumulator


def get_parts_with_named_pins(accumulator: Optional[Set[str]], symbol: Symbol, **kwargs) -> Optional[Set[str]]:
    if accumulator is None:
        accumulator = set()

    pin_unit = any((True for u in symbol.units if u.pins))

    if pin_unit:
        footprint = prop_value(symbol, "Footprint")

        accumulator.add(symbol.entryName + '::' + str(footprint))

    return accumulator


def get_parts_with_multiple_pin_units(accumulator: Optional[Set[str]], symbol: Symbol, **kwargs) -> Optional[Set[str]]:
    if accumulator is None:
        accumulator = set()

    pin_units = [u for u in symbol.units if u.pins]

    if len(pin_units) > 1:
        accumulator.add(symbol.entryName + f" has {len(pin_units)} pin units")

    return accumulator


def derived_symbol_analysis(accumulator: Optional[List[Dict]], symbol: Symbol, lib: SymbolLib, **kwargs) -> Optional[List[Dict]]:
    if accumulator is None:
        accumulator = []

    if symbol.extends:
        accumulator.append(dict(
            part=symbol.entryName,
            extends=symbol.extends,
            props=prop_dict(symbol),
        ))


    return accumulator


def footprint_vs_fp_filters(accumulator: Optional[List[Dict]], symbol: Symbol, **kwargs) -> Optional[List[Dict]]:
    if accumulator is None:
        accumulator = []

    accumulator.append(dict(
        Footprint=prop_value(sym, 'Footprint'),
        ki_fp_filters=prop_value(sym, 'ki_fp_filters'),
    ))


    return accumulator

target_fn = footprint_vs_fp_filters
acc = None

i = 1
for filename in tqdm(os.listdir(KICAD_REPO)):
    if not filename.endswith(SYM_EXTENSION):
        continue

    if END_EARLY and i > 5:
        break

    f = os.path.join(KICAD_REPO, filename)

    sym_lib = SymbolLib.from_file(f)

    for sym in sym_lib.symbols:
        acc = target_fn(accumulator=acc, symbol=sym, lib=sym_lib)

    i += 1

pprint(acc)
