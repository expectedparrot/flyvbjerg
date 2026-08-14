# How long do large technology acquisitions take?

## A Wikipedia-supported reference-class pilot for deal timing and completion risk

## Decision brief

Executives evaluating a large acquisition usually have an inside-view schedule:
the parties expect to close by a stated quarter, integration plans assume a
particular date, and financing or investor communications reflect that plan.
The relevant outside-view question is not whether the schedule is possible. It
is how that schedule compares with the experience of similar announced deals,
including agreements that never closed.

This pilot examines ten definitive agreements to acquire technology companies.
Each was announced between 2015 and 2022 with announced consideration of at
least $20 billion. Cases entered the cohort when the agreement was announced;
later completion or termination played no role in selection.

The pilot results are:

- Seven of ten agreements completed and three terminated.
- Time from announcement to completion or termination ranged from 185 to 637
  days.
- The median time to a terminal state was 467 days, approximately 15.3 months;
  the mean was 426 days.
- No deal reached a terminal state within six months. Four of ten did so within
  12 months, eight within 18 months, and all ten within 24 months.
- Among the seven completed deals, four closed within 12 months and six within
  18 months.

For a hypothetical newly announced transaction with a 12-month closing
estimate, the outside view is cautionary. Twelve months is faster than the
pilot median, and only 40% of the agreements had reached any terminal state by
then. That does not mean the target has a 40% chance of closing within a year:
the seed cohort is small, not yet certified exhaustive, and does not adjust for
regulatory overlap, jurisdictions, deal structure, or transaction-specific
facts. It does mean that a one-year plan should be presented as relatively
aggressive rather than historically routine.

The figures below make the outside-view comparison concrete. Both are generated
directly from the locked Flyvbjerg analysis and display its identity and
methodological caveats.

![Ordered announcement-to-terminal durations. The 365-day target is faster
than six of ten observed cases.](plots/terminal-duration-ordered.svg)

The ordered view shows a meaningful gap around the target. Four cases resolved
between 185 and 331 days. The next observed case, Adobe–Figma, did not terminate
until day 459. A 365-day estimate falls between the faster four and slower six,
not near the center of a dense group.

![Empirical cumulative distribution of announcement-to-terminal duration. At
365 days the observed cumulative fraction is 0.40.](plots/terminal-duration-ecdf.svg)

Reading vertically at 365 days gives 0.40. Reading horizontally from 0.50
places the nearest-rank empirical P50 at 459 days, while the conventional
even-sample median is 467 days. The chart uses steps rather than a smoothed
curve because ten observations do not justify invented continuity or precision.

The product lesson is that a decision-facing reference-class tool must connect
individual historical cases, the empirical distribution, a target estimate,
and a decision threshold without hiding missingness or dependence assumptions.

## The decision problem

The period between signing and terminal resolution creates real exposure. The
buyer and target must retain employees, operate under restrictions, maintain
financing, answer regulators, and plan for an integration that may be delayed
or never occur. A schedule that is too optimistic can distort financing costs,
synergy timing, retention programs, product road maps, and communications with
boards and investors.

An individual deal team will naturally emphasize its own legal analysis,
regulatory strategy, and expected timetable. Those facts matter. But they can
also produce overconfidence because every transaction appears unique from the
inside. Reference-class analysis supplies a disciplined baseline before
transaction-specific adjustments are applied.

The useful questions are:

1. How long did comparable announced agreements take to reach completion or
   termination?
2. What fraction completed at all?
3. What fraction resolved within the planning threshold?
4. Is management's schedule near the historical center or in an optimistic
   tail?
5. Which target-specific facts justify moving away from the outside view?

This pilot addresses the first four questions descriptively. It does not yet
estimate a causal effect of deal characteristics or produce an adjusted
probability for a specific transaction.

## Cohort construction

The pilot unit is one publicly announced definitive acquisition agreement. The
seed inclusion rule requires:

