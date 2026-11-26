# calluna-site

Landing page for Calluna (Android shared shopping list), served at https://callunalist.app.

## Rules

- **Static site, no build step.** Everything that is served lives in `site/`: plain HTML + one
  stylesheet (`site/assets/site.css`). `netlify.toml` stays at the repo root: no build command,
  `publish = "site"`. Nothing outside `site/` is served or referenced by the pages.
- **No cookies, no analytics, no trackers.** No external fonts, scripts, stylesheets or CDNs. No
  JavaScript at all: the CSP in `netlify.toml` sets `script-src 'none'`. No inline `<style>` or
  `style=""` either (`style-src 'self'`).
- **Only these external destinations:** `play.google.com`, `techtrest.github.io`, `mailto:`. Absolute
  `https://callunalist.app/...` URLs are allowed only where the format requires them (canonical,
  hreflang, og:url, og:image).
- **Three languages, same sections in the same order:** EN at `/` (`site/index.html`), DE at `/de/`,
  PL at `/pl/`. Every section except the hero has a visible `<h2>`. A change to one page's
  structure is made in all three.
- **PL text has been reviewed by the Polish reviewer.** Any future PL change goes to the Polish
  reviewer before it ships. Never mention the review on the page.
- **Personal names:** the developer's first name is allowed in the visible text of the EN, DE and PL
  pages only (not in markup, comments or any other file, this one included). No other personal names
  anywhere (`scripts/check.py` enforces it).
- **Copy:** tone and wording come from the marketing chat; facts about the app are checked in the
  Calluna project chat; PL text still needs the Polish reviewer. Don't write or "improve" page text
  here; use the copy you're given verbatim. "Calluna by Techtrest" is the same in all languages.
- **Design** follows `design/DESIGN.md` ("heath at low sun", approved 2026-11-24): one fixed day-to-night
  look, no dark mode, self-hosted Hanken Grotesk. Amber is a text colour on the dark grounds only.
- **Open slots** (files that will come later) are marked with `data-slot` in the HTML and listed in
  `SLOTS` in `scripts/check.py` and in `README.md`. When a file lands, keep the path and remove the
  path from `SLOTS`.

## Before committing

Run `python3 scripts/check.py`. It must pass.
