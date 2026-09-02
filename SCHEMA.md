# Data Schemas (locked 2026-08-31)

## 1. Historical / Foreign Actors — `data/historical_actors.json`

```json
{
  "actor_id": "string (slug)",
  "full_name": "string",
  "birth_name": "string (if different)",
  "birth_country": "string",
  "life_span": {"born": "YYYY-MM-DD", "died": "YYYY-MM-DD"},
  "primary_affiliations": ["string (e.g., Jewish National Fund, World Zionist Organization, British Mandatory Govt)"],
  "historical_role": "string (brief context)",
  "key_land_actions": [
    {
      "date": "YYYY-MM-DD or YYYY",
      "action_type": "string (e.g., Land Purchase, Policy Lobbying, Fund Raising, Legal Charter)",
      "location_affected": "string (region/locality)",
      "impact_description": "string",
      "primary_source_citation": "string (URL, book citation, archive ID)"
    }
  ],
  "personal_context": [
    {
      "title": "string (short label, e.g., 'Brother killed leading the Entebbe raid')",
      "date_or_range": "YYYY-MM-DD or YYYY or a range",
      "description": "string — biography, family, military service, or a major event not itself a land action",
      "citation": "string"
    }
  ]
}
```

### `personal_context` (added 2026-09-02)

Optional array, same shape in both this file and `knesset_members.json` below. For biographical
color and major life events that aren't themselves land actions but round the person out — family
(a sibling killed in a famous operation, say), military service, an unrelated notable event they
were central to, or — for a living/sitting person — an active legal matter. Kept structurally
separate from `key_land_actions`/`legislative_and_action_record` on purpose: this dataset's core
subject is land and dispossession, and `personal_context` is explicitly the "everything else that
makes this a real person, not just a land-policy record" field, not a second land ledger.

Same living-persons discipline as everywhere else in this dataset: a real citation, no
characterization beyond what the citation supports, and for an active legal matter — a criminal
trial, say — every charge stated as *alleged* until there's an actual verdict, not as established
fact. `null`/omitted rather than uncited, exactly like the existing rule for `land_impact` on
living MKs above.

## 2. Knesset Members / Legislative Items — `data/knesset_members.json`

```json
{
  "mk_id": "string (slug)",
  "full_name": "string (English)",
  "hebrew_name": "string",
  "birth_name": "string",
  "birth_country": "string",
  "knesset_terms": [
    {
      "knesset_number": "integer",
      "party": "string",
      "political_alignment": "string (Far-Left | Left | Center | Right | Far-Right | Religious Nationalist | Unaffiliated)"
    }
  ],
  "legislative_and_action_record": [
    {
      "event_id": "string",
      "date": "YYYY-MM-DD",
      "category": "string (Legislation Vote | Executive Action | Settlement Sponsorship | Land Expropriation Order)",
      "bill_or_action_title": "string",
      "vote": "string (For | Against | Abstain | Absent | N/A for Non-Legislative)",
      "land_impact": {
        "spatial_region": "string (e.g., West Bank Area C, Negev/Naqab, East Jerusalem, Galilee)",
        "estimated_hectares_affected": "number or null",
        "description": "string describing how this directly or indirectly altered land access/status"
      },
      "citation": "string (Knesset Archives ID, official record, or academic source)"
    }
  ],
  "personal_context": [
    {
      "title": "string",
      "date_or_range": "YYYY-MM-DD or YYYY or a range",
      "description": "string",
      "citation": "string"
    }
  ]
}
```

`personal_context` is the same field, same rules, as the one added to `historical_actors.json`
above — see that section for the full explanation. It's especially relevant here, since most of
the people in this file are living and several have active legal matters worth recording
honestly, under the same alleged-until-verdict standard.

### Living/sitting MKs — draft-time rule (see SCOPE.md)

`full_name`, `hebrew_name`, `birth_country`, `knesset_terms`, and `vote` are on-the-record
public facts and can be filled without a per-field citation. `land_impact.description`,
`estimated_hectares_affected`, and any characterization beyond the bare vote go in only when
a real citation is attached, or are left `null` — never asserted uncited for a living person.
This restriction does not apply to deceased historical figures.

### Citation confidence

No separate `citation_status` field — per Nick, citation is a single string. Where Claude's
confidence in a specific citation is low, the string itself says so, e.g.
`"UNVERIFIED — best guess: Sefer HaChukim 1953, no. 122"`, rather than presenting an
unverified source as if confirmed. Nick verifies before anything is published.

## 3. Organizations — `data/organizations.json` (one file, not two — see below)

Covers political parties, paramilitaries/militias, and pre-Mandate Zionist organizations in a
single schema, since they share one lineage graph (a militia becoming a party's founding core
is the same *kind* of fact as a party's Knesset vote record, just a different point on the same
timeline). Membership is a reference into `historical_actors.json` / `knesset_members.json` by
id, not a duplicated bio — avoids a third person-file and keeps one source of truth per person.