- an agreement announced from 2015 through 2022;
- a target whose principal business is technology;
- announced consideration of at least $20 billion; and
- a definitive agreement rather than an informal or hostile proposal.

Transaction value is assessed at announcement. This matters for stock deals,
whose reported value can change before closing. Realized consideration is a
different measurement and should not silently alter eligibility.

The cohort includes terminated agreements. Excluding them would select on the
outcome and answer only, “How long did the deals that eventually completed take
to close?” That conditional question can be useful, but it cannot estimate the
experience facing a decision-maker at announcement.

The ten seed cases are Dell–EMC, Qualcomm–NXP, IBM–Red Hat, AMD–Xilinx,
Salesforce–Slack, Nvidia–Arm, Microsoft–Activision Blizzard,
Broadcom–VMware, Adobe–Figma, and Elon Musk–Twitter.

The cohort is documented but not yet proven exhaustive. Before using its
completion share as a market base rate, it should be checked against an
independent enumeration of every qualifying announcement. Complete measurement
of the cases already found is not the same as complete discovery of the
reference class.

## Why Wikipedia works for this pilot

Large acquisitions commonly have dedicated Wikipedia pages or substantial
sections in company histories. These pages often state the parties, announced
value, definitive-agreement date, completion or termination date, regulatory
challenges, and successor identity. They also link to company announcements,
regulatory documents, and contemporaneous reporting.

That makes Wikipedia effective best-available evidence for a first-pass
chronology. It is not treated as infallible. Exact dates were registered with
their page identities, and absence from a page was never treated as proof that
an event did not occur. Claims that determine a disputed cohort boundary or
assert an absence would merit checking against the page's underlying sources.

