"""Checks that the GitHub Pages landing page (docs/index.html) stays agent-readable.

AI crawlers read the text inside <main>, the JSON-LD, and the Markdown twin that
<link rel="alternate" type="text/markdown"> points at. These tests keep those in
step with the HTML without touching the network.

The custom 404 page (docs/404.html) gets the same treatment: GitHub Pages serves it
for every missing path under the project, so it must stay a real noindex 404 that
hands agents short Markdown pointers and whose links work at any URL depth.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "langchain-fde-curriculum"
HTML = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
MD = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
NOT_FOUND = (ROOT / "docs" / "404.html").read_text(encoding="utf-8")


def section(tag: str, doc: str = HTML) -> str:
    """Inner HTML of the single <tag>…</tag> element in doc."""
    found = re.findall(rf"<{tag}\b[^>]*>(.*?)</{tag}>", doc, re.S | re.I)
    assert len(found) == 1, f"expected exactly one <{tag}>, found {len(found)}"
    return found[0]


def squash(text: str) -> str:
    """Collapse whitespace and drop the characters Markdown adds for emphasis/code."""
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "").replace("\\", "")).strip()


def block_text(fragment: str) -> str:
    """Visible text of one HTML block: <br> becomes a space, other tags vanish."""
    fragment = re.sub(r"<br\b[^>]*>", " ", fragment, flags=re.I)
    return squash(html.unescape(re.sub(r"<[^>]+>", "", fragment)))


def twin_plain(md: str) -> str:
    """The Markdown twin as plain text: no code blocks, links and images reduced to their text."""
    text = re.sub(r"```.*?```", " ", md, flags=re.S)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"(?m)^>\s?", "", text)
    return squash(text)


def text_blocks(main_html: str) -> list[str]:
    """Every paragraph and list item inside <main>, as plain text (empty ones dropped)."""
    blocks = re.findall(r"<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>", main_html, re.S | re.I)
    return [t for t in (block_text(b) for b in blocks) if t]


def test_h1_and_content_live_inside_main():
    main = section("main")
    assert len(re.findall(r"<h1\b", HTML, re.I)) == 1, "exactly one <h1>"
    assert len(re.findall(r"<h1\b", main, re.I)) == 1, "the <h1> must be inside <main>"
    assert len(block_text(main)) >= 500, "500+ chars of text inside <main>"
    # Boilerplate-stripping extractors drop <header>/<nav>/<aside>/<footer> elements before counting.
    found = re.findall(r"<(header|nav|aside|footer)\b", main, re.I)
    assert found == [], f"boilerplate element(s) inside <main> would hide content: {found}"


def test_head_advertises_markdown_twin_and_llms_txt():
    head = section("head")
    assert f'<link rel="alternate" type="text/markdown" href="/{SLUG}/index.md"' in head
    assert '<link rel="describedby" href="/llms.txt">' in head
    assert 'href="https://tatendaz.github.io/llms.txt"' in section("footer")


def test_markdown_twin_mirrors_the_page():
    assert MD.startswith("# "), "twin must start with an H1"
    assert MD.splitlines()[0][2:].strip() == block_text(section("h1"))
    md_h2s = [line[3:].strip() for line in MD.splitlines() if line.startswith("## ")]
    for h2 in re.findall(r"<h2\b[^>]*>(.*?)</h2>", HTML, re.S | re.I):
        # Whole-line match: "### Heading" contains "## Heading" but is not an H2.
        assert block_text(h2) in md_h2s, f"twin is missing the H2: {block_text(h2)!r}"
    assert f"HTML version: https://tatendaz.github.io/{SLUG}/" in MD
    assert "https://tatendaz.github.io/llms.txt" in MD
    assert not re.search(r"<(div|span|script|style)\b", MD), "twin must be plain Markdown"


def test_markdown_twin_carries_every_paragraph():
    blocks = text_blocks(section("main"))
    assert len(blocks) >= 10
    plain = twin_plain(MD)
    for block in blocks:
        assert block in plain, f"twin is missing the text: {block[:80]!r}"


def test_404_page_is_a_noindex_dead_end_with_markdown_pointers():
    assert "404" in block_text(section("title", NOT_FOUND))
    assert '<meta name="robots" content="noindex">' in section("head", NOT_FOUND)
    # A 404 is not a document: nothing to canonicalise and no Markdown twin to advertise.
    assert not re.search(r'<link\b[^>]*\brel="(?:canonical|alternate)"', NOT_FOUND, re.I)

    main = section("main", NOT_FOUND)
    assert block_text(section("h1", NOT_FOUND)) == "Page not found"
    assert re.findall(r"<(header|nav|aside|footer)\b", main, re.I) == []
    assert len(block_text(main)) < 1500, "keep the 404 short"

    blocks = re.findall(r'<pre class="md"[^>]*>(.*?)</pre>', main, re.S)
    assert len(blocks) == 1, 'exactly one <pre class="md"> inside <main>'
    md = html.unescape(blocks[0]).strip()
    assert md.startswith("# 404")
    assert "## Where to look next" in md
    assert "- [Site map](https://tatendaz.github.io/sitemap.xml)" in md
    assert "- [llms.txt](https://tatendaz.github.io/llms.txt)" in md
    assert f"https://tatendaz.github.io/{SLUG}/" in md
    assert len(md) < 700, "the Markdown pointers must stay short"
    assert not re.search(r"<[a-z]+[\s>]", md), "the Markdown block must be plain text, no HTML"


def test_404_page_urls_work_at_any_depth():
    # GitHub Pages serves 404.html for every missing path, however deep
    # (/langchain-fde-curriculum/a/b/c), so a relative URL would resolve against the
    # wrong directory. Every URL must be absolute; the favicon is a data: URI, which
    # has no path to resolve.
    urls = re.findall(r'\b(?:href|src)="([^"]*)"', NOT_FOUND)
    assert urls, "the 404 page must link somewhere"
    for url in urls:
        assert url.startswith((f"/{SLUG}/", "http://", "https://", "mailto:", "#", "data:")), url
