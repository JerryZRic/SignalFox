"""URL fetching and HTML text extraction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import re
import ssl
from urllib.request import Request, urlopen

BLOCK_TAGS = {
    "article",
    "aside",
    "blockquote",
    "br",
    "dd",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hr",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "section",
    "table",
    "tr",
    "ul",
}
IGNORED_TAGS = {"footer", "header", "nav", "noscript", "script", "style", "svg"}


@dataclass(slots=True)
class FetchedPage:
    """Normalized content fetched from a URL."""

    url: str
    title: str
    content: str


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._title_parts: list[str] = []
        self._segments: list[str] = []
        self._in_title = False
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in IGNORED_TAGS:
            self._ignored_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in BLOCK_TAGS:
            self._push_break()

    def handle_endtag(self, tag: str) -> None:
        if tag in IGNORED_TAGS and self._ignored_depth > 0:
            self._ignored_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in BLOCK_TAGS:
            self._push_break()

    def handle_data(self, data: str) -> None:
        if self._ignored_depth > 0:
            return
        normalized = " ".join(unescape(data).split())
        if not normalized:
            return
        if self._in_title:
            self._title_parts.append(normalized)
            return
        self._segments.append(normalized)

    @property
    def title(self) -> str:
        return " ".join(self._title_parts).strip()

    @property
    def body_text(self) -> str:
        lines: list[str] = []
        current_parts: list[str] = []
        for segment in self._segments:
            if segment == "\n\n":
                self._flush_line(current_parts, lines)
                continue
            current_parts.append(segment)
        self._flush_line(current_parts, lines)
        return "\n".join(lines).strip()

    def _push_break(self) -> None:
        if not self._segments:
            return
        if self._segments[-1] != "\n\n":
            self._segments.append("\n\n")

    def _flush_line(self, current_parts: list[str], lines: list[str]) -> None:
        if not current_parts:
            return
        line = " ".join(current_parts).strip()
        line = re.sub(r"\s+([,.;:!?])", r"\1", line)
        current_parts.clear()
        if not line:
            return
        if lines and lines[-1] == line:
            return
        lines.append(line)


def truncate_text(text: str, max_chars: int | None = None) -> str:
    """Trim text to a target size while preserving a clean ending."""

    if max_chars is None or max_chars <= 0 or len(text) <= max_chars:
        return text

    truncated = text[:max_chars].rstrip()
    cutoff = max(truncated.rfind("\n"), truncated.rfind(" "))
    if cutoff >= max_chars // 2:
        truncated = truncated[:cutoff].rstrip()
    return truncated + "\n... [truncated]"


def fetch_url_text(url: str, timeout: int = 20, verify_tls: bool = True) -> FetchedPage:
    """Fetch a URL and extract a readable title and text body."""

    request = Request(
        url,
        headers={
            "User-Agent": "SignalFox/0.1 (+https://github.com/JerryZRic/SignalFox)",
        },
    )
    context = ssl.create_default_context()
    if not verify_tls:
        context = ssl._create_unverified_context()

    with urlopen(request, timeout=timeout, context=context) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="replace")

    parser = _HTMLTextExtractor()
    parser.feed(html)

    title = parser.title or url
    content = parser.body_text or title
    return FetchedPage(url=url, title=title, content=content)
