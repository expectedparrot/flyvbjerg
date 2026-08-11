# Launching a new MLB expansion franchise — simulation

This pre-implementation simulation explores how Flyvbjerg would support a
prospective Major League Baseball expansion franchise. It uses the four most
recent expansion teams as an initial reference cohort:

- Colorado Rockies and Florida Marlins, inaugural season 1993;
- Arizona Diamondbacks and Tampa Bay Devil Rays, inaugural season 1998.

This is a model test, not advice to MLB, a city, or an ownership group. The
collection is incomplete for financial forecasting and uses public historical
sources with different provenance strengths.

## Target

A not-yet-located MLB expansion franchise expected to move from league award to
its first regular-season game. Because no city, stadium plan, ownership group,
league terms, or launch year is specified, the target remains deliberately
generic and cannot yet support target-specific adjustment.

## Initial questions

1. How long is the interval from franchise award to inaugural season?
2. What first-season attendance and on-field performance have recent expansion
   teams achieved?
3. How many seasons passed before the first postseason appearance?
4. Which launch workstreams are common across cases?

## Initial descriptive results

| metric | Colorado | Florida | Arizona | Tampa Bay | median |
|---|---:|---:|---:|---:|---:|
| Inaugural wins | 67 | 64 | 65 | 63 | 64.5 |
| Inaugural attendance | 4,483,350 | 3,064,847 | 3,610,290 | 2,506,293 | 3,337,568.5 |
| Inaugural attendance per home game | — | 37,838 | — | — | not ready |
| Seasons through first postseason | 3 | 5 | 2 | 11 | 4 |

The attendance total is not yet decision-ready: Colorado played in unusually
large Mile High Stadium, Arizona opened a new ballpark, Tampa Bay used an
existing dome, and league/context differences matter. Capacity utilization and
market-adjusted demand may be better later metrics.

## Most important modeling result

The franchise is the persistent case. The expansion cohort is a group. League
award, venue agreement, naming, executive appointments, expansion draft,
ticket sales, spring training, and first regular-season game are events. League
rules and the paired expansion program are shared context, not duplicated case
attributes.