Representative pages include [Dell](https://en.wikipedia.org/wiki/Dell),
[Red Hat](https://en.wikipedia.org/wiki/Red_Hat),
[Xilinx](https://en.wikipedia.org/wiki/Xilinx),
[Salesforce](https://en.wikipedia.org/wiki/Salesforce),
[Microsoft–Activision Blizzard](https://en.wikipedia.org/wiki/Acquisition_of_Activision_Blizzard_by_Microsoft),
and [Broadcom](https://en.wikipedia.org/wiki/Broadcom).

## Results and interpretation

### Deal-level chronology behind the ordered plot

| Agreement | Announced | Terminal date | State | Days |
|---|---:|---:|---|---:|
| Elon Musk–Twitter | 2022-04-25 | 2022-10-27 | Completed | 185 |
| Salesforce–Slack | 2020-12-01 | 2021-07-21 | Completed | 232 |
| IBM–Red Hat | 2018-10-28 | 2019-07-09 | Completed | 254 |
| Dell–EMC | 2015-10-12 | 2016-09-07 | Completed | 331 |
| Adobe–Figma | 2022-09-15 | 2023-12-18 | Terminated | 459 |
| AMD–Xilinx | 2020-10-27 | 2022-02-14 | Completed | 475 |
| Nvidia–Arm | 2020-09-13 | 2022-02-08 | Terminated | 513 |
| Broadcom–VMware | 2022-05-26 | 2023-11-22 | Completed | 545 |
| Microsoft–Activision Blizzard | 2022-01-18 | 2023-10-13 | Completed | 633 |
| Qualcomm–NXP | 2016-10-27 | 2018-07-26 | Terminated | 637 |

The table is the audit-friendly counterpart to the ordered plot. The fastest
terminal event still took slightly more than six months. Four transactions
resolved in less than a year, while four others clustered between roughly 15
and 18 months. Two took about 21 months.

### Threshold view

| Planning threshold | All terminal states | Completed by threshold |
|---|---:|---:|
| 6 months | 0/10 (0%) | 0/10 (0%) |
| 12 months | 4/10 (40%) | 4/10 (40%) |
| 18 months | 8/10 (80%) | 6/10 (60%) |
| 24 months | 10/10 (100%) | 7/10 (70%) |

The columns answer different questions. “All terminal states” measures when
uncertainty ended, regardless of result. “Completed by threshold” measures
whether the acquisition had actually closed. At 18 months, two terminated
agreements had resolved in addition to six completed deals; treating all eight
as successful closings would be a serious error.

The ECDF plots time to any terminal state. It does not yet distinguish
completion and termination visually, so the table remains necessary to prevent
the duration curve from being read as a closing-probability curve.

### Completion-conditioned view

Among the seven deals that ultimately completed, the median closing time was
331 days and the mean approximately 379 days. Four of seven closed within 12
months and six of seven within 18 months.

Among the three terminated deals, terminal durations were 459, 513, and 637
days. This small comparison suggests that failure was not necessarily resolved
quickly: parties could remain exposed for well over a year before termination.
It should not be interpreted as a stable estimate of how long failed deals take
because only three such cases are present.

## Interpreting a 12-month inside-view estimate

Suppose management expects a newly announced qualifying acquisition to close
within 12 months.

The unadjusted pilot says:

- 12 months is below the 467-day reference median;
- 4/10 agreements reached any terminal state within that interval;
- the same 4/10 completed within it; and
- 6/10 remained unresolved after one year.

The correct decision statement is not “the deal has a 40% chance of closing.”
It is:

> In this ten-case seed cohort, a 12-month schedule was achieved by four deals
> and was faster than the median terminal timetable. Management should identify
> the transaction-specific facts that justify planning toward the faster part
> of the historical range.

Potential adjustments might include the number of reviewing jurisdictions,
horizontal overlap, remedies anticipated at signing, political sensitivity,
financing constraints, and whether the parties' initial guidance already
allowed for an extended review. Those adjustments must remain explicit. They
should not overwrite the reference distribution or be smuggled into a revised
forecast without a stated rationale.

A practical plan could use separate dates for:

- an operating target or management objective;
- a base planning assumption near the outside-view center;
- a reserve date covering a larger share of historical cases; and
- a long-stop or termination scenario.

In this pilot, 18 months covers 80% of terminal resolutions but only 60% of all
announced agreements as completed transactions. Twenty-four months covers all
observed terminal resolutions, including three terminations. The distinction
should flow into financing, retention, and integration-contingency planning.

## What the analysis does not establish

Several limitations are material:

1. **The seed cohort may be incomplete.** It has not been reconciled against an
   authoritative enumeration of all $20B-plus technology agreements.
2. **Ten cases are few.** Every deal moves the completion rate by ten percentage
   points.
3. **Dependence is unassessed.** The transactions share regulatory authorities,
   jurisdictions, macroeconomic periods, and policy regimes. The absence of a
   registered cluster does not make them ten independent experiments.
4. **The cohort is heterogeneous.** Semiconductor, enterprise-software, gaming,
   social-media, and infrastructure deals may face different review processes.
5. **Terminal-state analysis is not survival analysis.** There are no pending
   cases in this historical seed. A live extension would need right censoring.
6. **No causal adjustment is estimated.** The pilot does not show that size,
   sector, or regulatory opposition causes a specified delay.
7. **The thresholds use simple calendar approximations.** Production tooling
   should define whether a “month” means a calendar-month anniversary or a
   fixed number of days.

These limitations reduce the strength of the forecast; they do not eliminate
the value of seeing that a one-year schedule is historically aggressive in the
observed set.

## Implications for Flyvbjerg

This business example identifies a compact set of general analytical features.

### Empirical quantiles

The revised analysis artifact now reports nearest-rank empirical quantiles in
addition to count, minimum, median, maximum, and mean. The convention is
explicit because nearest-rank P50 need not equal the average-of-middle-values
median in an even sample.

### Target location

`flyvbjerg locate` now positions a target or inside-view estimate against a
locked analysis without changing historical observations. For 365 days it
reports empirical rank 0.4, 102 days below the median, a ratio to median of
0.782, and the case identities above and below the estimate.

### Threshold frequencies

`flyvbjerg threshold` now counts observations satisfying a declared comparison
and reports the denominator, matching and nonmatching identities, missing
subjects, and dependence status. The operation is numeric and generic rather
than acquisition-specific.

### Competing outcomes and stratification

Completion and termination cannot be collapsed. Analyses need transparent
stratification or linked metrics so that duration-to-resolution and
probability-of-completion remain separate.

### Cohort-discovery status

Observation coverage answers whether values are known for registered cases.
Cohort-discovery status answers whether all eligible cases were likely found.
The package should report both without elaborate evidence scoring.

### Dependence not assessed

Flyvbjerg now reports `dependence_status: not_assessed` and a null cluster count
when no dependence groups are supplied, avoiding an affirmative independence
claim.

### Decision brief

The final output should compose rather than invent evidence: target question,
reference class, raw distribution, target position, threshold frequencies,
explicit adjustments, sensitivity, missingness, cohort status, and supported
non-conclusions.

### Audited plotting

Flyvbjerg now generates deterministic SVGs from locked analysis artifacts:

```sh
flyvbjerg plot analysis_01d0cdb1370c4808 \
  --kind ordered --target-value 365 --threshold 365 \
  --output plots/terminal-duration-ordered.svg

flyvbjerg plot analysis_01d0cdb1370c4808 \
  --kind ecdf --target-value 365 --threshold 365 \
  --output plots/terminal-duration-ecdf.svg
```

Each SVG has a JSON receipt identifying the analysis, plot kind, marker values,
creation time, and content hash. Its footer reports sample size, missingness,
dependence status, and quantile convention. Histograms and smoothed densities
are deliberately omitted because their bins or smoothing would be misleading
at n=10.

## Recommended next steps

For the analysis:

1. Audit the seed cases against an independent transaction enumeration.
2. Resolve any missing qualifying deals before calling the completion share a
   base rate.
3. Define dependence groupings or explicitly leave dependence unassessed.
4. Add announcement-era management closing guidance and compare planned with
   realized timing.
5. Add a live or hypothetical target only after its value, overlap,
   jurisdictions, and guidance are specified.

The first package slice—quantiles, `locate`, `threshold`, multi-terminal
derivation, non-assumptive dependence, and audited plotting—is complete. The
next slice should be smaller still:

1. explicit stratification by another accepted metric;
2. cohort-enumeration status distinct from metric coverage; and
3. a composed decision brief.

## Audit and reproduction

The Flyvbjerg workspace stores ten cases, twenty dated events, two metric
definitions, twenty accepted observations, explicit coverage states, and two
analysis sets. The principal artifacts are:

- terminal-state duration (metric v2): `analysis_01d0cdb1370c4808`;
- completion status: `analysis_b32546cda4ca4bd2`.

Reproduce the registered calculations with:

```sh
PYTHONPATH=../../src python -m flyvbjerg validate
PYTHONPATH=../../src python -m flyvbjerg rate analysis_01d0cdb1370c4808
PYTHONPATH=../../src python -m flyvbjerg threshold analysis_01d0cdb1370c4808 --operator le --value 365
PYTHONPATH=../../src python -m flyvbjerg locate analysis_01d0cdb1370c4808 --value 365 --label management_estimate
PYTHONPATH=../../src python -m flyvbjerg plot analysis_01d0cdb1370c4808 --kind ecdf --target-value 365 --threshold 365 --output plots/terminal-duration-ecdf.svg
PYTHONPATH=../../src python -m flyvbjerg plot analysis_01d0cdb1370c4808 --kind ordered --target-value 365 --threshold 365 --output plots/terminal-duration-ordered.svg
PYTHONPATH=../../src python -m flyvbjerg rate analysis_b32546cda4ca4bd2
PYTHONPATH=../../src python -m flyvbjerg next
```

No EDSL Job was built or executed, no paid model call was made, and no
credentials are stored in the simulation.
