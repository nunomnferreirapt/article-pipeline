# Essay: the limits of offline-first for small teams

This is an invented essay written for the article-pipeline example. It argues
one side of the question on purpose.

Offline-first is a sound idea applied to the wrong problem more often than its
fans admit. The idea is simple: the device is the source of truth and the
server catches up later. The trouble starts when more than one device claims
to be the source of truth for the same record.

Sync conflicts are not an edge case for field crews. They are the normal case
whenever two people measure the same thing on the same day. A small team has
nobody whose job it is to resolve those conflicts, so they get resolved by
whoever happens to sync last.

Reference data goes stale in the same quiet way. A list of site codes or a
price table cached on a device in the spring can still be in use in the autumn.
The app does not know the list is old, and neither does the person using it.

Regulated work raises the bar again. An inspector or an auditor wants to know
who recorded a value, on which device, at what time, and whether it was changed
later. Many offline-first tools keep that history on the server only from the
moment of sync. The hours before sync are a blind spot. Offline-first is not a
free lunch in regulated settings.

Then there is the cost. Supporting offline means supporting two paths through
every feature: the one that works with a connection and the one that works
without it. Teams of two to six people rarely have the budget to test both paths
on every release.

None of this means small teams should stay on paper. It means they should
adopt offline-first for the specific hours they are offline, write down who
owns each record, and ask hard questions about audit trails before the first
day in the field.
