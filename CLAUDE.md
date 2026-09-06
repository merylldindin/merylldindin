# merylldindin

GitHub profile README for Meryll Dindin. The special `merylldindin/merylldindin`
repository renders `README.md` at the top of the GitHub profile page
(github.com/merylldindin). This repo holds only that presentation — no code, no
build step, no linter. GitHub renders `README.md` directly on push.

**This repository is public.** Nothing committed here may name a local
filesystem path, a private tooling directory, or a personal MCP endpoint.

## Layout

| Path        | Purpose                                                       |
| ----------- | ------------------------------------------------------------- |
| `README.md` | The rendered profile: bio, ventures, research, patents, stack |

## Rendering constraints

GitHub sanitizes README HTML. The file uses `<a>`, `<img>` and
`<div align="center">`, which survive; stylesheets, scripts and `class`
attributes are stripped, so layout is limited to alignment and tables.

Relative links resolve against the repository, not the profile page, so every
link and image source is absolute. Images come from `cdn.merylldindin.com`.

Badges are shields.io, all on background `1B1B1B` so they read on both the light
and dark GitHub themes. The LinkedIn badge carries its logo as an inline base64
SVG rather than a named `logo=` slug — preserve that data URI when editing the
line.

Nothing checks the file before it publishes. Run `npx prettier --write README.md`
and `npx markdownlint-cli2 README.md` before committing, and open the rendered
profile afterwards to confirm every badge and link resolved.

## Conventions

- Conventional Commits; `docs(readme): <description>` for content changes
- Every factual claim — title, ventures, fundraising, patents, publications —
  must be accurate and verifiable on a public page under Meryll's own name
- Compliance badges name frameworks the work actually operates under: FERPA,
  COPPA, ISO 27001. Never add SOC 2 or HIPAA — Parallel holds neither, and a
  false certification claim on a public profile is the costly kind of error
