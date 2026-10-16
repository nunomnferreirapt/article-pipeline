# Why small field teams go offline-first

Small field crews do not adopt offline-first apps because they like new
software. They adopt them to get their evenings back. The gains are real, and
so are the limits. Both are worth stating plainly before a crew of four signs
up for a tooling change.

## The problem is the evening, not the morning

A survey of 140 small field crews, run between March and June 2025, put a
number on something every crew lead already knows. [S1] A small crew here means
two to six people on site. [S1] Of those 140 crews, 87 were offline for at
least one hour on a typical working day. [S1] The median crew spent 3 hours a
day without a usable connection. [S1]

The lost hours do not vanish. They move to the evening. Before switching tools,
the most common evening task reported by crews was re-entering notes taken on
paper during the offline hours. [S1] One crew lead put it at about two hours a
night spent typing in what the crew had already written down once. [S2]

## What offline-first means here

The survey used a narrow definition: an offline-first app stores every record
on the device first and syncs when a connection returns. [S1] That is the whole
idea. The device is the place where work happens, and the server catches up.

## What crews got

Crews that moved to offline-first tools cut their end-of-day sync time from 3.5
hours to 40 minutes on average. [S1] For the crew lead interviewed, the motive
was never the technology. [S2] In her words, nobody on the crew asked for new
technology; they wanted their evenings back. [S2] Her test for any field tool is
blunt: it has to work in a hole in the ground, or it is not a field tool. [S2]

Adoption was not instant. The crew took about two weeks to settle in, and the
first week was rough because people did not trust that data was saved when the
screen said offline. [S2] A year on, 62 percent of the crews that adopted an
offline-first tool in 2024 were still using it. [S1]

## Where it breaks

The other 38 percent matter more than the headline. [S1] The crews that gave
up most often named sync conflicts between devices, stale reference data, and
the lack of an audit trail their client would accept. [S1] Those are the three
limits an essay on the subject argues are structural, not teething problems. [S3]

Sync conflicts first. The essay calls them the normal case, not an edge case,
whenever two people measure the same thing on the same day. [S3] A small team
has nobody whose job it is to resolve them, so they get resolved by whoever
happens to sync last. [S3] The crew lead hit exactly that: the first time two
devices edited the same record, the crew got a conflict screen nobody
understood and lost a morning to it. [S2]

Stale data second. A list cached on a device in spring can still be in use in
autumn, and the app does not know the list is old, and neither does the person
using it. [S3] The crew's answer was a rule: the lead syncs every device before
anyone leaves the depot. [S2]

Audit trails third. Many tools keep history on the server only from the moment
of sync, so the hours before sync are a blind spot, and offline-first is not a
free lunch in regulated settings. [S3] There is also a cost that never shows up
on the feature list: supporting offline means two paths through every feature,
and teams of two to six people rarely have the budget to test both on every
release. [S3]

## What to do with this

None of this is an argument for paper. The essay's author says so directly.
[S3] It is an argument for adopting offline-first with open eyes: for the hours
the crew is actually offline, with a written rule for who owns which record,
and with the audit-trail question asked before the first day in the field.

The crew lead's closing advice says the same thing from the other side. The
app is the easy part. The hard part is agreeing who owns which record and
writing that down before the first day in the field. [S2] A crew that does
that work first will get its evenings back and keep them.
