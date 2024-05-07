import sys
from typing import List, Optional
import pprint

from kiutils.symbol import Symbol, SymbolLib

from packages import *

KICAD_REPO = "/home/troy/Downloads/pinout/kicad-symbols"

partname = sys.argv[1]

file = f"{KICAD_REPO}/{partname}.kicad_sym"

sym_lib = SymbolLib.from_file(file)

if len(sys.argv) == 2:
    for s in sym_lib.symbols:
        print(s.entryName)

    exit(0)

part_name = sys.argv[2]
part_sym = next((s for s in sym_lib.symbols if s.entryName == part_name))


def prop_value(symbol: Symbol, key: str):
    matches = [p for p in symbol.properties if p.key == key]

    if not matches:
        return None

    if len(matches) > 1:
        raise RuntimeError(f"Got >1 matches for key {key}")

    return matches[0].value


def get_groups(part_sym) -> List[PinGroup]: # TODO typing
    pin_units = [u for u in part_sym.units if u.pins]
    if len(pin_units) != 1:
        raise RuntimeError(f"pin_units has length {len(pin_units)}")

    pprint.pprint(pin_units[0].pins)

    footprint = prop_value(part_sym, 'Footprint')

    pins = [
        Pin(
            name=p.name,
            number=int(p.number),
        )
        for p in pin_units[0].pins
    ]

    pins.sort(key=lambda p: p.number)

    return PACKAGE_REGISTRY[footprint].group_pins(pins)


pprint.pprint(get_groups(part_sym))

#.properties[key=ki_fp_filters].value='DIP*W7.62mm*'
#.properties[key=Footprint].value='Package_DIP:DIP-20_W7.62mm'
#.units[].pins (multiple units, only one has pins I think)

# LibTable
