# Using reference-class forecasting in practice

This document is the methodological companion to `SPEC.md`. It describes how a
coding agent and a human decision-maker should use Flyvbjerg. It is deliberately
separate from the CLI specification: the method should determine the software,
not be reverse-engineered from its commands.

**Status:** working protocol for simulation and design review, not a claim that
every domain has one settled implementation.

---

## 1. What is established, and what is a Flyvbjerg design choice

The established core of reference-class forecasting is:

1. select a class of comparable past cases;
2. establish the empirical distribution of the outcome being forecast; and
3. locate or adjust the target case against that distribution.

Government implementations use this outside view to correct optimism in cost,
duration, and benefit estimates. They commonly present multiple percentile
levels because the appropriate point depends on the decision and its risk
tolerance. See the [HM Treasury optimism-bias guidance](https://www.gov.uk/government/publications/green-book-supplementary-guidance-optimism-bias),
the [2026 Green Book](https://www.gov.uk/government/publications/the-green-book-appraisal-and-evaluation-in-central-government/the-green-book-2026),
and [Homes England's accessible RCF guidance](https://www.gov.uk/government/publications/optimism-bias-and-contingency-at-homes-england/optimism-bias-and-contingency-at-homes-england-accessible-version).

The following controls are Flyvbjerg product choices intended to make those
three steps auditable when a coding agent assembles the evidence:

- preserve the target description before selecting cases;
- distinguish a candidate universe from accepted class membership;
- preserve the search protocol and search log;
- keep case dossiers independent of later metrics;
- version definitions and metric operationalizations;
- distinguish missing, censored, conflicted, and inapplicable values;
- show several defensible classes and percentiles rather than choosing one
  favorable result;
- store outside-view evidence separately from target-specific adjustment;
- freeze forecasts at an information cutoff.

These are safeguards, not guarantees of an unbiased forecast.

---

## 2. The practical protocol

### Phase A — frame the decision before collecting outcomes

#### A1. Record the target

Describe the target project, decision, or event without estimating its outcome.
Record:

- what is being forecast;
- the decision the forecast will inform;
- the forecast origin or information cutoff;
- the relevant horizon and terminal event;
- the current inside-view estimate, if one already exists;
- which risk attitude or service level matters, if known;
- who owns the final decision.

The target record must not be edited to make a later reference class appear more
or less comparable. Material changes create a new target version.

#### A2. Define the unit of analysis

Write one sentence of the form:

> One case is one ____ beginning at ____ and ending at ____.

This prevents common denominator mistakes: counting phases as projects,
releases as companies, funding rounds as ventures, or repeated forecasts of the
same underlying case as independent observations.

#### A3. Define the estimand

Specify the quantity the forecast is meant to estimate. Examples:

- realized cost relative to the approved baseline at a named decision stage;
- elapsed duration from implementation authorization to production cutover;
- whether a company is operating 36 months after a defined founding event;
- first-year demand relative to the forecast available at approval.

The baseline vintage is part of the metric. A cost estimate made at an early
concept stage is not directly comparable to one made after contracting because
uncertainty changes with project maturity. Official cost-estimating guidance
likewise ties a reference class and confidence level to evidenced scope
maturity, not merely to a nominal stage gate ([UK Government Cost Estimating
Guidance](https://www.gov.uk/government/publications/cost-estimating-guidance/cost-estimating-guidance)).

#### A4. Propose a class hierarchy

Start broad, then state potentially relevant narrower classes before viewing
their outcome distributions:

```text
broad eligible population
├── subclass by project maturity
├── subclass by technical or commercial form
└── subclass by organizational context
```

The governing principle is **as broad as possible, as similar as necessary**.
Homes England's guidance emphasizes both breadth and statistical comparability,
as well as matching the maturity of historical estimates to the target.

Do not begin with a class defined so narrowly that it contains only cases chosen
because they resemble the target's narrative. Do not add a filter after seeing
that it produces a preferred uplift.

### Phase B — define a reproducible collection strategy

The coding agent performs research with its own web, browser, document, and
repository tools. Flyvbjerg does not perform web discovery.

#### B1. Write a search protocol

Before outcomes are coded, record:

- databases, sites, repositories, and document collections to search;
- search terms and synonym families;
- date, geography, language, and source-type limits;
- how candidate cases will be deduplicated;
- how snowballing from references will work;
- the order in which searches will be performed;
- the stopping rule;
- known access and publication biases.

A protocol is not necessarily a formal systematic review. Its purpose is to
make selection understandable and to discourage outcome-driven stopping.

#### B2. Use a stopping rule

Defensible examples include:

- exhaust a closed organizational registry;
- complete every prespecified query and inspect the first N results from each;
- search until a full additional query round yields no new eligible cases;
- reach a prespecified minimum and demonstrate stability under another search
  round;
- stop at a fixed date or research budget and report the resulting incompleteness.

“The sample looked large enough” and “the median stabilized at an acceptable
value” are not stopping rules.

Official implementations sometimes say that roughly 20–30 comparable cases are
enough to get started, with more preferred. That is a practical rule of thumb,
not a universal validity threshold. Homes England states this explicitly; the
appropriate sample also depends on heterogeneity, tail behavior, missingness,
and the decision being supported.

#### B3. Build case dossiers before forcing a schema

For every plausible case, preserve:

- stable identity and aliases;
- why it may qualify;
- primary and secondary sources;
- source files or registered locators;
- dates and version information;
- narrative notes and unresolved questions;
- links to related or possibly duplicate cases.

Case dossiers may be rich and heterogeneous. They exist before metrics are
applied. Supporting material is not itself an observation.

### Phase C — decide membership without using the outcome

#### C1. Apply inclusion criteria

The membership reviewer should use identity, scope, timing, and design facts—not
the value of the outcome being forecast. When practical, conceal outcome fields
during membership review.

Every case receives one state:

- `candidate`: not yet adjudicated;
- `included`: satisfies the approved definition;
- `excluded`: fails a named criterion, with reason and source;
- `indeterminate`: insufficient information to decide.

The current specification uses candidate/included/excluded. Simulation should
test whether `indeterminate` needs to be a first-class membership state rather
than a candidate subtype.

#### C2. Resolve duplicates and dependence

Cases need not be statistically independent merely because their ids differ.
Record shared organizations, programs, vendors, time periods, or causal shocks.
Do not count multiple reports of one project as multiple projects. Where one
program contains several projects, state which level is the unit of analysis.

#### C3. Preserve the candidate funnel

Report counts at each stage:

```text
records found -> candidate cases -> unique cases -> adjudicated cases
              -> included cases -> cases with usable outcome
```

The funnel is evidence about selection. Excluded and indeterminate cases remain
in the workspace.

### Phase D — operationalize and code outcomes

#### D1. Define metrics after learning the case domain, before aggregating

It is acceptable—and often preferable—to assemble dossiers before finalizing
metrics. But the metric must be frozen before inspecting the aggregate
distribution it produces.

Each metric definition states:

- construct and role;
- type, unit, bounds, and allowed values;
- numerator and denominator;
- baseline vintage and terminal event;
- price basis, currency conversion, or normalization when relevant;
- treatment of cancellations, scope changes, and partial delivery;
- source hierarchy;
- calculation formula and rounding;
- missingness and censoring rules.

#### D2. Preserve reported inputs and derived values

If overrun is calculated from planned and actual duration, store all three:

```text
planned_months = 6        [reported observation]
actual_months = 9         [reported observation]
overrun_pct = 50          [derived observation referencing both inputs]
```

Never store only the derived percentage when the inputs are available.

#### D3. Follow a source policy

Prefer sources closest to the underlying event and baseline: official records,
contemporaneous plans, audited reports, contracts, or detailed postmortems.
Secondary summaries can identify cases or corroborate facts but should not
silently override stronger sources.

For conflicts:

1. preserve every source-stamped claim;
2. determine whether the claims use different definitions or vintages;
3. apply the declared source hierarchy;
4. accept one value only with a recorded reason; or
5. leave the metric conflicted and exclude it from the primary distribution.

Model agreement does not resolve a source conflict.

#### D4. Distinguish absence states

- `missing`: the case should have the metric, but no usable value is known;
- `not_applicable`: the metric does not conceptually apply;
- `right_censored`: the terminal event has not occurred by the cutoff;
- `conflicted`: supported claims cannot yet be reconciled;
- `not_found`: a bounded source search did not locate the value;
- `invalid`: a proposed value failed schema or evidence checks.

These states have different implications and must not collapse to null.

### Phase E — establish the distribution

#### E1. Freeze the analysis set

Before calculating results, pin:

- class-definition version;
- metric-definition version;
- membership decisions;
- accepted observation ids;
- information cutoff;
- missingness and censoring policy;
- planned subclasses and sensitivity checks.

#### E2. Report the empirical distribution

For nonnegative adverse outcomes such as cost or schedule overrun, report at
least:

- the raw empirical values or an artifact containing them;
- number eligible and number observed;
- missing, censored, conflicted, and excluded counts;
- minimum, P25, P50, P75, P80, P90, maximum, and mean;
- the quantile convention;
- a plot of the empirical cumulative distribution or uplift curve;
- uncertainty or stability diagnostics appropriate to sample size.

P50 is the outcome not exceeded by 50% of the observed class; P80 is the outcome
not exceeded by 80%. The chosen percentile expresses a risk posture, not model
confidence in the everyday sense. Homes England uses different outputs for
central appraisal, sensitivity, and budgeting, illustrating why Flyvbjerg must
not hard-code one universally “correct” percentile.

#### E3. Treat small samples honestly

Do not rely only on a warning at n < 10. Simulation should test a graduated
policy:

- fewer than 10 usable cases: descriptive evidence, not a stable operational
  uplift;
- 10–19: highly provisional distribution with prominent resampling and
  leave-one-out instability;
- 20–29: potentially usable with strong homogeneity and coverage evidence;
- 30 or more: still requires selection, comparability, and dependence checks.

These are product defaults to debate, not universal statistical laws.

#### E4. Show alternative defensible classes

Compute the broad prespecified class first. Then show prespecified subclasses
and leave-one-out results. A narrower class must not replace the broad result
merely because its forecast is preferred. Report why each subclass is more
comparable, how much data it discards, and how its distribution differs.

### Phase F — convert the distribution into a decision forecast

#### F1. Keep the base estimate clean

When applying an uplift, state what has already been included in the base. An
uplift intended for a base stripped of contingency must not be added on top of a
base that already contains the same risk allowance. HM Treasury and Homes
England guidance explicitly distinguish optimism-bias uplift from separately
modeled or mitigated risk.

#### F2. Choose an operating percentile explicitly

The decision-maker—not the agent and not Flyvbjerg—chooses the operating point.
Record:

- selected percentile or distributional functional;
- the decision it supports;
- consequences of under- and over-estimation;
- stated risk tolerance;
- any policy rule requiring a particular level.

Examples: P50 may be used as a central planning point, while P80 may inform a
budget or stress test. This is context-specific, not a default semantic attached
to those numbers.

#### F3. Separate placement from adjustment

There are two defensible ways to use target-specific evidence:

1. **Placement:** choose where the target lies in the empirical reference
   distribution using prespecified, observable predictors.
2. **Adjustment:** modify the selected outside-view estimate because verified
   target features differ from the class.

Both can reintroduce optimism. Record the unadjusted outside view first. Any
adjustment requires a directional causal rationale, evidence that the feature
differs from the class, an independently reviewable magnitude, and sensitivity
showing the result without the adjustment. Official guidance similarly requires
objective, transparent evidence before reducing an optimism-bias allowance.

#### F4. Freeze and later score the forecast

A forecast snapshot includes the target version, cutoff, class and metric
versions, analysis-set ids, full distribution, selected operating point,
adjustment, and rationale. When the outcome becomes known, score the forecast
against the realized value without rewriting the original snapshot.

Repeated scoring is essential if Flyvbjerg is eventually to say whether a class,
percentile policy, or adjustment practice improves calibration.

---

## 3. Roles and authority

### Coding agent

- executes the recorded search protocol using its own tools;
- builds and enriches case dossiers;
- proposes sources, observations, conflicts, and membership decisions;
- may build EDSL extraction/coding/verification packages through Flyvbjerg;
- explains gaps and uncertainty;
- does not silently choose the final class, percentile, or adjustment.

### Flyvbjerg

- stores versioned definitions and case dossiers;
- validates types, provenance, coverage, and artifact identity;
- preserves candidates, exclusions, conflicts, retries, and failures;
- computes deterministic distributions and sensitivities;
- prevents adjusted forecasts from overwriting the outside view;
- never performs web research or model execution.

### Human decision-maker or named methodological authority

- approves the target framing and class definition;
- accepts consequential membership and evidence decisions;
- approves EDSL plans and separately authorizes paid runs;
- selects the decision percentile or risk policy;
- approves and owns target-specific adjustments;
- owns the resulting decision.

---

## 4. Minimum viable reference-class forecast

A result should not be labeled a completed reference-class forecast unless it
has all of the following:

- a versioned target and information cutoff;
- a defined unit, population, outcome, baseline vintage, and terminal event;
- a recorded collection protocol and stopping status;
- an inspectable candidate funnel and explicit membership decisions;
- source-grounded, typed observations;
- visible missing, censored, conflicted, and excluded cases;
- a pinned empirical distribution and analysis set;
- a stated decision rule for selecting a percentile or estimate;
- the unadjusted outside view;
- any adjustment separately justified and sensitivity-tested.

If the evidence is too sparse, the correct product may be a **reference-class
evidence note** rather than a forecast. Flyvbjerg should make that downgrade easy
and explicit.

---

## 5. Questions for simulated use

The first simulation should test the method, not CLI ergonomics alone:

1. Can we write a target record without leaking a preferred answer into class
   selection?
2. Does a real agent know how broad to make the candidate universe?
3. Can the workspace preserve a reproducible search log without pretending to
   be a systematic-review platform?
4. Do case dossiers accommodate heterogeneous evidence naturally?
5. Can metrics be added after dossier construction without awkward migration?
6. Is `indeterminate` needed as a distinct membership state?
7. Can one source support several cases, and one case several source versions?
8. Are derived metrics and changed baselines represented without ambiguity?
9. Does `gaps` distinguish missing, censored, conflicted, and not applicable?
10. Can the tool show nested reference classes without encouraging subgroup
    shopping?
11. Does a forecast report make P50/P80 semantics and risk ownership clear?
12. Can a later realized outcome score the frozen forecast and its adjustment?

The simulation should keep a friction log. Every workaround, ambiguous command,
manual calculation, or place where conversational memory is required is evidence
for changing `SPEC.md` before implementation.

---

## 6. Initial source notes

- [HM Treasury, Green Book supplementary guidance: optimism bias](https://www.gov.uk/government/publications/green-book-supplementary-guidance-optimism-bias): empirically based adjustments to cost, benefit, and duration estimates, using past or similar projects and transparent treatment of mitigated risks.
- [HM Treasury, The Green Book 2026](https://www.gov.uk/government/publications/the-green-book-appraisal-and-evaluation-in-central-government/the-green-book-2026): current UK appraisal context for explicit optimism-bias adjustments and organization-specific historical forecast errors.
- [Homes England, Optimism Bias and Contingency](https://www.gov.uk/government/publications/optimism-bias-and-contingency-at-homes-england/optimism-bias-and-contingency-at-homes-england-accessible-version): practical three-step RCF account, breadth-versus-similarity principle, maturity matching, sample-size rule of thumb, percentile semantics, and worked use of P50/P80/P-mean.
- [UK Government, Cost Estimating Guidance](https://www.gov.uk/government/publications/cost-estimating-guidance/cost-estimating-guidance): warnings about sampling, survivorship, optimism, reference-class choice, and matching estimate maturity.
- [Flyvbjerg, “From Nobel Prize to Project Management: Getting Risks Right”](https://arxiv.org/abs/1302.3642): theoretical motivation for the outside view and its role in addressing optimism bias and strategic misrepresentation.
- [Flyvbjerg, Hon, and Fok, “Reference Class Forecasting for Hong Kong's Major Roadworks Projects”](https://arxiv.org/abs/1710.09419): applied construction and validation of cost and schedule reference distributions.

These sources are strongest for public projects and cost/schedule forecasting.
Applying the tool to startups, product launches, scientific experiments, or
other domains requires domain-specific operational definitions and should not
inherit infrastructure defaults uncritically.
