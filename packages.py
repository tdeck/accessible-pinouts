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

class Package:
    def __init__(self, desc, group_names: List[str]=[]):
        self._desc = dedent(desc).strip()
        self._group_names = group_names
            

    def desc(self) -> str:
        return self._desc

    def group_pins(self, pins: List[Pin]):
        """ Default behavior is to divide pins evenly into groups in given order. This is suitable for rectangular packages. """
        if not self._group_names:
            return PinGroup(name=None, pins=pins)

        assert len(pins) % len(self._group_names) == 0

        group_size = len(pins) // len(self._group_names)

        i = 0
        res = []
        for group_name in self._group_names:
            res.append(PinGroup(name=group_name, pins=pins[i:i+group_size]))

            i += group_size

        return res


DIPPackage = Package(
    desc="""
    This package has two parallel rows of pins extending down from opposite edges of the chip.

    There should be a semicircular notch that you can feel in the middle of one of the package's shorter bare edges. With the pins facing downward and the chip oriented so notch is on the side of the chip furthest from you, Pin 1 will be in the far left corner of the chip.

    Pins are numbered counter-clockwise. Numbers increase from the far left corner to the near left corner. They then continue on the right side, increasing from the near right corner to the far right corner. Thus the highest number pin is to the right of pin 1.
    """,
    group_names=["Left side (numbering starts at far end)", "Right side (numbering starts at near end)"],
)


# The keys here are the KiCAD footprint name
PACKAGE_REGISTRY: Dict[str, Package] = {}

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
]

for key in THT_DIP_KEYS:
    PACKAGE_REGISTRY[key] = DIPPackage