```json
{
  "org_id": "string (slug)",
  "name": "string",
  "hebrew_name": "string",
  "org_type": "string (Pre-Mandate Self-Defense Group | Paramilitary/Militia | Political Party | Youth Movement | National Military | Self-Governing Community | Sovereign State | Legislative Body | International Zionist Body | Land Fund | Land Company | Settlement Movement | Labor Federation | Representative Assembly | Executive Council | Government Office | International Body | Financial Institution)",
  "founding_date": "YYYY-MM-DD or YYYY",
  "dissolution_date": "YYYY-MM-DD or YYYY or null",
  "ideology": ["string tags, e.g. Labor Zionism, Revisionist Zionism, Religious Zionism"],
  "lineage": {
    "predecessor_orgs": ["org_id (or free text if the predecessor isn't profiled yet)"],
    "successor_orgs": ["org_id (or free text)"],
    "merged_into": "org_id or null",
    "current_knesset_party_id": "org_id or null — traces lineage to a party sitting in today's Knesset, even through multiple mergers"
  },
  "notable_members": ["actor_id or mk_id — reference into the other two files; add a stub bio inline only if the person isn't profiled anywhere yet"],
  "action_record": [
    {
      "event_id": "string",
      "date": "YYYY-MM-DD",
      "action_type": "string (Sanctioned Political Action | Land Settlement Operation | Non-Sanctioned Militant Action | Policy Lobbying | Fund Raising)",
      "title": "string (short label)",
      "location_affected": "string",
      "description": "string, factual, sourced — casualty/scale figures noted as disputed-range where sources disagree rather than asserted as a single number",
      "citation": "string"
    }
  ],
  "knesset_participation": [
    {
      "knesset_number": "integer",
      "seats_won": "integer or null",
      "notable_votes": [
        {"date": "YYYY-MM-DD", "bill_or_action_title": "string", "party_position": "string (For | Against | Abstain | Free Vote | N/A)", "citation": "string"}
      ]
    }
  ]
}
```

`action_type: "Non-Sanctioned Militant Action"` is where Nick's "non-sanctioned destructive
actions" requirement lives — used for armed/paramilitary actions outside a group's official
political-wing sanction (e.g. Irgun/Lehi operations the Haganah leadership didn't authorize).
Same UNVERIFIED-citation discipline as the other two files applies throughout.

`org_type: "Financial Institution"` added 2026-09-01 for the Jewish Colonial Trust — the WZO's
own chartered bank, distinct from `"Land Fund"` (JNF's type: a fund holding land itself under
inalienable Jewish tenure) since the Trust and its Anglo-Palestine Bank subsidiary held and lent
capital, not land.

`org_type: "National Military"` added 2026-08-31 for the IDF — previously out of scope
("national army, not a party/militia lineage node") but Nick asked for it explicitly. `lineage`
for a state military doesn't fit the clean single-predecessor pattern (the IDF absorbed the
Haganah cleanly in 1948, but took in the Irgun by force via the Altalena Affair and Lehi only
partially after its 1948 outlawing) — those nuances are described in the IDF's own
`action_record` and cross-referenced from Haganah/Irgun/Lehi's entries rather than forced into
the `lineage` fields' single-predecessor shape.

`org_type: "Youth Movement"` first used 2026-09-02 for Betar — the Revisionist youth movement
Jabotinsky founded in Riga in 1923, which trained the generation that led Irgun and Lehi and
later founded Herut/Likud (Begin and Shamir both came up through it; both entries' cross-links
are documented in their own `personal_context`/`primary_affiliations`). Unlike Irgun/Herut, Betar
never dissolved or merged — `dissolution_date` and `lineage.merged_into` are `null`, matching the
pattern already used for still-active orgs like Likud.

## 4. Current Foreign Actors — `data/current_foreign_actors.json` (added 2026-08-31)

Present-day counterpart to schema #1 (Balfour, Silver, Rothschild are all "foreign patrons" —
this is the same category, alive). **Deliberately built independent of Money Tracker** (Nick:
"I want no relation to Money Tracker... build this independently"), and structured on the MK
file's public-interest/transparency discipline rather than schema #1's freer shape, because
these are living people.

**Scope lock: institutional public role only.** In scope: an organization's listed officer/
director, a registered lobbyist (FARA, a national lobbying register, etc.), someone named and
quoted by mainstream press *in that professional capacity*. Out of scope: private individuals
with no organizational/registered role, however publicly they personally advocate. No religion/
ethnicity field anywhere in this schema — role and registration status only.

