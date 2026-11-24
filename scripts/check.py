#!/usr/bin/env python3
"""Static checks for the Calluna landing page. Standard library only.

  python3 scripts/check.py

Checks:
  1. All three pages have the same sections (by id) in the same order, and the same number of
     "how it works" rows, privacy facts and crossed-off items.
  2. Every local link and asset path resolves to a file, or to an open slot: the element carries
     `data-slot` AND the path is listed in SLOTS below.
  3. No external URL except play.google.com, techtrest.github.io and mailto:. Absolute
     https://callunalist.app/ URLs (canonical, hreflang, og:*) are the site itself and must resolve
     locally like any other path.
  4. No <script>, no inline <style> or style="", no on*= handlers, no external stylesheet or font
     (in the HTML or in the CSS). Every inline <svg> is aria-hidden, every <img> has width, height
     and alt, and no image in site/ is over MAX_IMAGE_KB.
  5. Nothing outside site/ (the Netlify publish dir) is referenced by the pages or the CSS.
  6. Every section except the hero has its own <h2>.
  7. No personal names in any tracked file. One exception: the developer's first name (VISIBLE_NAME)
     in the visible body text of the pages in VISIBLE_NAME_PAGES, never in their markup.
  8. Draft strings: each one is marked with a "draft, needs review" comment and counted in REVIEWS;
     no draft mark anywhere else, and none in the visible text.
Plus: hreflang set complete on every page; CSP header present in netlify.toml.

Exit code 0 = pass, 1 = fail.
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"            # Netlify publish dir; URL "/" maps here
SITE_HOST = "callunalist.app"
ALLOWED_HOSTS = {"play.google.com", "techtrest.github.io"}

PAGES = {"en": "index.html", "de": "de/index.html", "pl": "pl/index.html"}
URL_PATHS = {"en": "/", "de": "/de/", "pl": "/pl/"}

# Open slots: files that come later. Remove a path here once its file is in the repo.
SLOTS = {
    "/assets/og/calluna-og.png",
    "/press/calluna-press-kit.zip",
}

# Open reviews: number of "draft, needs review" comments per page. Lower the count when a string has
# been reviewed and its comment is gone (and update "Open reviews" in README.md).
REVIEWS = {"en": 0, "de": 0, "pl": 3}
DRAFT_MARK = "draft, needs review"

# Images under site/ must stay small (the screenshots are WebP, ~20-40 KB each).
MAX_IMAGE_KB = 250
IMAGE_EXT = {".webp", ".png", ".jpg", ".jpeg", ".avif", ".gif", ".svg"}

# Personal names that must not appear in any tracked file. Spelled in pieces so this file doesn't
# trip its own check (and so `git grep` for them stays empty).
NAMES = ["Mon" + "ika", "Oli" + "ver"]
NAMES_RE = re.compile("|".join(NAMES), re.I)
# Allowed in the visible text of these two pages only: the story there is told in the first person.
VISIBLE_NAME = NAMES[1]
VISIBLE_NAME_PAGES = {SITE / PAGES["en"], SITE / PAGES["de"]}

URL_ATTRS = {"href", "src", "srcset", "poster", "action", "data", "formaction"}
URL_META = {"og:image", "og:url", "og:image:url", "og:image:secure_url", "twitter:image"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections = []          # ids of top-level <section>s, in order
        self.urls = []              # (url, has_data_slot, line)
        self.tags = []              # (tag, attrs, line)
        self.comments = []
        self.text = []
        self._skip = 0              # inside <head>/<title>/<style>: not visible body text
        self.feature_count = 0
        self.fact_count = 0
        self.crossed_count = 0
        self._ul = []               # class stack for <ul>
        self.h2_per_section = {}    # section id -> number of <h2> inside it
        self._section = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        self.tags.append((tag, a, line))
        if tag in ("head", "style", "script", "title"):
            self._skip += 1
        if tag == "section":
            self._section = a.get("id", "<no id>")
            self.sections.append(self._section)
            self.h2_per_section[self._section] = 0
        if tag == "h2" and self._section:
            self.h2_per_section[self._section] += 1
        if tag == "ul":
            self._ul.append(a.get("class", ""))
        if tag == "li" and self._ul:
            classes = self._ul[-1].split()
            if "rows" in classes:
                self.feature_count += 1
            if "facts" in classes:
                self.fact_count += 1
            if "crossed" in classes:
                self.crossed_count += 1
        slot = "data-slot" in a
        for k, v in a.items():
            if v is None:
                continue
            if k in URL_ATTRS:
                for part in (v.split(",") if k == "srcset" else [v]):
                    u = part.strip().split(" ")[0]
                    if u:
                        self.urls.append((u, slot, line))
        if tag == "meta" and (a.get("property") in URL_META or a.get("name") in URL_META):
            self.urls.append((a.get("content", ""), slot, line))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in ("head", "style", "script", "title"):
            self._skip -= 1

    def handle_endtag(self, tag):
        if tag in ("head", "style", "script", "title"):
            self._skip -= 1
        if tag == "ul" and self._ul:
            self._ul.pop()
        if tag == "section":
            self._section = None

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)

    def handle_comment(self, data):
        self.comments.append(data)


errors = []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def resolve_local(path):
    """Map a site path (/de/, /assets/x.png) to a file under site/."""
    p = unquote(path)
    target = SITE / p.lstrip("/")
    if p.endswith("/"):
        target = target / "index.html"
    return target


def outside_site(target):
    return not target.resolve().is_relative_to(SITE.resolve())


def check_url(where, url, slot, line, base):
    loc = f"{where}:{line}"
    if url.startswith("mailto:"):
        return
    if url.startswith("#"):
        return
    parts = urlsplit(url)
    if parts.scheme in ("http", "https"):
        if parts.hostname == SITE_HOST:
            path = parts.path or "/"
        elif parts.hostname in ALLOWED_HOSTS:
            if parts.scheme != "https":
                err(loc, f"external link must be https: {url}")
            return
        else:
            err(loc, f"external URL not allowed: {url}")
            return
    elif parts.scheme or url.startswith("//"):
        err(loc, f"URL scheme not allowed: {url}")
        return
    else:
        path = parts.path
        if not path.startswith("/"):
            path = base + path
    if outside_site(resolve_local(path)):
        err(loc, f"references a file outside site/: {url}")
        return
    if resolve_local(path).is_file():
        if path in SLOTS:
            err(loc, f"{path} exists now: remove it from SLOTS in scripts/check.py")
        return
    if slot and path in SLOTS:
        return
    if slot:
        err(loc, f"{path} is marked data-slot but not listed in SLOTS")
    else:
        err(loc, f"broken local path: {path}")


def main():
    parsed = {}
    for lang, rel in PAGES.items():
        f = SITE / rel
        rel = f"site/{rel}"
        if not f.is_file():
            err(rel, "missing")
            continue
        p = Page()
        p.feed(f.read_text(encoding="utf-8"))
        parsed[lang] = p

        # html lang
        html = next((a for t, a, _ in p.tags if t == "html"), {})
        if html.get("lang") != lang:
            err(rel, f'<html lang="{html.get("lang")}"> should be "{lang}"')

        # hreflang alternates
        alts = {a.get("hreflang"): a.get("href") for t, a, _ in p.tags
                if t == "link" and a.get("rel") == "alternate"}
        want = {l: f"https://{SITE_HOST}{URL_PATHS[l]}" for l in PAGES}
        want["x-default"] = f"https://{SITE_HOST}/"
        if alts != want:
            err(rel, f"hreflang alternates {alts} != {want}")

        # forbidden markup
        for t, a, line in p.tags:
            loc = f"{rel}:{line}"
            if t == "script":
                err(loc, "<script> is not allowed")
            if t == "style":
                err(loc, "inline <style> is not allowed (CSP style-src 'self')")
            if t in ("iframe", "object", "embed", "form"):
                err(loc, f"<{t}> is not allowed")
            if "style" in a:
                err(loc, 'style="" attribute is not allowed (CSP style-src \'self\')')
            if t == "svg" and a.get("aria-hidden") != "true":
                err(loc, "inline <svg> needs aria-hidden=\"true\"")
            if t == "img":
                for k in ("width", "height"):
                    if not (a.get(k) or "").isdigit():
                        err(loc, f"<img> needs a numeric {k}: {a.get('src')}")
                if "alt" not in a:
                    err(loc, f"<img> needs an alt: {a.get('src')}")
            for k in a:
                if k.startswith("on"):
                    err(loc, f"event handler attribute {k}= is not allowed")
            if t == "link" and a.get("rel") in ("stylesheet", "preload", "preconnect", "dns-prefetch", "modulepreload"):
                href = a.get("href", "")
                if urlsplit(href).scheme or href.startswith("//"):
                    err(loc, f"external {a.get('rel')} not allowed: {href}")

        # every URL
        for url, slot, line in p.urls:
            check_url(rel, url, slot, line, URL_PATHS[lang])

        # Review notes never reach the visible page; draft comments only where REVIEWS expects them.
        visible = " ".join(p.text)
        if re.search(r"draft|entwurf|szkic", visible, re.I):
            err(rel, "visible text mentions a draft")
        drafts = [c.strip() for c in p.comments if re.search(r"draft", c, re.I)]
        for c in drafts:
            if not c.startswith(DRAFT_MARK):
                err(rel, f'draft comment must start with "{DRAFT_MARK}": {c}')
        if len(drafts) != REVIEWS[lang]:
            err(rel, f"{len(drafts)} draft comments, REVIEWS says {REVIEWS[lang]}")

        # 6. headings: h1 in the hero, one h2 in every other section
        if sum(1 for t, _, _ in p.tags if t == "h1") != 1:
            err(rel, "needs exactly one <h1>")
        for sid, n in p.h2_per_section.items():
            if sid == "hero" and n:
                err(rel, "the hero has no section heading (<h2>)")
            if sid != "hero" and n != 1:
                err(rel, f'section "{sid}" has {n} <h2>, needs 1')

    # 1. same sections, same order
    if len(parsed) == len(PAGES):
        ref = parsed["en"]
        for lang, p in parsed.items():
            if p.sections != ref.sections:
                err(f"site/{PAGES[lang]}", f"sections {p.sections} != EN {ref.sections}")
            if p.feature_count != ref.feature_count:
                err(f"site/{PAGES[lang]}", f"{p.feature_count} how-it-works rows, EN has {ref.feature_count}")
            if p.fact_count != ref.fact_count:
                err(f"site/{PAGES[lang]}", f"{p.fact_count} privacy facts, EN has {ref.fact_count}")
            if p.crossed_count != ref.crossed_count:
                err(f"site/{PAGES[lang]}", f"{p.crossed_count} crossed-off items, EN has {ref.crossed_count}")
        for what, n in (("how-it-works rows", ref.feature_count), ("privacy facts", ref.fact_count),
                        ("crossed-off items", ref.crossed_count)):
            if not n:
                err("site/index.html", f"no {what} found")
        if not ref.sections:
            err("site/index.html", "no <section>s found")

    # CSS: no @import; url() only for local files (this covers @font-face too)
    for css in SITE.rglob("*.css"):
        rel = css.relative_to(SITE)
        src = re.sub(r"/\*.*?\*/", "", css.read_text(encoding="utf-8"), flags=re.S)
        if re.search(r"@import", src):
            err(str(rel), "@import is not allowed")
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)", src):
            u = m.group(1)
            if urlsplit(u).scheme or u.startswith("//"):
                err(str(rel), f"external url() not allowed: {u}")
            elif not u.startswith("data:"):
                base = "/" + str(rel.parent).strip(".") + "/"
                target = resolve_local(u if u.startswith("/") else base + u)
                if outside_site(target):
                    err(f"site/{rel}", f"url() points outside site/: {u}")
                elif not target.is_file():
                    err(f"site/{rel}", f"broken url(): {u}")

    # No stray JS files in the publish dir
    for js in SITE.rglob("*.js"):
        err(str(js.relative_to(ROOT)), "JavaScript files are not allowed")

    for img in SITE.rglob("*"):
        if img.suffix.lower() in IMAGE_EXT and img.stat().st_size > MAX_IMAGE_KB * 1024:
            err(str(img.relative_to(ROOT)), f"{img.stat().st_size // 1024} KB, over {MAX_IMAGE_KB} KB")

    # 7. No personal names in any tracked file (text or binary metadata).
    try:
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True,
                                 capture_output=True).stdout.decode().split("\0")
        files = [ROOT / t for t in tracked if t]
    except (OSError, subprocess.CalledProcessError):
        files = [f for f in ROOT.rglob("*") if f.is_file() and ".git" not in f.parts]
    for f in files:
        if f.is_file():
            found = NAMES_RE.findall(f.read_bytes().decode("latin-1"))
            if f in VISIBLE_NAME_PAGES:
                # Drop one match per visible occurrence; comments, attributes and <head> stay caught.
                page = Page()
                page.feed(f.read_text(encoding="utf-8"))
                for _ in range(" ".join(page.text).count(VISIBLE_NAME)):
                    if VISIBLE_NAME in found:
                        found.remove(VISIBLE_NAME)
            if found:
                err(str(f.relative_to(ROOT)), f"contains a personal name: {found[0]}")

    # Netlify headers
    toml = (ROOT / "netlify.toml").read_text(encoding="utf-8")
    for needle in ("Content-Security-Policy", "script-src 'none'", "frame-ancestors 'none'",
                   "Referrer-Policy = \"no-referrer\"", "X-Content-Type-Options = \"nosniff\"",
                   "camera=()", "microphone=()", "geolocation=()"):
        if needle not in toml:
            err("netlify.toml", f"missing: {needle}")

    open_slots = sorted(s for s in SLOTS if not resolve_local(s).is_file())
    print(f"Open slots ({len(open_slots)}):")
    for s in open_slots:
        print(f"  {s}")
    print(f"Open reviews: {', '.join(f'{l} {n}' for l, n in REVIEWS.items() if n) or 'none'}")
    if errors:
        print(f"\nFAIL ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        return 1
    print(f"\nPASS: {', '.join('site/' + v for v in PAGES.values())}; sections: {' > '.join(parsed['en'].sections)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
