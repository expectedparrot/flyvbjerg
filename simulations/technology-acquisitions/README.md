# Large technology acquisitions: analytical stress test

This simulation tests whether Flyvbjerg can turn a Wikipedia-supported business
reference class into a decision-relevant outside view. The pilot contains ten
definitive technology-acquisition agreements announced during 2015–2022 with
announced value of at least $20 billion. Membership does not depend on whether
the deal later completed.

## Pilot results

- 7 of 10 agreements completed; 3 terminated.
- Terminal-state duration ranged from 185 to 637 days.
- Median terminal duration was 467 days (about 15.3 months); mean was 426 days.
- 0/10 reached a terminal state within 6 months, 4/10 within 12 months, 8/10
  within 18 months, and 10/10 within 24 months.
- Among completed deals, 4/7 closed within 12 months and 6/7 within 18 months.

A hypothetical 12-month inside-view estimate is therefore more aggressive than
the pilot median: only 40% reached either completion or termination within that
time. This is not yet a market base rate because the seed cohort has not been
audited for exhaustive enumeration.

## Package implications

The stress test produced a small, general analytical slice:

1. nearest-rank empirical quantiles;
2. `locate` for a target estimate in a reference distribution;
3. `threshold` with explicit denominators and case identities;
4. multi-terminal event-interval derivation; and
5. `dependence_status: not_assessed` instead of assumed independence.

Still open are stratification by terminal state, cohort-enumeration completeness,
and composition into a short decision brief.

See [definition.md](definition.md) for the cohort rule and
[friction-log.md](friction-log.md) for workflow findings. The full audit data
are stored under `.flyvbjerg/`.
