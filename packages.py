from dataclasses import dataclass
from typing import Dict, List, Optional
from textwrap import dedent
import itertools

@dataclass
class Pin:
    number: int
    name: str

@dataclass
class PinGroup:
    name: Optional[str]
    pins: List[Pin]

@dataclass
class Part:
    part_id: str
    name: str
    desc: Optional[str]
    pkg_desc: str
    pin_groups: List[PinGroup]

    # Source repo information
    source_name: str
    source_url: str
    source_revision: str

class Package:
    def __init__(self, slug, desc, group_names: List[str]=[], max_pins: Optional[int]=None):
        self.slug = slug
        self._desc = dedent(desc).strip()
        self._group_names = group_names
        self._max_pins = max_pins
            

    def desc(self) -> str:
        return self._desc

    def group_pins(self, pins: List[Pin]):
        """ Default behavior is to divide pins evenly into groups in given order. This is suitable for rectangular packages. """
        # Ensure no duplicate pin numbers
        assert len(set((p.number for p in pins))) == len(pins) 


        if self._max_pins:
            assert len(pins) <= self._max_pins

        if not self._group_names:
            return [PinGroup(name=None, pins=pins)]

        assert len(pins) % len(self._group_names) == 0

        group_size = len(pins) // len(self._group_names)

        i = 0
        res = []
        for group_name in self._group_names:
            res.append(PinGroup(name=group_name, pins=pins[i:i+group_size]))

            i += group_size

        return res


DIPPackage = Package(
    slug="DIP",
    desc="""
    This package has two parallel rows of pins extending down from opposite edges of the chip.

    There should be a semicircular notch that you can feel in the middle of one of the package's shorter bare edges. With the pins facing downward and the chip oriented so notch is on the side of the chip furthest from you, Pin 1 will be in the far left corner of the chip.

    Pins are numbered counter-clockwise. Numbers increase from the far left corner to the near left corner. They then continue on the right side, increasing from the near right corner to the far right corner. Thus the highest number pin is to the right of pin 1.
    """,
    group_names=["Left side (numbering starts at far end)", "Right side (numbering starts at near end)"],
)

TO220Package = Package(
    slug="TO-220",
    desc="""
    This package has 3 pins on one edge, and a metal tab with a hole in the center on the opposite edge. The metal tab serves as a heat sink and can be soldered to a larger heat sink or attached with an M3 screw.

    With the pins pointing towards you and the part flat on the table, tab side down, the pins are numbered 1, 2, 3 from left to right.

    The metal tab may be designated as pin 4. It is typically electrically connected to the center pin.
    """,
    max_pins=4,
)

TO92Package = Package(
    slug="TO-92",
    desc="""
    This small package has three pins protruding from one end. The body of the part has a curved side and a flat side, forming a D-shaped cross section. With the flat side facing up and the three pins pointing toward you, the pins are numbered 1, 2, 3 from left to right.
    """,
    max_pins=3,
)


# The keys here are the KiCAD footprint name
PACKAGE_REGISTRY: Dict[str, Package] = {
    'Package_TO_SOT_THT:TO-220-3_Vertical': TO220Package,
    'digikey-footprints:TO-220-3': TO220Package,
    "Package_TO_SOT_THT:TO-92_Inline": TO92Package,
    'digikey-footprints:TO-92-3': TO92Package,
    'digikey-footprints:TO-92-3_Formed_Leads': TO92Package,
}

THT_DIP_KEYS = [
    'Package_DIP:DIP-12_W7.62mm',
    'Package_DIP:DIP-14_W7.62mm',
    'Package_DIP:DIP-16_W10.16mm',
    'Package_DIP:DIP-16_W7.62mm',
    'Package_DIP:DIP-18_W7.62mm',
    'Package_DIP:DIP-20_W7.62mm',
    'Package_DIP:DIP-20_W7.62mm_LongPads',
    'Package_DIP:DIP-22_W7.62mm',
    'Package_DIP:DIP-24_W15.24mm',
    'Package_DIP:DIP-24_W7.62mm',
    'Package_DIP:DIP-28_W15.24mm',
    'Package_DIP:DIP-28_W7.62mm',
    'Package_DIP:DIP-32_W15.24mm',
    'Package_DIP:DIP-40_W15.24mm',
    'Package_DIP:DIP-4_W10.16mm',
    'Package_DIP:DIP-4_W7.62mm',
    'Package_DIP:DIP-5-6_W7.62mm',
    'Package_DIP:DIP-6_W7.62mm',
    'Package_DIP:DIP-8-N6_W7.62mm',
    'Package_DIP:DIP-8-N7_W7.62mm',
    'Package_DIP:DIP-8_W10.16mm',
    'Package_DIP:DIP-8_W7.62mm',
    'Package_DIP:DIP-8_W7.62mm_LongPads',
    'digikey-footprints:DIP-8_W7.62mm',
    'digikey-footprints:DIP-14_W3mm',
    'digikey-footprints:DIP-16_W7.62mm',
    'digikey-footprints:DIP-6_W7.62mm',
    'digikey-footprints:DIP-28_W7.62mm',
    'digikey-footprints:DIP-20_W7.62mm',
    'digikey-footprints:DIP-18_W7.62mm',
    'digikey-footprints:DIP-4_W7.62mm',
    'digikey-footprints:DIP-40_W15.24mm',
    'digikey-footprints:DIP-10_W10.16mm',
    'DIP*W7.62mm*',
]

for key in THT_DIP_KEYS:
    PACKAGE_REGISTRY[key] = DIPPackage
