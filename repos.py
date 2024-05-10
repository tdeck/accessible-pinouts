from dataclasses import dataclass

@dataclass
class Repo:
    name: str
    path: str
    url: str

# TODO these could be automatically synced to some known location in /tmp so there would be no need for path
SYMBOL_REPOS = [
    Repo( # These will be overridden by the official symbol lib
        name='DigiKey KiCAD library',
        path='/home/troy/Downloads/pinout/digikey-kicad-library/modern-symbols',
        url='https://github.com/tdeck/digikey-kicad-library',
    ),
    Repo(
        name='KiCAD symbol library',
        path='/home/troy/Downloads/pinout/kicad-symbols',
        url='https://gitlab.com/kicad/libraries/kicad-symbols',
    ),
]

SYM_EXTENSION = '.kicad_sym'
