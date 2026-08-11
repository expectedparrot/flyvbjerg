# Friction log

## 1. The target deserves first-class status earlier than forecast creation

This simulation begins with a prospective franchise, but the target is
underspecified. Recording that fact before collection prevents accidental
assumptions about city, venue, ownership, or launch year.

**Spec implication:** a lightweight target can be useful during exploration,
not only after an analysis set exists.

## 2. Launch programs create dependent case clusters

Colorado and Florida shared one expansion decision and draft structure; Arizona
and Tampa Bay shared another. Treating n=4 as four independent institutional
experiments overstates information.

**Spec implication:** analysis sets need dependence clusters or group-aware
warnings, not only pairwise relationships.

## 3. One persistent case has many launch workstreams

Award, venue, name, executive team, media agreements, player acquisition,
ticketing, spring training, and inaugural play are separate events. A franchise
launch is a program assembled from event streams.

**Spec implication:** events may need workstream/category and milestone status;
groups are not enough.

## 4. Duration is defined by event pairs

“Time to launch” could mean award-to-first-game, venue-agreement-to-first-game,
or expansion-draft-to-first-game. It should be a derived observation over two
event ids, not a mutable duration field on the case.

**Spec implication:** metrics should support event-pair derivations.

## 5. Raw attendance is easy to collect and easy to misuse

Venue capacity, number of home dates, temporary versus new stadium, market size,
ticket pricing, and novelty affect inaugural attendance. Total attendance is a
valid historical fact but a weak demand forecast without normalization.

**Spec implication:** metric definitions need required context/covariates or an
analysis readiness check beyond type compatibility.

## 6. Franchise success is multidimensional

Inaugural wins, attendance, time to postseason, franchise valuation, operating
economics, stadium delivery, community support, and league-wide value answer
different questions. A single launch-success label would be indefensible.

## 7. Historical source strength varies

Official team timelines are primary for institutional chronology but may be
celebratory and incomplete. Baseball-Reference supplies consistent historical
statistics but is secondary. Financial launch evidence will require league,
municipal, ownership, and contemporary reporting sources.

## 8. The four-case modern cohort is informative but tiny

The narrow cohort improves institutional comparability at the cost of sample
size. Earlier expansions could enlarge the class but introduce era differences.

**Next simulation step:** add earlier expansion cohorts as a broader group and
compare results by era rather than silently choosing one class.

