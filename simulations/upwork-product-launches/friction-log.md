# Friction log

## 1. A product is not the same thing as a launch

Press releases describe announcement, beta, waitlist, beginning rollout,
bundling, broad availability, expansion, and re-platforming. A single
`first_public_launch_date` loses important structure. The hand build added
`events.jsonl` inside each dossier.

**Likely spec change:** make case events first-class. Keep the case as the
persistent product identity and represent launch stages as events.

## 2. Umbrella products and atomic features coexist

Uma powers Job Post Generator, Proposal Tips, Chat Pro, matching, proposal
drafts, and Managed Services. Counting Uma beside those features risks double
counting or mixing levels.

**Likely spec change:** cases need typed relationships such as `powers`,
`replaces`, `bundled_into`, `feature_of`, and `renamed_to`, plus validation that
warns when a rate mixes entity levels.

## 3. Source-to-case is many-to-many

One Upwork Updates release supports several product dossiers, and one product is
discussed in several releases and earnings materials. Keeping sources only
inside a case would duplicate them.

**Current design response:** retain class-level source records and let each case
hold supporting files plus source references.

## 4. Outcomes are selectively and heterogeneously disclosed

Examples found in the first pass include time saved, qualitative faster hiring,
daily-active-user growth, strong adoption without a number, feature expansion,
and portfolio revenue growth. These are not one comparable success metric.

**Consequence:** do not define `product_success` yet. First model disclosures as
typed claims. A later metric might be `still-supported-after-12-months`,
`repeatedly-mentioned-in-next-four-quarters`, or a carefully defined adoption
disclosure measure, but each risks measuring disclosure strategy rather than
product performance.

## 5. Absence has several meanings

Boosted Profiles has no initial launch date in this pass because it has not yet
been researched. Uma has no clean adoption number because disclosures aggregate
its features. Neither should be a generic null.

**Likely spec change:** distinguish `not_researched`, `not_disclosed`,
`not_applicable`, `conflicted`, and `censored` at the metric-coverage level.

## 6. We need an announcement or release entity

The Spring and Fall Upwork Updates are meaningful corporate release events with
many product members. They should be representable without pretending they are
products themselves.

**Open design:** introduce a general `event` record related to one or many
cases, rather than only case-local event files.

## 7. Local material is not yet preserved

This simulation registers canonical URLs and retrieval dates but does not copy
the source pages or PDFs. Link drift would weaken future reproducibility.

**Likely real workflow:** the research agent saves permitted source artifacts
into managed storage and records content hashes; URL metadata alone is a useful
but weaker source record.
