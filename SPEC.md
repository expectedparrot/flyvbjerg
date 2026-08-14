# flyvbjerg — specification

An agent-first CLI for assembling evidence about comparable cases and turning
accepted observations into auditable reference-class distributions.

The coding agent using Flyvbjerg performs the research. Flyvbjerg does not
search the web, browse, fetch, scrape, or decide what to investigate. It gives
the agent a durable place to register raw material, resolve that material into
cases and events, apply metrics later, and calculate outside-view evidence.

Flyvbjerg uses native EDSL objects for optional batch extraction, coding, or
verification of material already registered in the workspace. EDSL owns model
execution, credentials, caching, providers, and `.ep` serialization.

**Version:** 0.1 · **Language:** Python ≥3.11 · **Primary dependencies:**
`edsl`, `typer`, `rich`, `pyyaml`

---

## 1. Product boundary

### 1.1 The coding agent researches

The agent uses its own tools to:

- discover candidate sources and cases;
- search websites, filings, transcripts, repositories, and documents;
- retrieve material it is permitted to preserve;
- assess source relevance and credibility;
- decide what to register with Flyvbjerg;
- propose entities, events, relationships, and observations.

Flyvbjerg can show gaps and unprocessed material, but it never performs these
research actions itself.

### 1.2 Flyvbjerg organizes evidence

Flyvbjerg owns:

- versioned prospective targets and readiness gaps;
- the intake of sources, captures, and unprocessed items;
- provenance and content hashes;
- triage state;
- persistent case identities and rich case dossiers;
- events involving one or more cases;
- typed relationships among cases;
- class-level metric definitions;
- case-level observations and evidence decisions;
- deterministic distributions, coverage, and exports;
- optional EDSL processing plans, artifacts, audits, and ingestion;
- versioned forecasts derived from accepted evidence.

### 1.3 EDSL processes bounded material

For source material the agent has already registered, Flyvbjerg may construct
native EDSL `ScenarioList`, `Survey`, `AgentList`, `ModelList`, and `Jobs`
objects. The user inspects and approves those objects, then runs them separately
with the `ep` CLI. Flyvbjerg later audits and ingests native `Results` objects.

Flyvbjerg never creates an EDSL prompt that asks a model to browse the web or
acquire sources.

```text
coding agent researches with its own tools
    ↓
Flyvbjerg intake: sources → captures → candidate items
    ↓
triage: cases ↔ relationships ↔ events ↔ candidate claims
    ↓
metrics applied as observations
    ↓
accepted evidence → distributions → forecasts
```

---

## 2. Design principles

**Intake precedes interpretation.** A document can matter before the agent knows
which case it belongs to. Register it once, then link it to zero, one, or many
cases during triage.

**A case is a dossier, not a row.** Cases have stable identity, editable notes,
supporting material, relationships, lifecycle events, observations, and
decisions.

**Products and events are different things.** A persistent entity may be
announced, enter beta, roll out, be bundled, renamed, expanded, deprecated, or
absorbed into another product. Those are events, not new copies of the case.

**Metrics come later.** Agents may assemble rich case dossiers before deciding
what can be measured consistently. Metric definitions belong to a class;
observations apply those definitions to cases.

**Dependence is part of the evidence model.** Distinct cases can share a launch
program, policy regime, organization, or source process. Analyses disclose those
clusters rather than assuming every case is independent.

**Claims are not facts merely because they parse.** Extracted claims and model
outputs enter as candidates. Only accepted observations enter distributions.

**Absence has meaning.** `not_researched`, `not_disclosed`, `not_applicable`,
`censored`, `conflicted`, and `invalid` are not interchangeable nulls.

**The filesystem is the evidence ledger.** Records and manifests remain useful
without the CLI and diff cleanly in git. A future index is disposable.

**External execution is explicit.** Building an EDSL package does not authorize
model calls or spending.

---

## 3. Core model

### 3.1 Workspace

A workspace contains one or more collections. Commands walk upward from the
current directory to find `.flyvbjerg/workspace.json`. There is no hidden global
active project.

### 3.2 Collection

A **collection** is a research corpus and candidate population, such as
“Upwork product launches.” It owns intake material, cases, and metric
definitions.

The term `collection` is deliberately broader than `reference class`. A corpus
may be exploratory or too heterogeneous to support a forecast. It becomes an
approved reference class only after its unit, membership criteria, and relevant
metric semantics are defined.

Collection states:

- `exploratory`: collecting and resolving material;
- `defined`: unit and membership rules are versioned;
- `approved`: suitable for a stated analysis;
- `archived`: retained but no longer active.

### 3.3 Target

A **target** is the prospective project, product, organization, event, or
decision to which an outside view may eventually be applied. Targets can exist
during exploration, before a valid reference class, metric, analysis set, or
forecast exists.

```json
{
  "target_id": "prospective-mlb-expansion-team",
  "name": "Prospective MLB expansion franchise",
  "status": "underspecified",
  "forecast_origin": "2026-08-11",
  "terminal_event": "first regular-season MLB game",
  "known": {"league": "MLB", "kind": "expansion"},
  "unknown": ["city", "stadium_plan", "ownership_group", "launch_year"],
  "decision_to_inform": null
}
```

