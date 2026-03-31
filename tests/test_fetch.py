from signalfox.fetch import _HTMLTextExtractor, truncate_text


def test_html_text_extractor_cleans_block_structure_and_ignored_tags() -> None:
    parser = _HTMLTextExtractor()
    parser.feed(
        """
        <html>
          <head>
            <title>Example Story</title>
            <style>.hidden { display: none; }</style>
          </head>
          <body>
            <header>Site Header</header>
            <main>
              <article>
                <h1>Example Story</h1>
                <p>First paragraph.</p>
                <div>Second paragraph with <strong>detail</strong>.</div>
                <ul>
                  <li>Point one</li>
                  <li>Point two</li>
                </ul>
              </article>
            </main>
            <footer>Footer links</footer>
            <script>console.log('ignore me');</script>
          </body>
        </html>
        """
    )

    assert parser.title == "Example Story"
    assert parser.body_text == (
        "Example Story\n"
        "First paragraph.\n"
        "Second paragraph with detail.\n"
        "Point one\n"
        "Point two"
    )


def test_html_text_extractor_deduplicates_adjacent_lines() -> None:
    parser = _HTMLTextExtractor()
    parser.feed(
        """
        <html>
          <head><title>Duplicate Example</title></head>
          <body>
            <p>Repeated line.</p>
            <div>Repeated line.</div>
            <p>Different line.</p>
          </body>
        </html>
        """
    )

    assert parser.body_text == "Repeated line.\nDifferent line."


def test_truncate_text_adds_marker_when_content_is_trimmed() -> None:
    text = "alpha beta gamma delta epsilon"

    truncated = truncate_text(text, 12)

    assert truncated == "alpha beta\n... [truncated]"


def test_truncate_text_returns_original_when_under_limit() -> None:
    text = "short text"

    assert truncate_text(text, 100) == text
