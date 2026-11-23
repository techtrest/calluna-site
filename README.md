# calluna-site

Landing page for Calluna at https://callunalist.app. Static HTML + one stylesheet; no build step,
no JavaScript, no cookies, no analytics, nothing loaded from other servers. Rules for editing are
in `CLAUDE.md`.

Everything that is served lives in `site/`. The rest of the repo (`CLAUDE.md`, `README.md`,
`netlify.toml`, `scripts/`) is never published.

| Language | URL | File |
|---|---|---|
| English | `/` | `site/index.html` |
| German | `/de/` | `site/de/index.html` |
| Polish | `/pl/` | `site/pl/index.html` |

The Polish text has been reviewed by the Polish reviewer. Any future change to it goes to the
Polish reviewer before it ships.

## Deploy

Netlify, from this repo:

- Build command: none. Publish directory: `site`. Both are set in `netlify.toml` at the repo root,
  so the Netlify UI fields can stay empty.
- `netlify.toml` also sets the security headers (CSP with `script-src 'none'`, `frame-ancestors
  'none'`, `Referrer-Policy: no-referrer`, `nosniff`, and a Permissions-Policy that denies camera,
  microphone and geolocation).
- Custom domain `callunalist.app` with Netlify's HTTPS. The canonical, hreflang and og:url tags
  assume that domain.

Every push to `main` deploys. Before pushing:

```sh
python3 scripts/check.py
```

It must print `PASS`. It also lists the slots that are still open.

To preview locally, run `python3 -m http.server -d site` and open http://localhost:8000/.
Paths are root-absolute, so opening the files directly with `file://` won't load the CSS.

## Open slots

The HTML references these files already. Each one is marked `data-slot` with a `<!-- SLOT -->`
comment, and they are listed in `SLOTS` in `scripts/check.py`. To fill a slot, drop the file at
exactly this path and remove the path from `SLOTS`. If the path is still in `SLOTS` after the file
lands, `check.py` fails.

| Slot | Path | Size / notes |
|---|---|---|
| Google Play badge ×3 | `site/assets/badges/google-play-{en,de,pl}.png` | Google's official localized badges. Shown at 56 px tall, width follows the file. Already linked to the Play listing. |
| Open Graph image | `site/assets/og/calluna-og.png` | 1200 × 630, shared by all three languages. |
| Press kit | `site/press/calluna-press-kit.zip` | Linked from the press section in all three languages. |

Still to shoot, with no page slot yet: the **notification shot** (partner's push in the
notification shade). It needs a second phone; see
`ShoppingApp/docs/screens/marketing-2026-11/review.json`, item 4.

## Screenshots (temporary)

`site/assets/screens/{en,de,pl}/` holds the raw marketing shots from
`ShoppingApp/docs/screens/marketing-2026-11/{en,de,pl}/raw/`, converted to WebP. They stand in until
the framed images from Claude Design arrive.

| File | Size | Used for |
|---|---|---|
| `sync.webp`, `add.webp`, `shops.webp` | 1080 × 2400 (frame is 9:20) | The three how-it-works items, in that order |
| `hero.webp` | 1200 × 1200 (frame is 1:1) | Hero; for now the sync shot scaled to 540 × 1200 with rounded corners, centred on a transparent canvas |

To replace them, keep the file names, or update the `src` in all three pages. The alt texts are
final copy from the Calluna project chat; change them only if the new image shows something
different. `check.py` fails on any image in `site/` over 250 KB.

The app icon (`site/assets/icons/calluna-512.png` and its 180/64/32 px versions) comes from
`ShoppingApp/app/src/main/ic_launcher-playstore.png`.