Target states are `draft`, `underspecified`, `ready_for_analysis`, and
`archived`. `target gaps` reports missing facts without filling them. A target
revision creates a new version; it never changes a forecast already pinned to an
earlier target version.

A target may guide collection and comparability review, but target attributes
do not automatically filter a reference class. Filters and target placement
remain explicit analysis or forecast decisions. Target-specific adjustment is
unavailable until an analysis set exists.

### 3.4 Source

A **source** is the bibliographic identity of an information resource: a press
release, earnings call, filing, webpage, dataset, email, report, or interview.

```json
{
  "source_id": "src_01K...",
  "kind": "press_release",
  "title": "Upwork Updates: Spring 2024",
  "publisher": "Upwork Inc.",
  "published": "2024-04-30",
  "url": "https://...",
  "retrieved": "2026-08-11T15:20:00Z",
  "restrictions": null
}
```

A source is registered once at collection level and may support many cases,
events, and observations.

### 3.5 Capture

A **capture** is a preserved representation of a source at a point in time: PDF,
HTML, Markdown, transcript, spreadsheet, image, JSON, or another file.

```json
{
  "capture_id": "cap_01K...",
  "source_id": "src_01K...",
  "original_name": "spring-2024.pdf",
  "path": "intake/captures/cap_01K.../spring-2024.pdf",
  "media_type": "application/pdf",
  "sha256": "...",
  "captured_at": "2026-08-11T15:22:00Z",
  "method": "agent_supplied"
}
```

Flyvbjerg copies agent-supplied files into managed storage by default. It does
not download a registered URL. URL-only sources are allowed but visibly lack a
durable capture.

A source may have several captures: original HTML, official PDF, extracted text,
or a later version. Derivatives point to their parent capture and record the
producer and transformation.

### 3.6 Intake item

An **intake item** is a bounded piece of collected information not yet fully
resolved into the domain model. It may be created manually or extracted from a
capture.

```json
{
  "item_id": "item_01K...",
  "source_id": "src_01K...",
  "capture_id": "cap_01K...",
  "kind": "candidate_event",
  "text": "Portfolio, now available in beta...",
  "locator": {"page": 3, "heading": "New Resources for Freelancers"},
  "status": "untriaged",
  "proposed_names": ["Portfolio"],
  "created_by": {"kind": "agent", "name": "codex"},
  "created_at": "2026-08-11T15:25:00Z"
}
```

Kinds are open but begin with:

- `candidate_entity`;
- `candidate_event`;
- `candidate_claim`;
- `relationship_hint`;
- `context`;
- `unknown`.

Statuses are:

- `untriaged`;
- `resolved`;
- `irrelevant`;
- `duplicate`;
- `deferred`.

Resolution is append-only. An item can resolve to several records, such as a
release event involving five products. Items remain preserved after resolution.

### 3.7 Case

A **case** is a persistent entity that may become a member of a reference
class. Examples include a product, project, company, experiment, or policy.

```json
{
  "case_id": "upwork-chat-pro",
  "name": "Upwork Chat Pro",
  "entity_type": "integrated_application",
  "aliases": [],
  "membership": "candidate",
  "created_from": ["item_01K..."],
  "created_at": "2026-08-11T15:30:00Z"
}
```

Each case owns a directory containing:

- immutable identity records;
- optional editable `README.md` narrative;
- case-specific managed materials;
- relationships;
- events;
- observations;
- membership and evidence decisions.

Membership states are `candidate`, `included`, `excluded`, and
`indeterminate`. Exclusion and inclusion require a decision record. A candidate
may exist before the collection has an approved membership definition.

### 3.8 Relationship

A **relationship** is a typed, directional link between two cases.

Initial relationship types:

- `feature_of` / `has_feature`;
- `powered_by` / `powers`;
- `bundled_into` / `includes`;
- `replaces` / `replaced_by`;
- `renamed_to` / `renamed_from`;
- `successor_to` / `predecessor_of`;
- `variant_of`;
- `part_of_program`;
- `possibly_same_as`.

Relationships require a source or intake-item provenance. The inverse is
derived, not independently stored. Relationships do not imply shared membership
or metric values.

### 3.9 Group

A **group** is a named, non-case collection of cases used by the company or the
researcher: a product portfolio, program, bundle, cohort, or business line.

```json
{
  "group_id": "ads-and-monetization",
  "kind": "portfolio",
  "name": "Ads & Monetization",
  "membership_events": ["gevt_01K..."],
  "created_from": ["item_01K..."]
}
```

Group membership is temporal and append-only. `member_added` and
`member_removed` records state the case, effective date or period, source, and
provenance. This matters when a disclosed portfolio changes composition.

Groups are not cases and do not enter a reference class merely because their
members do. A claim or observation scoped to a group never propagates to its
members. Allocation requires an explicit, versioned allocation method and a new
derived claim or observation; implicit allocation is prohibited.

### 3.10 Event

An **event** records something that happened at a point or interval and can
involve one or many cases.

