# Corporate separations: Wikipedia-based reference-class pilot

This is a new-domain stress test of Flyvbjerg using eight large US public
companies that announced a breakup or spin-off from 2014 through 2022.
Membership uses announcement-era facts, so the cohort does not select on later
success. Wikipedia is the registered evidence source for identity, chronology,
and descriptive history.

## What the pilot asks

The decision question is not whether breakups are good. It is narrower and
actionable: how much calendar time should a decision-maker allow after a public
separation announcement?

Two endpoints prevent a phased plan from being flattened:

1. **First separation:** the first planned company becomes independent.
2. **Full plan:** all separations in the latest documented plan are complete.

Kellogg's January 2023 revision is retained explicitly: the announced
plant-based spin-off was shelved, while the cereal separation proceeded. GE's
HealthCare and Vernova separations are retained as distinct first and final
endpoints.

## Audited results

| Case | First separation (days) | Full plan (days) |
|---|---:|---:|
| eBay / PayPal | 291 | 291 |
| Hewlett-Packard / HPE | 391 | 391 |
| IBM / Kyndryl | 392 | 392 |
| Alcoa / Arconic | 400 | 400 |
| General Electric | 421 | 875 |
| Kellogg / Kellanova and WK Kellogg | 468 | 468 |
| United Technologies / Carrier and Otis | 494 | 494 |
| 3M / Solventum | 615 | 615 |

- First separation: median **410.5 days**, range **291–615**.
- Full plan: median **434 days**, range **291–875**.
- Only **1/8** reached first independence within 12 months.
- An 18-month (548-day) allowance covered **7/8** first separations and **6/8**
  full plans.
- A 24-month (730-day) allowance covered **8/8** first separations and **7/8**
  full plans.

![Ordered first-separation durations](plots/first-separation-ordered.svg)

![Ordered full-plan durations](plots/full-plan-ordered.svg)

## Decision interpretation

In this small seed cohort, 12 months looks aggressive. Eighteen months is a
reasonable central planning allowance for reaching first independence, but it
is not a conservative allowance for a phased breakup. Twenty-four months covers
every first separation in the pilot, while GE shows that full execution of a
multi-stage plan can extend toward 30 months.

These are provisional empirical frequencies, not population estimates. The
eight cases were documented in advance of looking at their durations, but the
seed list has not been independently certified as exhaustive. A real decision
should add an enumeration audit and assess comparability on number of planned
successors, tax/regulatory complexity, and whether the target date means legal
distribution or first trading.

## Audit trail

The cohort rule and endpoint policy are in [definition.md](definition.md).
Registered sources, events, candidate-to-accepted decisions, coverage states,
metric versions, distributions, and plot receipts are under `.flyvbjerg/` and
`plots/`. `flyvbjerg validate` reports 98 valid JSON records. No native EDSL Job
was constructed or executed, and no paid model call was used.

Workflow limitations encountered are recorded in
[friction-log.md](friction-log.md).
