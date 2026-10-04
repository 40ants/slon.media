---
name: slon-site-content
description: Add or update film, book, and news pages on the Slon media site using its shared templates, styles, and JSON content sources. Use for new projects, publication news, and homepage teasers.
---

# Slon site content

Resolve paths from the Slon media repository root. All published root HTML is
regenerated from sources. Do not edit generated pages directly.

## Sources and shared design

- `content/site/*.json`: complete film, book, news and studio texts.
- `content/site.json`: ordered film/book/news lists and homepage news selection.
- `content/team.json`: participant groups, biographies, portraits and partners.
- `templates/content/base.html`: shared header, navigation, metadata and footer.
- `templates/content/home.html`: homepage sections with generated project cards.
- `templates/content/film.html`, `book.html`, `news.html`, `page.html`: page bodies.
- `templates/content/contact.html`: contact content, direct form link and iframe.
- `css/style.css`: the single stylesheet for published pages and design previews.

The chosen style is a light lilac-white background, muted purple links, Georgia
headings and Arial body text. Reuse shared components and responsive rules; make
site-wide visual changes in the templates or stylesheet, not per-page inline CSS.
Film posters and book covers in homepage/catalog cards must link to the
corresponding detail page, including film title tiles without an image. The
shared card renderer in `scripts/render-content.py` provides these links.

## Adding a film, book or news item

1. Use supplied Russian author text and real assets. Do not invent release dates,
   credits, availability, contact addresses, or purchase links. Preserve full
   existing material during updates; homepage teasers may be shorter.
2. Create `content/site/<slug>.json` using the
   [content fields](references/content-fields.md). Copy a relevant source file
   as a starting point. Put images under `images/`, use descriptive lowercase
   hyphenated names, and supply meaningful Russian `image_alt` text.
3. Add the slug to its section in `content/site.json`. The list order controls
   the catalog and homepage film/book cards. `featured_news` controls the
   homepage news block and may refer to a book announcement or a news article.
4. Run `python3 scripts/render-content.py --build`. This regenerates root pages,
   navigation, catalog cards and `sitemap.xml` with unique page metadata.
5. Review the edited page, its catalog and homepage teaser in a browser at desktop
   and phone widths. Verify image paths, links, keyboard focus and `git diff --check`.

For a requested draft before adding the item to the site manifest, run
`python3 scripts/render-content.py content/site/<slug>.json`. Drafts stay under
`docs/design/`, use `noindex`, and are excluded from the Docker production image.
Use `--replace` to intentionally update an existing draft.

## Related changes

The former sidebar is gone. A request to add a news item to the sidebar usually
means adding a news page and selecting it in `featured_news`; explain that
placement when needed. Actual historical-layout requests should use the prior
revision, not recreate the obsolete sidebar in the new homepage.

For team changes edit `content/team.json`; for contact changes edit the contact
body template. Existing `testimonials.html` and `contact.html` addresses remain.
`ourwork.html` and `projects.html` are legacy redirects; do not add real content
there without changing their routing intentionally.

Changing templates requires regenerating published pages with `--build`. Refresh
`docs/design/home-wireframe.html` using `--home` only when its preview is needed.
Building locally does not authorize deployment, Git pushes, or external messages.