```json
{
  "event_id": "evt_01K...",
  "type": "beta_announced",
  "workstream": "product_availability",
  "date": "2023-11-06",
  "date_precision": "day",
  "subjects": [{"kind": "case", "id": "upwork-chat-pro"}],
  "source_id": "src_01K...",
  "item_ids": ["item_01K..."],
  "changes": [
    {"field": "availability_stage", "before": null, "after": "beta_waitlist"}
  ],
  "note": "Waitlist opened; selected-user rollout planned."
}
```

Initial event vocabulary is intentionally extensible:

- `announced`;
- `beta_announced`;
- `waitlist_opened`;
- `rollout_started`;
- `generally_available`;
- `distribution_changed`;
- `bundled`;
- `capability_expanded`;
- `renamed`;
- `deprecated`;
- `discontinued`;
- `outcome_disclosed`.

An optional `workstream` classifies parallel parts of a launch or program, such
as `governance`, `venue`, `finance`, `brand`, `commercial`, `operations`,
`staffing`, `regulatory`, or `product_availability`. Workstream vocabulary is
collection-defined and does not change event identity.

Events are collection-level records because one release event may involve many
cases. Case directories contain generated or stored references to their events,
not duplicated event bodies.

Events may describe structured changes to prices, packages, terms, names,
availability, or group membership. A change can record exact before/after
values, directional changes such as `increased`, or explicitly unknown values.
Persistent offerings remain cases; material interventions affecting them remain
events.

### 3.11 Claim

A **claim** is a structured statement supported by a source but not necessarily
ready to become a metric observation. Claims are the durable bridge between
intake and measurement.

```json
{
  "claim_id": "claim_01K...",
  "claim_kind": "reported_measurement",
  "scope": {"kind": "case", "ids": ["connects-monetization"]},
  "period": "2024Q2",
  "construct": "revenue growth year over year",
  "value": 81,
  "unit": "percent",
  "source_id": "src_q2_2024",
  "capture_id": "cap_q2_2024",
  "locator": {"heading": "Ads & Monetization"},
  "status": "candidate",
  "limitations": []
}
```

Claim scope kinds are:

- `case`;
- `event`;
- `group`;
- `collection`;
- `multi_subject`.

Claim kinds begin with:

- `reported_measurement`;
- `management_attribution`;
- `causal_estimate`;
- `qualitative_assessment`;
- `guidance`;
- `forward_looking_expectation`.

Attribution claims record `causal_strength`, such as `not_isolated`,
`observational`, `quasi_experimental`, or `experimental`, plus the subjects and
claimed outcome. Management attribution is useful evidence but never becomes an
isolated causal effect by default.

Claims may be numeric, categorical, or narrative. Statuses are `candidate`,
`accepted`, `rejected`, `conflicted`, and `superseded`. An accepted claim is
still not an observation until it is promoted against a compatible metric.

An intake item may resolve to zero, one, or many claims. Claims preserve company
and portfolio disclosures that are useful even when no cross-case metric is
possible.

### 3.12 Metric

A **metric** is a versioned class-level measurement definition.

```json
{
  "metric_id": "daily-active-user-growth-qoq",
  "version": 1,
  "kind": "numeric",
  "unit": "percent",
  "role": "outcome",
  "description": "Quarter-over-quarter change in product daily active users",
  "subject_kinds": ["case"],
  "eligible_entity_types": ["integrated_application"],
  "time_basis": "first fully reported quarter after general availability",
  "period_basis": "fiscal_quarter",
  "comparison_basis": "previous_fiscal_quarter",
  "allocation_policy": "no_implicit_allocation",
  "required_context": [],
  "missing_context_policy": "warn",
  "bounds": {"min": -100, "max": null},
  "missingness_policy": "not_disclosed is not zero"
}
```

Metrics can be added after cases, sources, events, and relationships exist.
Adding a metric never rewrites a case. Metric revisions create new versions and
stale only dependent analyses and processing plans.

Metric applicability is part of validation. Subject kind, entity or group type,
period basis, comparison basis, and allocation policy prevent numerically
similar but semantically incompatible claims from sharing a distribution.

Metrics may declare contextual fields required for interpretation, such as
venue capacity and number of home dates for attendance. `missing_context_policy`
is `allow`, `warn`, or `error`. Context requirements do not alter the underlying
observation; they determine analysis readiness and are reported case by case.

A metric may also define a deterministic derivation. The first derivation kind
is an interval between two events:

```json
{
  "metric_id": "award-to-inaugural-game-days",
  "version": 1,
  "kind": "numeric",
  "unit": "days",
  "subject_kinds": ["case"],
  "derivation": {
    "kind": "event_interval",
    "start_event_type": "franchise_awarded",
    "end_event_type": "inaugural_regular_season_game",
    "selection": "unique_per_case",
    "date_precision_required": "day"
  }
}
```

Derived observations reference the exact input event or observation ids and the
metric version. Ambiguous event selection, insufficient date precision, or
missing endpoints produces a gap, never a guessed duration.

An interval derivation may instead declare `end_event_types` and
`selection: first_terminal_event`. The derived observation preserves the chosen
`terminal_event_type`; completion, cancellation, termination, and other terminal
states therefore remain distinguishable.

### 3.13 Observation

An **observation** applies one metric version to one subject. A subject may be a
case, event, or group only when the metric permits that subject kind.

