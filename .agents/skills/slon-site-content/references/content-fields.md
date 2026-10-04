# Content JSON

| Field | Meaning |
| --- | --- |
| `type` | Required: `film`, `book`, `news`, or `page` for a standalone studio page. |
| `slug` | Required: lowercase letters/digits separated by hyphens, without `.html`; must match the JSON filename. Do not use index, films, books, news, testimonials, contact, ourwork or projects. |
| `title` | Required: complete page title, also used as `h1`. |
| `description` | Required: specific short summary for search metadata and fallback teaser. |
| `paragraphs` | Required: plain-text paragraph array. It may be empty when `sections` contains the text. HTML is escaped; newline characters become line breaks. |
| `display_title` | Optional short `h1` when the search title is longer (for example «Неля»). |
| `card_title` | Optional shorter title for homepage/catalog cards. |
| `teaser` | Optional short text for homepage/catalog cards; does not replace full paragraphs. |
| `label` | Optional genre, author, or project context on the page and card. |
| `image` | Optional existing repository-relative path under `images/`. |
| `image_alt` | Required with an image: Russian description. Dimensions are read from JPEG/PNG/GIF automatically. |
| `gallery` | Optional array of `{ "image": "images/…", "image_alt": "…" }` for film frames. |
| `sections` | Optional array of `{ "heading": "…", "paragraphs": ["…"] }`. Each becomes `h2`; film pages receive a table of contents. |
| `links` | Optional array of `{ "label": "…", "url": "https://…" }` for reading, viewing, or sources. Only HTTP/HTTPS. |
| `date` | Optional date stated by the source, `YYYY-MM-DD`. Omit when unknown; do not confuse a dated announcement with a film's release year. |

Film, book, news and studio entries are registered in the corresponding arrays
of `content/site.json`. `featured_news` is an editorial selection, not an
inferred publication-date sort. Keep each title and description specific to its
page. Existing source files under `content/site/` are complete; draft examples
under `content/examples/` contain abbreviated text and are not migration sources.

```sh
python3 scripts/render-content.py --build
python3 scripts/render-content.py content/site/book-oda-moskve.json --replace
python3 scripts/render-content.py --home
```

`--build` replaces generated root pages and sitemap. Single-entry commands create
`docs/design/examples/<slug>.html` and refuse to overwrite without `--replace`.
A custom `--output-dir` must remain under `docs/design/`.
