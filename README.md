# far-medicine

**diagnoses, treatments, trials, dosing, contraindications. Evidence is the gate; opinion is not.**

diagnostic criteria, treatment protocols, trial summaries, dosing tables, contraindication lists, the medical-text pipeline.

## What this repo is

- A free, public-domain substrate for the medical-text pipeline.
- A gate (evidence schema) that no document enters without citation to primary literature.
- A growing library of cited protocols, trial summaries, and dosing references.

## What this repo is not

- A prompt collection. (Prompts are noise without evidence.)
- A house-style. (The whole point is *named* condition + cited evidence, not default voice.)
- A model zoo. (Models belong upstream; we use the open ones.)
- Medical advice. (This is a substrate and tooling. Use a clinician.)

## AGENTS.md

The schema lives in [AGENTS.md](./AGENTS.md). Read it first. The
evidence axes (condition, study type, sample size, effect size, CI,
GRADE) are the contract.

## Repo layout

```
far-medicine/
├── AGENTS.md                # the evidence schema (this is the contract)
├── README.md                # this file
├── LICENSE                  # MIT
├── CONTRIBUTORS.md          # who built this
├── protocols/               # treatment protocols
├── trials/                  # trial summaries
├── dosing/                  # dosing tables
├── tools/                   # evidence.compile + evidence.gate
└── tests/                   # Med1..Med5 gate tests
```

## Quick start

```bash
git clone https://github.com/the-far-queen/far-medicine.git
cd far-medicine
# Read AGENTS.md
# Pick a protocol from protocols/
# Compile a variant: python tools/compile_evidence.py path/to/protocol.yaml
# Gate: python tools/gate.py path/to/protocol.json
```

## License

MIT. Free for all agents, human and non-human. No copyright trap.
No paywall. No "research only" carve-out. Evidence summaries belong to everyone.

## Sister repos

the-far-queen/far-writing (voice substrate), the-far-queen/simself
(constitutional identity + kernel), the-far-queen/fieldcore (geometric
substrate). Far-medicine sits on top of far-writing: every clinical
text is a voice with evidence constraints.

## Status

Early scaffold. Schema, gate, and first protocol templates landing
in the next pass. Pull requests welcome — see CONTRIBUTORS.md.