```json
{
  "observation_id": "obs_01K...",
  "subject": {"kind": "case", "id": "upwork-chat-pro"},
  "metric": {"id": "daily-active-user-growth-qoq", "version": 1},
  "period": "2024Q2",
  "value": 68,
  "source_id": "src_q2_2024",
  "capture_id": "cap_q2_2024",
  "locator": {"heading": "Artificial Intelligence"},
  "method": "reported",
  "status": "candidate",
  "provenance": {"kind": "claim", "id": "claim_01K..."}
}
```

Observation statuses are `candidate`, `accepted`, `rejected`, and
`superseded`. Methods begin with `reported`, `calculated`, `human_coded`, and
`model_coded`. Calculated observations reference their input observation ids.
Promoted observations reference their originating claim. Promotion validates
scope, period basis, construct, unit, and metric applicability; it never changes
the claim.

Only eligible subjects with accepted observations enter a distribution. A
case-level reference distribution still requires included cases; event and group
analyses declare their own membership unit explicitly.

### 3.14 Coverage state

For every relevant subject/metric pair, Flyvbjerg can derive or store one
coverage state:

- `observed`;
- `not_researched`;
- `not_disclosed`;
- `not_found_in_reviewed_sources`;
- `not_applicable`;
- `censored`;
- `conflicted`;
- `invalid`.

`not_researched` is the default when no observation or explicit coverage
decision exists. A coverage decision must cite its scope; for example,
`not_found_in_reviewed_sources` names the captures actually reviewed.

### 3.15 Analysis set and forecast

An **analysis set** freezes a collection-definition version, metric version,
membership decisions, accepted observation ids, filters, cutoff, and absence
policy. Distributions are computed from analysis sets rather than from mutable
“current state.”

An analysis set also records dependence clusters. A cluster is a group or an
explicit set of subjects that share a program, intervention, organization,
source process, or other dependence relevant to inference.

```json
{
  "dependence_clusters": [
    {"group_id": "mlb-expansion-1993", "reason": "shared expansion program"},
    {"group_id": "mlb-expansion-1998", "reason": "shared expansion program"}
  ]
}
```

Flyvbjerg always reports subject count. It reports cluster count only when
dependence clusters have been explicitly supplied. Otherwise
`dependence_status` is `not_assessed` and `n_clusters` is null; distinct case ids
do not imply independent observations. V0.1 warns and exposes
leave-one-cluster-out sensitivity; later estimators may model dependence
directly.

Numeric distributions include nearest-rank empirical quantiles. Read-only
`locate` operations position a proposed target value against the locked
distribution, while `threshold` operations report exact matching counts,
denominators, subject identities, missing subjects, and dependence status.
`plot` renders an ordered case view or empirical cumulative distribution as a
deterministic SVG. Each plot has a JSON receipt identifying the locked analysis,
marker values, and output hash. Plot annotations expose sample size,
missingness, dependence status, and quantile convention.

A **forecast** applies an analysis-set distribution to a target. The unadjusted
outside view and any target-specific adjustment are separate stored objects.
Forecasting is useful but not required for the first vertical slice.

---

## 4. Filesystem layout

```text
.flyvbjerg/
  workspace.json
  targets/<target-id>/
    v1.json
    v2.json
  collections/<collection-id>/
    collection.json
    definition.md
    intake/
      sources/<source-id>.json
      captures/<capture-id>/
        capture.json
        <preserved file>
      items/<item-id>.json
      resolutions/<resolution-id>.json
    claims/<claim-id>.json
    cases/<case-id>/
      case.json
      README.md
      materials/
      material-manifest.jsonl
      relationships/<relationship-id>.json
      observations/<observation-id>.json
      decisions/<decision-id>.json
    groups/<group-id>/
      group.json
      membership/<membership-event-id>.json
    events/<event-id>.json
    metrics/<metric-id>/
      v1.json
      v2.json
    analysis-sets/<analysis-id>/
      analysis.json
      distribution.json
    runs/<run-id>/
      plan.json
      prompts.jsonl
      jobs.ep
      models.ep
      jobs.audit.json
      results/<result-set-id>.results.ep
      results.audit.json
      candidates.jsonl
      ingestion.json
      manifest.json
    forecasts/<forecast-id>/
      forecast.json
      outside-view.json
      adjustment.json
      report.md
  schemas/
  receipts/
```

Stored JSON uses canonical UTF-8 serialization for hashing. Manifests use
workspace-relative paths and record schema version, SHA-256, producer command,
created time, and logical input hashes.

Targets are workspace-level because several collections may inform the same
decision. Target versions, identity, intake, resolution, claim,
group-membership, event, relationship, observation, decision, run, and
analysis-set records are immutable. Corrections use new records and explicit
`supersedes` relationships. `README.md` is editable narrative and never counts
as structured evidence by itself.

Writes use temporary files plus atomic rename. A workspace lock serializes id
allocation and mutations. The directory tree is authoritative; indexes and
caches are rebuildable.

---

## 5. Agent output contract

Every command prints exactly one versioned JSON envelope to stdout by default.
Logs and progress go to stderr. `--human` is an opt-in Rich rendering and must
not be used by agents.

