# flyvbjerg

**An auditable reference-class evidence ledger for coding agents.**

<p align="center">
  <img src="docs/flyvbjerg-art.png" width="900" alt="An Expected Parrot assembling a Danish historical reference class inside EDSL brackets">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
[![EDSL](https://img.shields.io/badge/built%20on-EDSL-brightgreen.svg)](https://github.com/expectedparrot/edsl)

`flyvbjerg` is an agent-facing Python CLI for assembling evidence about
comparable cases and turning accepted observations into auditable
reference-class distributions. It is built on
[EDSL](https://github.com/expectedparrot/edsl) and developed by
[Expected Parrot](https://www.expectedparrot.com).

The coding agent performs research with its own tools. Flyvbjerg does not
search, browse, scrape, or download. It preserves registered sources and
captures, unresolved intake, persistent cases, events, claims, metrics,
decisions, missingness, dependence clusters, and frozen analyses.

The [worked browser tutorial](https://expectedparrot.github.io/flyvbjerg/)
follows real Upwork product evidence through the intake-first workflow.

## Copy and paste into a coding agent

```text
Set up Flyvbjerg and help me construct an auditable reference-class analysis in
this repository.

Install the current Flyvbjerg and EDSL main branches from GitHub with uv:

uv tool install --python 3.11 --upgrade --force \
  --with-executables-from "edsl @ git+https://github.com/expectedparrot/edsl.git@main" \
  "flyvbjerg @ git+https://github.com/expectedparrot/flyvbjerg.git@main"

Verify both agent-facing interfaces:

flyvbjerg version
flyvbjerg --help
ep --help

Use Flyvbjerg's CLI as the workflow source of truth:

flyvbjerg guide
flyvbjerg next

Run `flyvbjerg next` after each material stage. Research with your own tools;
Flyvbjerg must never browse or fetch sources. Register source identities,
preserve permitted captures, and keep unresolved material in intake until its
case, event, relationship, or claim identity is supportable.

Treat extracted claims and observations as candidates until explicitly
accepted. Preserve absence states, required metric context, target versions,
and dependence clusters. Never turn a missing or malformed result into a zero
or negative finding.

Flyvbjerg may construct native EDSL Jobs from registered captures, but it must
not execute them. Inspect Jobs and estimated cost, then stop for my approval
before any paid `ep run` unless I have already authorized it. Never display or
commit credentials.

Continue until the reference-class analysis is complete or my input or approval
is required.
```

## Install

Flyvbjerg requires Python 3.11 or newer. Install it together with EDSL's `ep`
executable:

```bash
uv tool install --python 3.11 --upgrade --force \
  --with-executables-from "edsl @ git+https://github.com/expectedparrot/edsl.git@main" \
  "flyvbjerg @ git+https://github.com/expectedparrot/flyvbjerg.git@main"
```

For repository development:

```bash
uv sync --extra test
uv run pytest -q
```

When co-developing against a local EDSL checkout:

```bash
python -m pip install -e '.[test]'
python -m pip install -e ../edsl
pytest -q
```

## Start a workspace

```bash
mkdir outside-view
cd outside-view
flyvbjerg init
flyvbjerg target create proposed-project --name "Proposed project"
flyvbjerg collection new comparable-projects --title "Comparable projects"
flyvbjerg next
```

Every command emits one versioned JSON envelope on stdout. Errors are structured
and nonzero; logs belong on stderr. Each `next_steps` entry states whether the
action mutates state, requires network access, or requires user approval.

## Operating model

The evidence lifecycle is:

```text
agent research → sources and captures → unresolved intake
               → cases, events, relationships, and claims
               → metrics and explicit evidence decisions
               → frozen analysis sets and sensitivity checks
               → forecasts (later slice)
```

Targets are workspace-level and versioned. Collections remain exploratory until
their analytical unit and membership policy are defensible. Metrics can be
introduced after rich cases exist, and may require contextual fields or derive
values deterministically from exact event pairs.

Distinct cases are not automatically independent. Analysis sets record shared
program or intervention clusters, report both case and cluster counts, and
support leave-one-cluster-out sensitivity.

## EDSL boundary

Flyvbjerg uses native EDSL objects for bounded extraction, coding, and
verification over captures already registered in the workspace:

```bash
flyvbjerg process plan COLLECTION --name extraction --mode extract \
  --capture CAPTURE_ID
flyvbjerg process approve RUN_ID
flyvbjerg process build RUN_ID
ep inspect PATH/TO/jobs.ep
ep jobs cost PATH/TO/jobs.ep
# Obtain explicit approval before model execution.
ep run PATH/TO/jobs.ep --output results.ep
```

Building a package never authorizes inference. The exact Jobs, Results,
registrations, and audits remain part of the evidence trail.

## Central caveat

A reference-class distribution is only as defensible as its unit, membership
rules, evidence decisions, metric semantics, context coverage, and dependence
assumptions. Flyvbjerg makes those choices inspectable; it does not make them
correct automatically or convert management attribution into causal evidence.

## Documentation

- [Worked tutorial](https://expectedparrot.github.io/flyvbjerg/)
- [Local tutorial source](docs/index.html)
- [Specification](SPEC.md)
- [Practice notes](PRACTICE.md)
- [Agent operating contract](AGENTS.md)
- [MIT license](LICENSE)