```json
{
  "actor_id": "string (slug)",
  "full_name": "string",
  "organizational_role": "string (e.g., Executive Director, Board Chair, Registered Foreign Agent)",
  "organization": "string",
  "operating_countries": ["string — country/countries of primary operation, e.g. United States, United Kingdom, Canada, Australia, EU member state"],
  "public_registration": "string or null — the evidentiary basis for public-role status (FARA registration ID, national lobbyist register ID, nonprofit/charity registration number)",
  "role_status": "string (CONFIRMED — Claude has reasonable confidence in current officeholder | UNCONFIRMED — organization/role identified, current named holder not verified by Claude, do not treat the name as reliable)",
  "primary_activity_description": "string — factual, documented conduct only, no characterization of intent",
  "action_record": [
    {
      "date": "YYYY-MM-DD or YYYY",
      "action_type": "string (Registered Lobbying | Organizational Leadership | Fund Raising | Public Advocacy Statement)",
      "location_affected": "string (country/region)",
      "description": "string",
      "citation": "string (registration filing, org's own public materials, mainstream press citing them by name in their professional role)"
    }
  ]
}
```

### Why `role_status` exists (and doesn't exist in schema #1 or #2)

Historical actors are dead — their roles don't change. Living MKs have a public, easily
time-stamped voting record. But "who currently runs organization X" is exactly the kind of fact
that turns over on a timescale shorter than this session's knowledge is current for, and getting
a living person's current title wrong in a lobbying-focused database is a real misattribution
risk, not just an inconvenience. `role_status: UNCONFIRMED` is the honest default; `CONFIRMED`
is used sparingly, only for long-tenured, extensively-published public figures.

## 5. Laws — `data/laws.json` (added 2026-09-01, documented here retroactively)

Built when Nick asked for dedicated pages for specific laws rather than leaving them buried
inside an MK's `legislative_and_action_record`. Content for the first two entries was adapted
from what already lived in `knesset_members.json` (Kaplan/Eshkol), now given proper standalone
treatment instead.

```json
{
  "law_id": "string (slug)",
  "title": "string (English, incl. Hebrew-year citation, e.g. 'Absentees' Property Law, 5710-1950')",
  "hebrew_title": "string",
  "official_citation": "string (Sefer HaChukim volume/page)",
  "enactment_date": "YYYY-MM-DD",
  "knesset_number": "integer",
  "sponsoring_ministry": "string",
  "sponsoring_mk_id": "string — references knesset_members.json, resolved via the wiki's personLink() helper",
  "category": "string (e.g. Absentee Property, Land Expropriation)",
  "summary": "string",
  "land_impact": {
    "spatial_region": "string",
    "estimated_hectares_affected": "number or null",
    "description": "string"
  },
  "citation": "string"
}
```

## 6. Topics — `data/topics.json` (added 2026-09-01)

The long tail of things that are neither a person, an organization, nor a law: geographic
regions, migration periods (the Aliyah waves), one-off historical events (a conference, a
congress), publications, agreements, and lineages/families. Rather than force each of these
into a bespoke schema (a "place" schema, a "period" schema, a "publication" schema...), one
flexible schema covers all of them — the same way a real encyclopedia varies its infobox by
context without needing a structurally different article type underneath.

```json
{
  "topic_id": "string (slug)",
  "name": "string",
  "aliases": ["string (optional) — other names prose actually uses for the same topic"],
  "hebrew_name": "string (optional)",
  "topic_type": "string (Geographic Region | Migration Period | Historical Event | Publication | Agreement | Family/Lineage | Political Era | Institution Type | Historical Phenomenon | Unit of Measurement | Armed Conflict | UN Resolution | Legislative Proposal)",
  "date_or_range": "string (e.g. '1882-1903', '1897', 'N/A')",
  "summary": "string",
  "significance": "string — why this belongs in a land-loss timeline specifically",
  "related_actor_ids": ["string — actor_id or mk_id references"],
  "related_org_ids": ["string — org_id references"],
  "citation": "string"
}
```

`related_actor_ids`/`related_org_ids` are resolved the same way `notable_members` is elsewhere
— through `personLink()`/`orgLink()` — rather than requiring every related name to already
appear naturally in the prose (a Geographic Region's summary won't always happen to name every
relevant person in a linkable sentence).

### `aliases` (added 2026-09-01)

Some topics are the same event under more than one name in general use — Resolution 181 is also
"the 1947 UN Partition Plan," which had already been used unlinked in several other entries'
prose before this topic existed. Rather than duplicate the topic under two `topic_id`s,
`aliases` lets one entry answer to several names: every alias is indexed into the wiki's
auto-linker and its search, and the topic page itself lists them under "Also known as." Added
specifically for the UN Resolutions batch (2026-09-01) — see SCOPE.md.

`topic_type: "UN Resolution"` added the same day, covering both UN General Assembly and UN
Security Council resolutions — `related_org_ids` points to whichever body (`united-nations-
general-assembly` or `united-nations-security-council`) actually adopted it, so "which UN" is
still recoverable without a separate field.

`topic_type: "Legislative Proposal"` added 2026-09-01 for Knesset bills that have not become
enacted law — distinct from `data/laws.json`, which is reserved for laws that actually took
effect (with a real `official_citation`). A bill that failed outright, or passed only a
preliminary/first reading and was later frozen or is still pending further readings, belongs
here instead; if it's later enacted, promote it into `laws.json` and note the supersession in
both places rather than deleting the topic entry.