```json
{
  "schema_version": "1.0",
  "command": "flyvbjerg intake next upwork-product-launches",
  "status": "ok",
  "argv": ["intake", "next", "upwork-product-launches"],
  "data": {},
  "artifacts": [],
  "warnings": [],
  "errors": [],
  "next_steps": []
}
```

Errors contain stable `code`, `message`, `hint`, and optional `context`.
Artifacts contain path, role, media type, SHA-256, and manifest path.

Each structured next action contains:

- `id`;
- `purpose`;
- `command`;
- `mutates_state`;
- `requires_network`;
- `requires_user_approval`.

Exit codes:

- `0`: success, including idempotent no-op;
- `1`: usage or validation error;
- `2`: integrity or provenance error;
- `3`: incomplete external results;
- `4`: dependency or system failure.

---

## 6. CLI surface

Exact flags and defaults live in `--help`. This section defines the conceptual
surface, not a second parser specification.

### 6.1 Orientation

```bash
flyvbjerg init [PATH]
flyvbjerg status
flyvbjerg next [COLLECTION]
flyvbjerg guide [TOPIC]
flyvbjerg capabilities
flyvbjerg doctor
flyvbjerg validate [--collection ID] [--run ID]
flyvbjerg describe PATH
```

`next` derives state from artifacts. It prioritizes target gaps, untriaged
intake, unresolved identity conflicts, indeterminate membership,
metric-and-context gaps, unaudited EDSL results, and stale analysis sets.

### 6.2 Collections

```bash
flyvbjerg collection new ID --title TEXT
flyvbjerg collection list
flyvbjerg collection show ID
flyvbjerg collection define ID --definition FILE
flyvbjerg collection approve ID
flyvbjerg collection archive ID
```

Collection approval is analysis-specific: it confirms a versioned unit and
membership policy. Exploratory collections can still hold intake and cases.

### 6.3 Targets

```bash
flyvbjerg target create ID --name TEXT [--from FILE]
flyvbjerg target list
flyvbjerg target show ID [--version N]
flyvbjerg target revise ID --from FILE
flyvbjerg target gaps ID [--version N]
flyvbjerg target archive ID
```

Targets are workspace-level, versioned descriptions of the decision or proposed
undertaking. They may begin underspecified. Creating a target does not create a
collection, select reference cases, or imply an adjustment. `target gaps` is a
read-only readiness report; research and case construction remain explicit.

### 6.4 Intake

```bash
flyvbjerg source add COLLECTION --url URL [--title TEXT] [--kind KIND]
flyvbjerg source add COLLECTION --file PATH [--url URL] [--title TEXT]
flyvbjerg source list COLLECTION
flyvbjerg source show COLLECTION SOURCE

flyvbjerg capture add COLLECTION SOURCE --file PATH [--parent CAPTURE]
flyvbjerg capture list COLLECTION [--source SOURCE]
flyvbjerg capture show COLLECTION CAPTURE

flyvbjerg intake add COLLECTION --source SOURCE [--capture CAPTURE] \
  --kind KIND --text TEXT [--locator JSON] [--proposed-name TEXT ...]
flyvbjerg intake import COLLECTION --input items.jsonl
flyvbjerg intake list COLLECTION [--status STATUS] [--kind KIND]
flyvbjerg intake next COLLECTION
flyvbjerg intake show COLLECTION ITEM
flyvbjerg intake defer COLLECTION ITEM --reason TEXT
flyvbjerg intake reject COLLECTION ITEM --reason TEXT
```

`source add --file` is convenience for registering a source and its first
capture. Flyvbjerg never follows or downloads `--url`.

### 6.5 Triage and entity resolution

```bash
flyvbjerg intake resolve-case COLLECTION ITEM --new-case ID --name TEXT
flyvbjerg intake resolve-case COLLECTION ITEM --case CASE
flyvbjerg intake resolve-event COLLECTION ITEM --type TYPE --case CASE ... \
  [--date DATE] [--date-precision PRECISION]
flyvbjerg intake resolve-relationship COLLECTION ITEM \
  --from CASE --type TYPE --to CASE
flyvbjerg intake resolve-claim COLLECTION ITEM --scope-kind KIND \
  --scope ID ... --claim-kind KIND [--construct TEXT] [--value JSON] [--unit UNIT]
flyvbjerg intake mark-duplicate COLLECTION ITEM --of ITEM
```

One item may have several resolutions. Resolving it does not delete it. Claims
normally remain metric-free until a suitable definition exists.

### 6.6 Cases, materials, events, and relationships

