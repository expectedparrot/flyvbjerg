# Friction log

## 1. Claims need scope before they need a metric

The intake contains company-wide take rate, portfolio revenue, component
revenue, subscriptions, user outcomes, and management attribution. These are
useful structured claims before we know which can share a metric definition.

**Model implication:** `candidate_claim` should be a durable first-class record,
not merely an intake item waiting to become an observation. A claim has scope,
period, value or statement, source, and limitations. Promotion to an observation
happens only after a metric exists.

## 2. Portfolio aggregates must not flow down the entity graph

Ads & Monetization revenue includes Boosted Profiles, Boosted Proposals,
Connects Purchases, Featured Jobs, and subscriptions in later investor
presentations. Portfolio growth cannot be copied to every component.

**Model implication:** claims need explicit scope (`company`, `portfolio`,
`case`, `event`, or `multi_intervention`) and an `allocation_prohibited` guard.

## 3. A persistent product and an intervention are different analytical units

Freelancer Plus is a persistent subscription. The Q2 2024 addition of Connects
and Chat Pro plus a higher price is one intervention event. Revenue growth can
describe the product; a causal question about the repackage belongs to the
event.

**Model implication:** metrics and observations may need to apply to events as
well as cases. The current spec applies observations only to cases.

## 4. Management attribution is evidence, but not an isolated effect

Management explicitly linked the 2023 take-rate increase to the flat fee and
Connects strategies, and linked Q2 2024 pricing and packaging changes to the
highest take rate and portfolio growth. Those claims matter, but they do not
identify separate causal effects.

**Model implication:** structured claim kinds should include
`management_attribution`, with causal-strength metadata and multi-entity scope.

## 5. Pricing policies have versions

The flat 10% fee replaced a tiered schedule, with grandfathering for existing
5% relationships through 2023. Contract initiation fees and subscription prices
may also change over time.

**Model implication:** pricing terms should be versioned attributes or events;
one mutable `price` field on a case would destroy history.

## 6. Reported growth rates need denominator semantics

Revenue growth, subscriber growth, active-subscription counts, take rate, invite
lift, acceptance lift, and hire lift are all percentages or counts but are not
interchangeable. Even repeated `revenue-growth-yoy` observations depend on
product versus portfolio scope and quarterly versus annual periods.

**Model implication:** metric validation must include scope/entity level and
period basis, not type and unit alone.

## 7. URL-only intake is visibly incomplete

The earnings sources are registered, but no exact captures are preserved. Page
content can change and locators are weaker than capture-backed page or line
ranges.

**Next research step:** save the official prepared remarks, shareholder letters,
filings, and results releases where permitted; hash them; then upgrade source
locators against those captures.

