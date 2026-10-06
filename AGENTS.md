# AGENTS.md — far-medicine (the anatomy contract)

> An anatomy term with no structure is decoration.

This file is the contract. Every term passes through it. Every test
reads it.

If you change the schema, update AGENTS.md first. The repo is
downstream of this file.

## What this repo is

A free, open-source substrate for a medical education pipeline: terms
anchored to named anatomical structures, organized by the standard US
medical school curriculum, sourced from public-domain and
openly-licensed textbooks.

## What this repo is NOT

- **Not clinical advice.** This is a substrate and tooling. Use a
  clinician.
- **Not a diagnosis tool.** Nothing here takes a patient.
- **Not a vocabulary list.** A term that cannot name the structure it
  describes is refused by the gate.
- **Not a casebook farm.** AI-generated clinical summaries presented as
  authoritative are the failure mode this repo exists to prevent.

## Blocks (the taxonomy)

Standard US medical school curriculum — the USMLE Step 1 / Step 2
framework. Each block is a directory under `blocks/`.

```
blocks/
├── anatomy          # gross + regional (Gray's template)
├── histology        # tissue + cell biology
├── physiology       # normal function
├── biochemistry     # metabolic pathways
├── genetics         # genomics, expression
├── microbiology     # organisms, immune evasion
├── immunology       # host response
├── pharmacology     # agents, mechanisms, kinetics
├── pathology        # disease mechanisms
├── neuroscience     # CNS structure + function
├── psychiatry       # mind, behavior, disorders
├── preventive       # epidemiology, population health
├── clinical         # medicine proper, the clerkship year
└── ethics           # bioethics, consent, law-in-medicine
```

## Packet

```
Term     term_id | block | system | term | definition | structure | sources[]
Source   title | author | edition | year | source_url | license | locator
```

**No term without a structure and at least one licensed source.** The
gate refuses naked terms.

## Axes (the term contract)

| Axis | Type | Values |
|---|---|---|
| `block` | enum | one of the 14 directories above |
| `system` | enum | integumentary, skeletal, muscular, nervous, endocrine, cardiovascular, lymphatic, respiratory, digestive, urinary, reproductive |
| `term` | string | the term itself |
| `definition` | string | what it is, in the source's terms or our own |
| `structure` | string | **the named anatomy this describes** |
| `sources` | Source[] | one or more, each with license + locator |
| `see_also` | string[] | related terms |

## The structure anchor (load-bearing)

`structure` is what separates an anatomy substrate from a word list.
Every term names the physical thing it refers to. `peritoneum` is a
double-layered serous membrane lining the abominopelvic cavity; the
structure is the peritoneum itself. Test M4 enforces it.

## License rules per source (load-bearing)

This repo is MIT for **our own** material. It cannot relicense anyone
else's. The gate records license per source and refuses to upgrade it.

| Material | Status | Verdict |
|---|---|---|
| Gray's Anatomy, 20th US ed. (1918, ed. Warren H. Lewis) | public domain | **SAFE** |
| Gray's Anatomy for Students (2005+) | Elsevier | **NOT SAFE** |
| Gray's Anatomy 40th/41st/42nd ed. | Elsevier | **NOT SAFE** |
| OpenStax (all books) | **CC BY-NC-SA 4.0** | **NC + SA — see below** |
| LibreTexts | typically CC-BY-NC-SA | NC + SA constrain use |
| NCBI Bookshelf / OpenBook | US government work | **SAFE** (verify per title) |
| Project Gutenberg anatomy texts | public domain | **SAFE** (verify per title) |
| BRS / Schwartz / Moore Clinically Oriented Anatomy | Elsevier | **NOT SAFE** |
| Netter Atlas | Elsevier | **NOT SAFE** |

### The OpenStax trap

OpenStax is widely described as "CC-BY". **It is not.** Verified on
openstax.org on 2026-10-06: textbooks are licensed
**Creative Commons Attribution-NonCommercial-ShareAlike 4.0**, and the
site footer states this explicitly.

Consequences:

1. **NonCommercial** — may not be used in a commercial product. Our
   repos are free and non-commercial today, so this holds now, but it is
   a standing constraint, not a permanent permission.
2. **ShareAlike** — derivative works inherit NC-SA. A far-medicine page
   built from OpenStax text cannot be relicensed MIT.
3. **Attribution mandatory** — author, title, and license must ship
   with any adapted material.

The rule: index and link to OpenStax; write our own text about the
subject. Where a definition is taken verbatim from OpenStax, that entry
is marked `cc-by-nc-sa` and stays NC-SA permanently. Test M8 refuses the
upgrade.

## Surface

```
term.compile(block, term, ...)
term.gate(term)
term.load(block)
term.save(block, terms)
```

## Gate

The gate checks:

1. `term` and `definition` non-empty
2. `structure` present — **the anatomy anchor**
3. `block` is a real directory on disk
4. `system`, if present, is on the list
5. at least one source, each carrying a title/url **and a license**
6. `year` in a plausible range
7. license never upgraded above what the source carries

## Tests

| # | Test | What it checks |
|---|---|---|
| M1 | repro id | same term/block/system → same id |
| M2 | definition required | empty definition refused |
| M3 | block valid | unknown block refused |
| M4 | structure required | **structureless term refused** |
| M5 | source required | no source refused |
| M6 | source licensed | unlicensed source refused |
| M7 | system valid | unknown system refused |
| M8 | no license upgrade | NC-SA cannot ship as CC-BY |
| M9 | year plausible | year 2500 refused |
| M10 | taxonomy complete | all 14 blocks declared and scaffolded |

## Anti-patterns

- vocabulary dressed as anatomy (no structure anchor)
- AI-written clinical content presented as authoritative
- copying a copyrighted atlas or textbook into the repo
- one house voice across all systems
- upgrading a license to make a table look tidy

## Related

- the-far-queen/far-writing/ — voice schema + voice.py
- the-far-queen/simself/ — constitutional identity + kernel
- the-far-queen/fieldcore/ — geometric substrate
- the-far-queen/far-law/ — sibling repo, same gate shape

## License

MIT for our own material. Third-party material retains its own license,
recorded per source. No copyright trap. No paywall.