```bash
flyvbjerg case add COLLECTION --id ID --name TEXT [--type TYPE]
flyvbjerg case import COLLECTION --input cases.jsonl
flyvbjerg case list COLLECTION [--membership STATE] [--type TYPE]
flyvbjerg case show COLLECTION CASE
flyvbjerg case note COLLECTION CASE [--write-template]
flyvbjerg case material add COLLECTION CASE --file PATH [--source SOURCE]
flyvbjerg case material list COLLECTION CASE
flyvbjerg case decide COLLECTION CASE \
  --include|--exclude|--indeterminate --reason TEXT [--source SOURCE]

flyvbjerg event add COLLECTION --type TYPE --case CASE ... \
  [--workstream WORKSTREAM] [--date DATE] --source SOURCE \
  [--item ITEM ...] [--change JSON ...]
flyvbjerg event list COLLECTION [--case CASE] [--type TYPE] \
  [--workstream WORKSTREAM]
flyvbjerg event show COLLECTION EVENT

flyvbjerg relationship add COLLECTION --from CASE --type TYPE --to CASE \
  --source SOURCE [--item ITEM]
flyvbjerg relationship list COLLECTION [--case CASE] [--type TYPE]

flyvbjerg group create COLLECTION ID --kind KIND --name TEXT
flyvbjerg group list COLLECTION [--kind KIND]
flyvbjerg group show COLLECTION GROUP [--at DATE|PERIOD]
flyvbjerg group add-member COLLECTION GROUP --case CASE \
  [--effective DATE|PERIOD] --source SOURCE
flyvbjerg group remove-member COLLECTION GROUP --case CASE \
  [--effective DATE|PERIOD] --source SOURCE
```

`case show` composes identity, narrative path, source links, relationships,
events, membership history, observations, and coverage states without copying
collection-level records.

### 6.7 Claims

```bash
flyvbjerg claim add COLLECTION --scope-kind KIND --scope ID ... \
  --claim-kind KIND --source SOURCE [--capture CAPTURE] [--locator JSON] \
  [--period PERIOD] [--construct TEXT] [--value JSON] [--unit UNIT] \
  [--causal-strength STRENGTH] [--limitation TEXT ...]
flyvbjerg claim list COLLECTION [--scope-kind KIND] [--scope ID] \
  [--claim-kind KIND] [--status STATUS]
flyvbjerg claim show COLLECTION CLAIM
flyvbjerg claim decide COLLECTION CLAIM --accept|--reject --reason TEXT
flyvbjerg claim supersede COLLECTION CLAIM --with CLAIM --reason TEXT
flyvbjerg claim promote COLLECTION CLAIM --metric ID [--metric-version N]
```

Promotion creates a candidate observation and returns applicability failures
without modifying the claim. A group-scoped claim cannot promote to a case-only
metric. A `management_attribution` claim cannot promote to a causal-effect
metric unless the metric explicitly permits that claim kind and causal strength.

### 6.8 Metrics, observations, and coverage

```bash
flyvbjerg metric add COLLECTION ID --kind KIND --role ROLE [OPTIONS]
flyvbjerg metric revise COLLECTION ID [OPTIONS]
flyvbjerg metric list COLLECTION
flyvbjerg metric show COLLECTION ID [--version N]
flyvbjerg metric derive COLLECTION ID [--metric-version N] \
  [--subject ID ...] [--dry-run]

flyvbjerg observation add COLLECTION --subject-kind CASE|EVENT|GROUP \
  --subject ID --metric ID [--metric-version N] \
  --value JSON --source SOURCE [--capture CAPTURE] [--locator JSON] \
  [--period PERIOD] [--method METHOD] [--claim CLAIM]
flyvbjerg observation list COLLECTION [--subject-kind KIND] [--subject ID] \
  [--metric ID] [--status STATUS]
flyvbjerg observation decide COLLECTION OBS --accept|--reject --reason TEXT
flyvbjerg observation supersede COLLECTION OBS --with OBS --reason TEXT

flyvbjerg coverage set COLLECTION --subject-kind KIND --subject ID \
  --metric ID --state STATE \
  --reason TEXT [--source SOURCE] [--capture CAPTURE ...]
flyvbjerg coverage show COLLECTION [--metric ID] \
  [--subject-kind KIND] [--subject ID]
flyvbjerg gaps COLLECTION [--metric ID]
flyvbjerg conflicts COLLECTION [--metric ID]
```

An observation without an explicit decision is a candidate. Manual writes do
not bypass this rule by default; `--accept` is an explicit convenience flag that
records a separate acceptance decision in the same invocation.

`metric derive` resolves the inputs declared by the metric version and reports
missing inputs, ambiguity, and insufficient precision. Unless `--dry-run` is
used, successful derivations create candidate observations that cite their exact
input ids. The command never chooses among ambiguous events.

### 6.9 Optional EDSL processing

```bash
flyvbjerg process plan COLLECTION --name NAME --mode extract|code|verify \
  --capture CAPTURE ... [--case CASE ...] [--metric METRIC ...]
flyvbjerg process show RUN
flyvbjerg process approve RUN
flyvbjerg process build RUN --output RUN_DIR
flyvbjerg process inspect RUN
flyvbjerg process register-results RUN --input RESULTS_EP [--jobs JOBS_EP]
flyvbjerg process audit RUN [--result-set ID]
flyvbjerg process ingest RUN [--result-set ID] [--allow-partial]
flyvbjerg process retry RUN --failures AUDIT_JSON --name NAME
```

Processing plans are bounded by registered capture ids. `build` refuses a plan
that contains a URL but no capture. Modes mean:

- `extract`: propose intake items or structured claims from captures;
- `code`: apply an approved rubric to existing items or claims;
- `verify`: independently assess an existing candidate against named captures.

`build` produces loadable native `jobs.ep` and `models.ep`, stable scenario and
result keys, and a manifest. It returns but never executes:

