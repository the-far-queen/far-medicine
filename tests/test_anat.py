"""
test_anat.py — M1..M10 gate tests for far-medicine.

The load-bearing one is M4: an anatomy term must name the STRUCTURE it
describes. Without that, far-medicine is a vocabulary list wearing an
anatomy coat.

Run:  python tests/test_anat.py
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))

from anat import (  # noqa: E402
    Source, Term, BLOCKS, SYSTEMS, LICENSES, LICENSE_RANK,
    compile_term, gate_term, gate_license_never_upgraded,
)

DISK = list(BLOCKS)

GRAY = Source(
    title="Anatomy of the Human Body (20th US ed.)",
    author="Henry Gray; ed. Warren H. Lewis",
    edition="20th US edition",
    year=1918,
    source_url="https://www.gutenberg.org/ebooks/37417",
    license="public-domain",
    locator="digestive system",
)


def good_term(**over):
    base = dict(
        term="peritoneum",
        block="anatomy",
        system="digestive",
        definition="a double-layered serous membrane lining the abdominopelvic cavity",
        structure="peritoneum",
        sources=[GRAY],
    )
    base.update(over)
    return compile_term(**base)


def t_M1_repro_id():
    a = good_term()
    b = good_term()
    assert a.term_id() == b.term_id(), "same term, different id"
    c = good_term(term="mesentery")
    assert a.term_id() != c.term_id()
    print("M1: ok (deterministic term id)")


def t_M2_definition_required():
    t = good_term(definition="")
    v = gate_term(t, DISK)
    assert not v.allow
    assert "no_definition" in v.reasons
    print("M2: ok (empty definition refused)")


def t_M3_block_valid():
    t = good_term(block="crystal-healing")
    v = gate_term(t, DISK)
    assert not v.allow
    assert any(x.startswith("unknown_block") for x in v.reasons)
    print(f"M3: ok (fake block refused: {v.reasons})")


def t_M4_structure_required():
    """THE test. a term with no named structure is decoration."""
    t = good_term(structure="")
    v = gate_term(t, DISK)
    assert not v.allow, "structureless term was ALLOWED"
    assert "no_structure" in v.reasons, v.reasons
    print("M4: ok (structure anchor required)")


def t_M5_source_required():
    t = good_term(sources=[])
    v = gate_term(t, DISK)
    assert not v.allow
    assert "no_source" in v.reasons
    print("M5: ok (no source refused)")


def t_M6_source_needs_license():
    """an uncredited source is unusable — we cannot ship it or verify it."""
    t = good_term(sources=[Source(title="Some Book", source_url="https://x.example")])
    v = gate_term(t, DISK)
    assert not v.allow
    assert any(x.startswith("no_license") for x in v.reasons), v.reasons
    print(f"M6: ok (unlicensed source refused: {v.reasons})")


def t_M7_system_valid():
    t = good_term(system="aura")
    v = gate_term(t, DISK)
    assert not v.allow
    assert any(x.startswith("unknown_system") for x in v.reasons)
    print(f"M7: ok (unknown system refused: {v.reasons})")


def t_M8_license_never_upgraded():
    """NC-SA source may not be republished as CC-BY."""
    v = gate_license_never_upgraded("cc-by", "cc-by-nc-sa")
    assert not v.allow, "NC-SA upgrade was ALLOWED"
    # PD source may be labeled cc-by (narrowing is always allowed)
    v2 = gate_license_never_upgraded("cc-by", "public-domain")
    assert v2.allow, f"narrowing refused: {v2.reasons}"
    print(f"M8: ok (no license upgrade: {v.reasons})")


def t_M9_bad_year_refused():
    t = good_term(sources=[Source(title="x", source_url="https://y", license="public-domain", year=2500)])
    v = gate_term(t, DISK)
    assert not v.allow
    assert any(x.startswith("bad_year") for x in v.reasons)
    print(f"M9: ok (impossible year refused: {v.reasons})")


def t_M10_taxonomy_complete():
    """every declared block is scaffolded and unique."""
    assert len(BLOCKS) == len(set(BLOCKS)), "duplicate block"
    for b in BLOCKS:
        assert b in DISK, f"{b} declared but not scaffolded"
    # the med school core must all be present
    for core in ("anatomy", "physiology", "biochemistry", "pathology",
                 "pharmacology", "microbiology"):
        assert core in BLOCKS, f"core block {core} missing"
    print(f"M10: ok ({len(BLOCKS)} blocks declared and scaffolded)")


def main():
    t_M1_repro_id()
    t_M2_definition_required()
    t_M3_block_valid()
    t_M4_structure_required()
    t_M5_source_required()
    t_M6_source_needs_license()
    t_M7_system_valid()
    t_M8_license_never_upgraded()
    t_M9_bad_year_refused()
    t_M10_taxonomy_complete()
    print("\nALL FAR-MEDICINE GATE TESTS PASS (M1..M10)")


if __name__ == "__main__":
    main()
