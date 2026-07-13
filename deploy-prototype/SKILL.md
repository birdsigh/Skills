---
name: deploy-prototype
description: Deploy static HTML prototypes to a ProtoLab instance (a Cloudflare Worker that hosts throwaway prototypes) with one command, and manage labs, pairing, and deployed prototypes. Use this whenever the user wants to deploy, publish, ship, host, or share an HTML prototype, mockup, demo page, or static site they've built — phrases like "deploy this", "put this on the lab", "get me a link for this prototype", "push this to protolab", "share this demo". Also use for managing ProtoLab itself from the client side - pairing with a new lab, listing or switching labs, removing deployed prototypes, or checking whether deploys are set up. Do NOT use for deploying apps with backends, databases, auth, or build steps.
compatibility: Requires Python 3.8+ and network access to the user's ProtoLab instance.
---
 
# deploy-prototype
 
ProtoLab hosts throwaway static HTML prototypes. A deploy is a single
authenticated HTTP call — no repo, no wrangler, no Cloudflare account on this
side. Everything goes through the bundled client:
 
```
python3 <skill-dir>/scripts/protolab.py <verb> ...
```
 
Prefer the script over hand-rolled curl: it handles config resolution,
zipping, pairing, and turns API errors into actionable messages.
 
**A deploy is user-visible and overwrites by slug, so it is never run
without explicit user approval of the deploy plan.** See "Confirm before
deploying" below — this gate applies to every `deploy`, including re-deploys.
 
## Scope guard — static HTML only
 
ProtoLab serves static files. If the prototype needs a backend, database,
auth, server-side rendering, or a build step (React with JSX, bundlers,
npm build), this is the wrong tool. Say so plainly and stop — do not try to
"make it work" by building locally and deploying the output unless the user
explicitly asks for that.
 
## Which lab? (resolution order)
 
The script resolves the target lab in this order, first match wins:
 
1. `PROTOLAB_URL` + `PROTOLAB_TOKEN` env vars — explicit override, wins outright
2. `PROTOLAB_LAB=<name>` env var selecting a config entry
3. `--lab <name>` — pass this when the user names a lab ("deploy to the work lab")
4. `default` from config
5. Exactly one lab configured — use it
6. Otherwise the script exits with code 3 and lists the labs. **Ask the user
   which lab they mean; never guess.**
Config lives at `~/.config/protolab/config` (TOML, chmod 600). If that is
missing, the script falls back to `./.protolab` in the working directory —
useful in sandboxed sessions where `$HOME` does not persist. When pairing in
such a session, pass `--local` to write `./.protolab` instead, and make sure
`.protolab` is gitignored.
 
## Verbs
 
| Command | What it does |
|---|---|
| `status` | Show config file, labs, default; health-check the resolved lab |
| `pair --url <url> [--name <alias>] [--local]` | First-run pairing (below) |
| `deploy <path> [--slug <slug>] [--lab <name>]` | Deploy a folder or a single .html file |
| `remove <slug> [--lab <name>]` | Delete a prototype from the lab |
| `labs` | List configured labs |
| `set-default <name>` | Change the default lab |
| `remove-lab <name>` | Drop a lab from local config (see note below) |
| `health [--lab <name>]` | Verify the token and URL work |
 
## First run — pairing
 
If the user has never set up (`status` shows no labs, or deploy exits with
code 3 and an empty lab list):
 
1. Ask for the lab URL only — nothing else, noting to the user that ProtoLab needs to be setup separately first if they have not already done so (https://github.com/birdsigh/ProtoLab).
2. Run `pair --url <url>`. It prints a short code and blocks, polling.
3. Relay to the user verbatim: "Open `<url>/settings` and approve code
   **XXXX**." The code matters — approval is by code, not hostname.
4. On approval the script saves the token. Ask the user what to call this
   lab if `--name` wasn't given (the script suggests the domain's short
   name); the first lab paired becomes the default.
Re-pairing an already-configured URL updates that entry in place — the
script dedupes by URL, so this is also the fix for a revoked token.
 
## Confirm before deploying — mandatory
 
Never run `deploy` until the user has explicitly approved the deploy plan for
this specific deploy. This is a hard gate, not a courtesy: a deploy is
publicly reachable at a URL and replace semantics mean a colliding slug
silently overwrites whatever was there.
 
Before every deploy, resolve the target (lab, source, slug) and present the
plan back to the user, then wait for approval. Surface all of:
 
- **Lab** — the resolved lab's alias and its host URL, so it's unambiguous
  which lab receives this (e.g. `work-lab → https://lab.example.com`).
- **Source** — the exact folder or file being deployed (the path).
- **Result URL** — the slug and the full URL it produces
  (e.g. `→ https://lab.example.com/my-idea/`).
- **Overwrite** — whether that slug already exists on the lab. If it does,
  say plainly that deploying replaces the existing prototype at that URL. If
  you can't tell without a network call, say the slug *may* already be in use
  and that deploy overwrites on collision.
What counts as approval:
 
- An explicit go-ahead **after** the plan is shown ("yes", "ship it",
  "go ahead") — this is the normal path.
- A same-turn instruction that itself fully specifies and authorises the
  deploy ("deploy ./foo to work-lab as bar, go ahead") can satisfy the gate,
  but only when lab, source, and slug are all unambiguous. Still echo the
  resolved plan in your reply so the user sees the URL and overwrite status
  before it happens.
What does NOT count: silence, a vague earlier "let's deploy this at some
point", or approval you inferred rather than the user gave. If any of lab,
source, or slug is ambiguous, resolve it (ask, per the resolution rules
above) before presenting the plan — never guess your way past the gate.
 
After the deploy, echo the full URL the script returns (see below).
 
## Deploying
 
- A folder must contain `index.html` at its root. The script zips it
  (skipping `.DS_Store` and friends) and PUTs it. A single `.html` file is
  sent directly and becomes `index.html`.
- If `--slug` is omitted the script derives one from the folder/file name
  (lowercased, invalid characters became hyphens). The derived slug is part
  of the deploy plan the user approves (above), so it's always surfaced
  before deploy — pay extra attention when it looks surprising, since slugs
  are the URL and a colliding slug overwrites.
- Limits: 25 MB zipped, 500 files. Slugs: lowercase alphanumeric plus
  hyphens, max 63 chars; `settings`, `api`, `favicon.ico`, `robots.txt`,
  and `_`-prefixes are reserved.
- **Always echo the full URL** the script prints (e.g.
  `https://lab.example.com/my-idea/`), never just the slug — slugs are
  per-lab namespaces and mean nothing without the host.
## Errors worth translating
 
- Exit code 4 (HTTP 401): the token was revoked or the lab was reset. Tell
  the user "the token for '<alias>' was revoked — want me to re-pair?"
  rather than surfacing the raw error. Re-pair with the same URL.
- Exit code 3: ambiguous lab — ask, never guess.
- `rate limited` during pairing: the lab throttles pairing hard; wait a
  minute before retrying.
- Zip/size/slug validation errors are printed with the reason; fix and
  retry rather than working around the limits.
`remove-lab` only edits local config — it does not revoke the token. If the
user wants the token dead, point them at the lab's `/settings` page.