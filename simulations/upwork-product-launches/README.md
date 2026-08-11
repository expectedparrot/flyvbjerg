# Upwork product launches — hand-built simulation

This is a pre-implementation simulation of the Flyvbjerg data model using real
Upwork public materials. It is not yet a reference-class forecast and does not
claim to be a complete census of Upwork launches.

## Purpose

Test whether rich case dossiers can represent Upwork product launches before we
commit to a CLI or a final metric scheme.

## Initial scope

- Company: Upwork Inc.
- Initial discovery window: July 2023 through October 2024
- Sources in this pass: Upwork investor-relations press releases, financial
  results, and prepared earnings remarks
- Candidate unit: one named customer-facing product or feature introduced by
  Upwork
- Status: intentionally unresolved; bundled announcements and staged rollouts
  make the unit ambiguous

## Candidate cases in the first pass

| case | first public launch evidence | later outcome evidence found |
|---|---:|---|
| Job Post Generator | 2023-07-11 | ~70% faster posting in FY2023; 73% faster in Q3 2024 |
| Proposal Tips | 2023-07-11 | Upwork says freelancers secured work faster in FY2023 |
| Upwork Chat Pro | 2023-11-06 | strong adoption in Q1 2024; DAU +68% QoQ in Q2 2024 |
| Uma | 2024-04-30 | later capability expansion; product-level adoption not yet found |
| Boosted Profiles | no later than 2024-04-30 in this pass | expanded placement in Q3 2024; only portfolio-level revenue disclosed |

## Immediate model questions

1. Is the case a persistent product (`Uma`) or a launch event (`Uma homepage
   rollout, Spring 2024`)?
2. Is a beta announcement a launch, or should availability stages be separate
   observations?
3. Does a rename or absorption into an umbrella product end the old case?
4. Are monetization features comparable with workflow tools and marketplace
   hubs?
5. Most outcomes are selectively disclosed and use different denominators. What
   common outcome can honestly be applied across cases?

The first pass suggests that product identity and launch events must be distinct
entities, or at least that each product needs an append-only event history.

