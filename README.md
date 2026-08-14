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

The [worked browser example](https://expectedparrot.github.io/flyvbjerg/)
builds an outside view of theatrical stage-musical adaptations from reported
budgets and worldwide box office. The earlier
[Upwork product-launch tutorial](https://expectedparrot.github.io/flyvbjerg/upwork-product-launches.html)
remains available as a secondary example of the intake-first workflow.

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

Use the best available evidence for the task. Wikipedia and similar tertiary
sources are valid for company histories, identities, ownership, products,
chronology, and reported actions. Prefer stronger sources when readily
available or when a claim is disputed, causal, quantitative, determines cohort
membership, or asserts an absence. Never treat a source's silence as evidence
that an event did not occur. See `flyvbjerg guide --topic evidence`.

Decision-facing analysis can position a target value and evaluate thresholds
without changing the locked reference distribution:

```bash
flyvbjerg locate ANALYSIS --value 365 --label management_estimate
flyvbjerg threshold ANALYSIS --operator le --value 365
flyvbjerg plot ANALYSIS --kind ecdf --target-value 365 --output distribution.svg
```

Analysis distributions report nearest-rank empirical quantiles. When no
dependence groups are supplied, dependence is reported as `not_assessed` and
cluster count remains null rather than defaulting to the subject count.
Plots are deterministic SVG artifacts accompanied by JSON receipts identifying
their source analysis and content hash.

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

## Business and government applications

Flyvbjerg is useful when a decision-maker faces a recurring class of projects
or events, has an inside-view forecast, and can reconstruct historical cases
without selecting membership based on what happened later. The table below
gives 20 promising applications and realistic starting points for evidence.

| Application | Decision supported | Possible data sources |
|---|---|---|
| M&A completion risk | Closing-time allowance, regulatory exposure, and termination risk | SEC filings and 8-Ks; company announcements; FTC, DOJ, CMA, and European Commission decisions; Wikipedia transaction histories; LSEG, Bloomberg, PitchBook, or S&P Capital IQ |
| New-product launches | Launch schedule, adoption range, and commercial downside | Company press releases and product blogs; earnings calls and filings; app stores; product documentation and changelogs; retailer data; archived websites; Wikipedia company histories |
| Enterprise software implementations | Duration, cost growth, scope reduction, and abandonment risk | Internal PMO and procurement systems; vendor case studies; audit reports; litigation; public contract records; Government Accountability Office and inspector-general reports |
| Factory and capacity expansions | Construction time, capital overrun, and ramp-to-utilization allowance | Company filings and investor presentations; permitting databases; environmental reviews; local planning records; trade press; satellite or facility data |
| Corporate restructurings and spin-offs | Time to first independence, full completion, and plan revision | SEC Form 10 filings and 8-Ks; investor-relations releases; exchange notices; annual reports; Wikipedia company histories; financial news archives |
| Technology-disruption responses | Timing and portfolio of incumbent responses to a new technology | Wikipedia company and technology histories; annual reports; patents; product announcements; trade journals; archived company sites; earnings transcripts |
| Startup and corporate-venture portfolios | Follow-on funding, commercialization, acquisition, or shutdown base rates | Crunchbase, PitchBook, Dealroom, and SEC Form D; accelerator and corporate-venture portfolios; company websites; app stores; web archives; press databases |
| Drug-development programs | Phase-transition time, approval probability, delay, and attrition | ClinicalTrials.gov; FDA Drugs@FDA and advisory materials; EMA records; trial registries; company pipelines and filings; publications and conference abstracts |
| Retail-market expansion | Store-opening pace, maturity economics, and closure risk | Company filings; store locators and archived websites; municipal permits; commercial real-estate databases; foot-traffic providers; OpenStreetMap; local news |
| Film, media, and entertainment investments | Budget exposure, release risk, and revenue scenarios | Wikipedia film histories; Box Office Mojo and The Numbers; studio releases; trade publications; production tax-credit records; Nielsen and streaming disclosures |
| Large outsourcing contracts | Transition time, service attainment, renegotiation, and termination risk | Internal contract and service-management systems; procurement notices; contract awards; court filings; customer and vendor announcements; audit reports |
| Cybersecurity incidents | Containment and recovery time, disclosure lag, and loss exposure | SEC cyber disclosures; state breach notices; CISA advisories; company incident reports; insurer and forensic reports; court filings; outage telemetry |
| Supplier and technology migrations | Switching duration, dual-running cost, disruption, and failure risk | Internal procurement and operations records; ERP change logs; vendor announcements; regulatory filings; recalls; customer-status pages; postmortems |
| Turnaround and restructuring plans | Liquidity runway, milestone attainment, asset-sale timing, and bankruptcy risk | Bankruptcy dockets; restructuring-support agreements; SEC filings; lender presentations; rating-agency reports; court-appointed examiner and monitor reports |
| Major litigation and regulatory proceedings | Duration, legal-cost allowance, settlement, judgment, and remedy risk | PACER and state court dockets; agency enforcement databases; consent decrees; company filings; legal research services; Wikipedia case histories |
| Public infrastructure projects | Cost and schedule overrun, opening delay, scope change, and demand risk | Agency capital plans; procurement portals; environmental-impact statements; legislative audits; GAO reports; World Bank and OECD project data; local news |
| Government IT modernization | Procurement-to-deployment time, contract growth, partial delivery, and cancellation | USAspending.gov and SAM.gov; agency dashboards; GAO and inspector-general reports; congressional testimony; state procurement systems; contract documents |
| Emergency and disaster recovery | Time to restore utilities, housing, transport, schools, and public services | FEMA OpenFEMA; NOAA and USGS; utility outage data; insurance claims; state emergency reports; satellite imagery; after-action reports; academic disaster datasets |
| Policy implementation | Time from enactment to rules and operation, litigation delay, and compliance uptake | Congress.gov and state legislatures; Federal Register and Regulations.gov; agency guidance; court dockets; implementation dashboards; inspector-general and GAO reports |
| Public procurement and defense acquisition | Award time, protest delay, development duration, unit-cost growth, and cancellation | SAM.gov, USAspending.gov, and FPDS; GAO bid-protest decisions; Selected Acquisition Reports; Congressional Budget Office and CRS; inspector-general reports |

These domains tend to reuse a small set of analytical patterns:

- elapsed time from announcement, authorization, or award to a milestone or
  competing terminal state;
- original estimate versus realized cost;
- the fraction attaining a milestone by a decision threshold;
- scope, schedule, or intended-outcome revision;
- completion, cancellation, termination, or supersession;
- the location of a current estimate in an empirical distribution; and
- sensitivity to cohort boundaries, metric versions, missingness, and
  dependence assumptions.

Public sources can support a useful first pass, but internal operational data
often produce the most decision-relevant reference class. In either case,
source availability must not become an implicit outcome filter: register cases
from an outcome-independent enumeration, preserve unresolved and censored
cases, and represent unsupported measurements as missing rather than zero.

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

- [Primary worked example: theatrical musical adaptations](https://expectedparrot.github.io/flyvbjerg/)
- [Secondary worked example: Upwork product launches](https://expectedparrot.github.io/flyvbjerg/upwork-product-launches.html)
- [Local primary example](docs/index.html)
- [Local Upwork tutorial](docs/upwork-product-launches.html)
- [Specification](SPEC.md)
- [Practice notes](PRACTICE.md)
- [Agent operating contract](AGENTS.md)
- [MIT license](LICENSE)
