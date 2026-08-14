# Pilot reference-class definition

## Decision question

When a large public company announces a separation, how much calendar time
should a decision-maker allow before the first independent company exists, and
how much longer can a multi-stage plan take to finish?

## Seed-cohort rule

One publicly announced plan, announced from 2014 through 2022, by a large
publicly traded US parent to create at least one separately traded public
company through a spin-off or corporate split. Membership is determined only
from facts stated when the plan was announced. A later completion, delay,
revision, partial completion, or abandonment cannot affect membership.

This pilot is a deliberately documented eight-case seed cohort assembled from
Wikipedia company histories. It is not asserted to be an exhaustive census.
The cohort therefore supports workflow testing and a provisional outside view,
not a population base rate.

## Cases

- eBay / PayPal
- Hewlett-Packard / HP Inc. and Hewlett Packard Enterprise
- Alcoa / Arconic and Alcoa Corporation
- United Technologies / Carrier, Otis, and the aerospace successor
- IBM / Kyndryl
- General Electric / GE HealthCare, GE Vernova, and GE Aerospace
- Kellogg / Kellanova and WK Kellogg
- 3M / Solventum

## Endpoint rules

`first_separation_days` is elapsed calendar days from the public announcement
to the first planned independent public company becoming legally separate or
beginning regular-way trading, whichever clearly establishes independence.

`full_plan_days` is elapsed calendar days until all separations in the latest
documented version of the announced plan are complete. A plan revision is an
event, not an error: the original scope and revised scope are both preserved.
For a one-stage plan, first and full completion dates coincide. An unsupported
endpoint remains missing; it is never coded as zero.

## Important limits

The cases share a parent-level decision and can contain several successor
companies, so successor-level outcomes are dependent and must not be treated as
independent cases. Announcement wording, legal separation, distribution, and
first trading can occur on different dates. This pilot uses the explicit rules
above and retains those distinctions in the event record.
