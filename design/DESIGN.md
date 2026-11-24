# Design: heath at low sun

The approved look of callunalist.app. Code: `site/assets/site.css` and the inline SVGs in the pages.
Renders: `design/renders/`.

## Direction

The page is one landscape, walked from late afternoon to night. The hero is a warm sky with the sun
low over the hills; its near ground is the floor of "How it works"; the middle sections are plain
daylight paper; press and footer are the same heath after sunset. The look is fixed: there is no
dark mode, because the page already goes from day to night.

Privacy is written like the app's own list. What is true stands as open items; what Calluna leaves
out (ads, analytics, tracking tools) is ticked and crossed off below them.

| Section | Ground | What carries it |
|---|---|---|
| Nav + hero | Sky | Big headline, Play badge, invite link; two tilted phones standing in the landscape |
| How it works | Heath ground | Three rows, phone and text side by side, alternating; cropped phones fade into the ground; row 3 adds the enlarged shop bar |
| Why Calluna | Page | Heading left, story right, last sentence semibold |
| Privacy | Surface | The list, the honest note, the policy link |
| Invite | Page | Heading left, text right |
| Press + footer | Night | Night hills with moon and cypress, press text, footer line |

## Colour roles

| Role | Value | Used for |
|---|---|---|
| Sky | `#FBEBC8` | Nav and hero |
| Page | `#F5F3EC` | Why, invite, open list items; text on the heath ground |
| Surface | `#ECE7DA` | Privacy |
| Done item | `#E2DED1` | Crossed-off items |
| Ink | `#1C1B1F` | All text on light grounds, phone frames |
| Heath ground | `#2E3A30` | How it works, near ground, tick circles |
| Amber | `#D89B45` | Sun, link underlines, shop-bar border, ticks; as text only on the heath ground and the night |
| Night | `#1C1B1F` | Press and footer; text `#E6E1E5`, links `#F5F3EC`, rule `#3A383F` |
| Landscape | `#9AAA86` far hill, `#4F6B55` mid hill, `#1F2A22` cypress, `#A85E7C` heather | Drawing only, never text |
| Night landscape | `#26302A` hill, `#141813` cypress, `#F0D9A3` moon | Drawing only, never text |

All text meets WCAG AA. Amber is never a text colour on a light ground (about 2:1).

## Type

Hanken Grotesk, self-hosted, system sans as the fallback.

| Role | Size | Weight |
|---|---|---|
| Headline | 56–104 px, line height 0.98, tracking −0.02 em | 700 |
| Section heading | 34–44 px, 1.1 | 700 |
| Row heading | 28–36 px, 1.15 | 700 |
| Subline | 20–22 px, at most 30 characters wide | 400 |
| Story | 20–24 px | 400, last sentence 600 |
| Row text | 18–21 px, at most 32 characters wide | 400 |
| List items | 19 px | 500 |
| Group label, footer | 15 px | 600 / 400 |

## The landscape

The landscape (low amber sun, two hills, the lone cypress, a few heather dots, dark near ground) is
an approved brand element next to the app icon, which shows the same scene. The night version keeps
the hill line and the cypress and swaps the sun for a moon.

- It is an inline SVG, `aria-hidden`, scaled with `xMidYMax slice` (night: `xMidYMin slice`).
- The cypress is always in view and always alone. It stands left, clear of text and phones.
- The sun sits low, half behind the far hill, and stays visible beside the phones.
- Below 1112 px the drawing keeps a fixed size and is pulled left; the sun, the moon and the heather move with CSS.
- Flat shapes only. Don't redraw, recolour or add to it without approval.

## Not

- No gradient washes. The one gradient is the mask that fades the cropped phones into the ground.
- No three equal feature cards.
- No badges or pills. The official Google Play badge is the only badge.
- No stock imagery.
- No emoji outside app screenshots.