```bash
ep inspect RUN_DIR/jobs.ep
ep jobs cost RUN_DIR/jobs.ep
ep run RUN_DIR/jobs.ep --output run.results.ep
```

Production builds require approved plans. Paid or local model execution requires
separate user authority. `--allow-unapproved` creates a visibly diagnostic
package and still does not authorize execution.

Audit compares the exact originating Jobs and Results objects and checks:

- run, source, capture, scenario, question, model, and result identities;
- expected coverage and stable keys;
- nulls, duplicates, exceptions, malformed structured answers;
- locators and quotations against the registered capture;
- claim scope, kinds, attribution strength, metric applicability, types, and bounds;
- conflicting results across models or retries.

Malformed or missing responses are failures, not negative findings. Ingestion
preserves them and creates only intake items, claims, or observations with
candidate status. It is idempotent by stable result
key and fails closed on incomplete coverage unless `--allow-partial` is explicit.

### 6.10 Analysis and forecasting

```bash
flyvbjerg analysis create COLLECTION --name NAME --metric ID \
  [--target TARGET] [--target-version N] [--where EXPR] [--cutoff DATE] \
  [--absence-policy POLICY] [--cluster-group GROUP ...]
flyvbjerg analysis show ANALYSIS
flyvbjerg rate ANALYSIS
flyvbjerg sensitivity ANALYSIS \
  --leave-one-out|--leave-one-cluster-out|--by FIELD
flyvbjerg export ANALYSIS --format json|csv|md

flyvbjerg forecast new ANALYSIS --name NAME --target TARGET \
  [--target-version N]
flyvbjerg forecast adjust FORECAST --value JSON --rationale FILE --source SOURCE
flyvbjerg forecast report FORECAST --format json|md|html
```

Creating an analysis set validates that all included cases have an explicit
coverage state for the selected metric. `rate` uses only accepted observations
and reports:

- eligible and observed counts;
- every absence-state count and affected case ids;
- definition and metric versions;
- exact observation ids;
- empirical values or a linked artifact;
- numeric distribution statistics or categorical counts;
- quantile convention;
- small-sample and dependence warnings.

It also reports required-context coverage, subject count, dependence-cluster
count, cluster membership, and leave-one-cluster-out sensitivity. The selected
metric's missing-context policy determines whether incomplete context is
allowed, warned on, or blocks creation.

Analysis also pins subject kind, entity/group type, group membership as of the
cutoff, period and comparison basis, and allocation policy. It refuses implicit
conversion between company, group, event, and case scope. Portfolio results are
never copied to members. Mixed subject or entity levels require an explicitly
compatible metric and otherwise fail validation.

When an analysis names a target, it pins the target version but does not apply a
target-specific adjustment. A later target revision makes that relationship
visible; it does not mutate the frozen analysis.

A forecast pins its analysis set. An adjustment never overwrites the outside
view. Forecasting and forecast scoring may ship after the first vertical slice.

---

## 7. Agent workflows

### 7.1 Ordinary research loop

```text
1. flyvbjerg intake next / gaps --json
2. Agent researches using its own tools.
3. Agent registers sources and captures.
4. Agent creates bounded intake items with locators.
5. Agent resolves items into cases, events, relationships, or claims.
6. Agent records unresolved identity and evidence questions explicitly.
7. Human or agent applies approved membership and evidence decisions.
8. Repeat until the chosen scope is adequately covered.
```

No EDSL job is required for this loop.

### 7.2 EDSL-assisted loop

```text
1. Select registered captures and a bounded extraction/coding task.
2. Build and approve a processing plan.
3. Build native EDSL packages.
4. Inspect Jobs and estimated cost.
5. Obtain explicit authority and run with ep.
6. Register and audit Results against Jobs and captures.
7. Ingest valid outputs as intake items, candidate claims, or candidate observations.
8. Triage claims and accept or promote evidence explicitly.
```

### 7.3 Context recovery

After every material stage, the agent runs `flyvbjerg next`. The bundled
`flyvbjerg guide` is the durable lifecycle source of truth; repository
`AGENTS.md` should be only a short bootstrap pointer.

---

## 8. Safety and integrity

- EDSL owns authentication through `ep auth`, profiles, caches, execution, and
  remote result retrieval. Flyvbjerg never prints or stores credentials.
- Never run `ep run` merely because Flyvbjerg built jobs.
- Preserve exact Jobs, ModelList, Results, retries, audits, and merge provenance.
- Never commit `.env`, `.edsl/profiles/`, confidential captures, licensed data,
  or provider responses that cannot be redistributed.
- Never equate `not_disclosed`, `not_researched`, malformed, or missing with a
  negative or zero outcome.
- Never count a portfolio-level disclosure as a product-level observation
  without an explicit defensible allocation method.
- Never treat management attribution as an isolated causal effect. Preserve its
  stated scope and causal strength.
- Never promote a claim when its scope, entity level, period basis, comparison
  basis, unit, or claim kind is incompatible with the metric.
- Never duplicate one persistent entity merely because it had several launch
  stages or appeared in several announcements.
- Never infer class membership from a product mention alone.
- Never silently mix entity levels in one distribution. Analyses spanning
  umbrella products and atomic features emit an entity-level warning.
