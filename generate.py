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
import git

from repos import *
from packages import *

OUTDIR = '/home/troy/projects/static/blindmakers/content/pinouts'
#OUTDIR = '/home/troy/tmp/pinout-gen'

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))

DEBUG=False

def debug(*args):
    if DEBUG:
        print(*args)


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


def has_meaningful_pin_labels(pins: List[Pin]):
    for pin in pins:
        name = pin.name
        if name != "~" and name != "" and name != "NC":
            return True
    return False


def reformat_label(txt: str) -> str:
    """ Replaces some of the formatting used in KiCAD symbols with more human readable formatting. """

    # Inverted (overbar) pins
    txt = re.sub(r'~\{(.+?)\}', r'\1 (active low)', txt)

    # Subscript + superscript (not much we can do here so we just clean up the braces)
    txt = re.sub(r'_\{(.+?)\}', r'_\1', txt)
    txt = re.sub(r'\^\{(.+?)\}', r'_\1', txt)

    # Slashes
    txt = re.sub(r'(\S)/(\S)', r'\1 / \2', txt)

    return txt


def process_part_instance(symbol: Symbol, repo: Repo, footprint: str, parent: Optional[Symbol], repo_rev: str) -> None:
    if footprint not in PACKAGE_REGISTRY:
        debug("footprint reject", symbol.entryName, footprint)
        return
    
    
    pin_part = parent or symbol
    kc_pins = [p for u in pin_part.units for p in u.pins]

    if not kc_pins:
        debug("Pins reject", symbol.entryName)
        return

    if not has_meaningful_pin_labels(kc_pins):
        debug("Label reject", symbol.entryName)
        return

    pins = [
        Pin(
            name=reformat_label(p.name),
            number=int(p.number),
        )
        for p in kc_pins
    ]

    pins.sort(key=lambda p: p.number)
    
    pkg = PACKAGE_REGISTRY[footprint]

    part_id = symbol.entryName + '_' + pkg.slug

    try:
        part = Part(
            part_id=part_id,
            name=symbol.entryName, # TODO check for a better one
            desc=prop_value(symbol, 'Description'),
            pkg_desc=pkg.desc(),
            pin_groups=pkg.group_pins(pins),
            source_name=repo.name,
            source_url=repo.url,
            source_revision=repo_rev,
        )

        with open(f"{OUTDIR}/{part_id}.html", 'w') as fh:
            fh.write(template.render(part=part))
    except AssertionError as e:
        print(f"Part {symbol.entryName} is weird!", str(e))

def process_symbol(symbol: Symbol, repo: Repo, lib: SymbolLib, repo_rev: str) -> None:
    single_footprint = prop_value(symbol, 'Footprint')

    if single_footprint is None or single_footprint == '':
        fp_filters = prop_value(symbol, 'ki_fp_filters')
        if not fp_filters:
            debug("No footprint", symbol.entryName)
            return # Nothing to do 

        footprints = [f.strip() for f in fp_filters.split()]
    else:
        footprints = [single_footprint]

    parent = None
    if sym.extends:
        parent = next((s for s in lib.symbols if s.entryName == sym.extends))


    for footprint in footprints:
        process_part_instance(
            symbol=symbol,
            repo=repo,
            footprint=footprint,
            parent=parent,
            repo_rev=repo_rev
        )


if __name__ == '__main__':
    # Prepare the list of files to process
    repos_and_files = []
    for repo in SYMBOL_REPOS:
        # Determine git hash
        git_repo = git.Repo(repo.path, search_parent_directories=True)
        revision = git_repo.head.object.hexsha[:6]

        for filename in os.listdir(repo.path):
            if not filename.endswith(SYM_EXTENSION):
                continue

            file = os.path.join(repo.path, filename)
            sym_lib = SymbolLib.from_file(file)

            # Generate pinouts for all eligible parts in the catalog
            for sym in sym_lib.symbols:
                process_symbol(sym, repo, sym_lib, revision)
