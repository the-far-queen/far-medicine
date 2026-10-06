"""
anat.py — the far-medicine anatomy schema, compiler, and gate.

Same shape as far-law/tools/cite.py, deliberately. The two repos share a
contract: a claim without a source is refused, and a license is never
upgraded from what the source actually carries.

The clinical difference: anatomy terms are anchored to STRUCTURE
(organ system + named structure), not to citation alone. A term that
cannot name the structure it describes is decoration.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCKS_DIR = os.path.join(REPO, "blocks")

# ---------------------------------------------------------------------------
# the taxonomy: standard US medical school curriculum blocks
# (the USMLE Step 1 / Step 2 framework)
# ---------------------------------------------------------------------------
BLOCKS = [
    "anatomy",           # gross + regional, Gray's template
    "histology",         # tissue + cell biology
    "physiology",        # normal function
    "biochemistry",      # metabolic pathways
    "genetics",          # genomics, expression
    "microbiology",      # organisms, immune evasion
    "immunology",        # host response
    "pharmacology",      # agents, mechanisms, kinetics
    "pathology",         # disease mechanisms
    "neuroscience",      # CNS structure + function
    "psychiatry",        # mind, behavior, disorders
    "preventive",        # epidemiology, population health
    "clinical",          # medicine proper, the clerkship year
    "ethics",            # bioethics, law-in-medicine, consent
]

SYSTEMS = [
    "integumentary", "skeletal", "muscular", "nervous",
    "endocrine", "cardiovascular", "lymphatic", "respiratory",
    "digestive", "urinary", "reproductive",
]

LICENSES = ["public-domain", "cc-by", "cc-by-sa", "cc-by-nc-sa", "other"]

LICENSE_RANK = {
    "public-domain": 4,
    "cc-by": 3,
    "cc-by-sa": 2,
    "cc-by-nc-sa": 1,
    "other": 0,
}

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class Source:
    """where a claim came from."""
    title: str = ""
    author: str = ""
    edition: str = ""
    year: Optional[int] = None
    source_url: str = ""
    license: str = ""
    # the anchor inside the source — page, section, or chapter id
    locator: str = ""

    def is_empty(self) -> bool:
        return not (self.source_url or self.title)


@dataclass
class Term:
    """an anatomical or clinical term anchored to a structure."""
    term: str
    block: str
    system: str = ""
    definition: str = ""
    structure: str = ""          # the named anatomy this describes
    sources: List[Source] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)

    def term_id(self) -> str:
        h = hashlib.sha256(
            f"{self.term}|{self.block}|{self.system}".lower().encode("utf-8")
        ).hexdigest()
        return f"term-{h[:12]}"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["term_id"] = self.term_id()
        return d


@dataclass
class Verdict:
    allow: bool
    reasons: List[str] = field(default_factory=list)
    term_id: str = ""

    @classmethod
    def of(cls, allow: bool, reasons: List[str], term_id: str = "") -> "Verdict":
        return cls(allow=allow, reasons=reasons, term_id=term_id)

    def __str__(self) -> str:
        return f"{'ALLOW' if self.allow else 'DENY'} {self.term_id} {self.reasons}"


# ---------------------------------------------------------------------------
# gate
# ---------------------------------------------------------------------------

def _blocks_on_disk() -> List[str]:
    if not os.path.isdir(BLOCKS_DIR):
        return []
    return sorted(
        d for d in os.listdir(BLOCKS_DIR)
        if os.path.isdir(os.path.join(BLOCKS_DIR, d))
    )


def gate_term(t: Term, on_disk: Optional[List[str]] = None) -> Verdict:
    r: List[str] = []

    if not t.term.strip():
        r.append("no_term")
    if not t.definition.strip():
        r.append("no_definition")

    # a term must name the structure it describes — that is the difference
    # between an anatomy entry and a vocabulary entry
    if not t.structure:
        r.append("no_structure")

    disk = on_disk if on_disk is not None else _blocks_on_disk()
    if disk:
        if not t.block:
            r.append("no_block")
        elif t.block not in disk:
            r.append(f"unknown_block:{t.block}")

    if t.system and t.system not in SYSTEMS:
        r.append(f"unknown_system:{t.system}")

    # at least one real source, and it must carry a license
    if not t.sources:
        r.append("no_source")
    for i, s in enumerate(t.sources):
        if s.is_empty():
            r.append(f"empty_source:{i}")
        if not s.license:
            r.append(f"no_license:{i}")
        elif s.license not in LICENSES:
            r.append(f"unknown_license:{i}:{s.license}")
        if s.year is not None and not (1000 <= s.year <= 2100):
            r.append(f"bad_year:{i}:{s.year}")

    return Verdict.of(not r, r, t.term_id())


def gate_license_never_upgraded(claimed: str, source_license: str) -> Verdict:
    """a CC-BY-NC-SA source may not be republished as CC-BY."""
    if claimed in LICENSE_RANK and source_license in LICENSE_RANK:
        if LICENSE_RANK[claimed] > LICENSE_RANK[source_license]:
            return Verdict.of(False, [f"license_upgrade:{source_license}->{claimed}"])
    return Verdict.of(True, [])


def compile_term(term: str, block: str, **kw) -> Term:
    return Term(term=term, block=block, **kw)


# ---------------------------------------------------------------------------
# load / save
# ---------------------------------------------------------------------------

def load_terms(block: str) -> List[Term]:
    path = os.path.join(BLOCKS_DIR, block, "terms.json")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    out = []
    for d in (raw if isinstance(raw, list) else raw.get("terms", [])):
        d = dict(d)
        d.pop("term_id", None)
        srcs = [Source(**s) if isinstance(s, dict) else s for s in d.get("sources", [])]
        d["sources"] = srcs
        out.append(Term(**d))
    return out


def save_terms(block: str, terms: List[Term]) -> str:
    d = os.path.join(BLOCKS_DIR, block)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "terms.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in terms], f, indent=2, ensure_ascii=False)
    return path


# ---------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------

def _main(argv: List[str]) -> int:
    if not argv:
        print(__doc__)
        print("usage: anat.py gate <file.json> | anat.py list | anat.py init")
        return 1
    cmd = argv[0]

    if cmd == "list":
        print("blocks:")
        for b in _blocks_on_disk():
            print(f"  {b:16s} {len(load_terms(b)):5d} terms")
        return 0

    if cmd == "init":
        os.makedirs(BLOCKS_DIR, exist_ok=True)
        for b in BLOCKS:
            sub = os.path.join(BLOCKS_DIR, b)
            os.makedirs(os.path.join(sub, "texts"), exist_ok=True)
            readme = os.path.join(sub, "README.md")
            if not os.path.exists(readme):
                with open(readme, "w", encoding="utf-8") as f:
                    f.write(f"# {b}\n\nCurriculum block. Terms live in "
                            "`terms.json`, open textbooks in `texts/`.\n")
        print(f"initialized {len(BLOCKS)} blocks under {BLOCKS_DIR}")
        return 0

    if cmd == "gate":
        if len(argv) < 2:
            print("gate: need a file")
            return 1
        with open(argv[1], encoding="utf-8") as f:
            raw = json.load(f)
        raw.pop("term_id", None)
        raw["sources"] = [Source(**s) if isinstance(s, dict) else s
                          for s in raw.get("sources", [])]
        t = Term(**raw)
        v = gate_term(t)
        print(v)
        return 0 if v.allow else 2

    print(f"unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