- Never use a draft target to silently select, filter, or weight reference
  cases. Selection is an explicit analysis decision.
- Never present clustered case ids as independent observations without reporting
  both subject and dependence-cluster counts.
- Never derive an interval by guessing which events are endpoints or by
  silently increasing date precision.
- Never suppress missing required metric context: `warn` remains visible in all
  outputs and `error` blocks analysis creation.
- Archival is reversible. Permanent deletion is out of scope for v0.1.

---

## 9. Non-goals for v0.1

- Web search, browsing, crawling, scraping, or downloading.
- A general document-management or systematic-review platform.
- Automatic entity resolution without reviewable candidates.
- Automatic product-success scoring from heterogeneous disclosures.
- An alternative EDSL runner, cache, credential store, or serializer.
- One-command autonomous research and inference.
- Causal inference from company-reported observational outcomes.
- Hosted multi-user coordination.
- Advanced survival analysis or forecast calibration in the first slice.

---

## 10. Implementation shape

```text
src/flyvbjerg/
  cli.py                 # Typer assembly only
  commands/              # command-family modules
  envelope.py            # JSON contract and human rendering
  workspace.py           # discovery, ids, atomic writes, hashing, locks
  targets.py             # versioned decision targets and gap reports
  collections.py         # collection definitions and versions
  intake.py              # sources, captures, items, resolutions
  claims.py              # scoped claims, attribution, promotion
  cases.py               # dossiers and membership
  groups.py              # portfolios and temporal membership
  events.py              # multi-case lifecycle events
  relationships.py       # typed entity graph
  metrics.py             # definitions, context rules, and derivations
  observations.py        # candidates, decisions, supersession
  edsl_bridge.py         # public EDSL construction/load/audit boundary
  processing.py          # plans, manifests, ingestion, retries
  analysis.py            # frozen sets, clusters, rates, sensitivity
  forecasts.py           # pinned forecasts and reports
  guidance.py            # guide and state-aware next actions
  schemas/
  guides/
```

Do not put business logic in `cli.py`. EDSL-specific imports and compatibility
handling live behind `edsl_bridge.py`; Flyvbjerg never reimplements `.ep`
serialization.

---

## 11. First vertical slice

The first implementation is complete when it can reproduce the essential shape
of the three hand-built simulations without model calls:

1. initialize a workspace and exploratory collection;
2. create an underspecified workspace-level target and report its gaps without
   automatically constructing or filtering a reference class;
3. register one URL-only source and one source with a managed capture;
4. create several untriaged intake items from one shared source;
5. resolve those items into multiple persistent cases and one multi-case event;
6. relate an umbrella product to atomic features;
7. show a composed case dossier without duplicating shared records;
8. create a dated portfolio group without turning it into a case;
9. resolve intake into case-, event-, group-, and multi-subject claims;
10. preserve management attribution without representing it as a causal effect;
11. add a metric after the cases and claims exist, with subject, period, and
    required-context rules, then report missing context;
12. promote a compatible claim and reject an incompatible portfolio-to-case promotion;
13. derive an event-interval observation from exact endpoints and reject an
    ambiguous or insufficiently precise derivation;
14. add candidate observations and explicit absence states;
15. accept selected observations through separate decisions;
16. freeze an analysis set with dependence clusters and compute a
    provenance-complete distribution reporting both subject and cluster counts;
17. return a schema-valid JSON envelope and useful next action from every path;
18. validate all hashes, scopes, temporal memberships, references, inverse
    relationships, and state transitions.

The second slice adds native EDSL processing over registered captures. The third
adds forecasts and scoring.

Tests use synthetic files and API-key-free EDSL objects. They require no network
or paid inference. During monorepo development, install Flyvbjerg and overlay the
local EDSL checkout with `pip install -e ../edsl`; published metadata depends on
a compatible released EDSL version.

---

## 12. Design evidence

This model was revised after three hand-built simulations:
`simulations/upwork-product-launches/` and
`simulations/upwork-monetization/`, which used real Upwork press releases,
earnings materials, and filings, and
`simulations/mlb-expansion-franchise/`, which modeled a new-franchise decision.
Together they demonstrated:

- source-to-case relationships are many-to-many;
- collected material often precedes stable case identity;
- a product and its launch events must be separate;
- umbrella products and atomic features require typed relationships;
- company disclosures produce heterogeneous claims rather than a ready-made
  success metric;
- absence states must distinguish lack of research from lack of disclosure;
- claims need scope before they need metrics;
- portfolio disclosures must not propagate to portfolio members;
- persistent products and pricing interventions are different analytical units;
- management attribution is evidence but not an isolated causal estimate;
- metric compatibility requires subject level, period basis, comparison basis,
  and allocation semantics in addition to type and unit;
- a target may need to remain exploratory while its location, timing, ownership,
  venue, and operating assumptions are filled in;
- cases from the same expansion round or intervention program are analytically
  dependent even when they have distinct identities;
- elapsed-time outcomes are reproducible derivations from exact event pairs,
  not free-standing numbers;
- a metric can be numerically observed yet remain uninterpretable without
  required context such as venue capacity or number of home dates.

Further simulation should continue to change this specification before the CLI
surface is treated as stable.
