---
name: sidebar-news
description: Handle requests to add Slon media news in the former sidebar by using the site's current news-page and homepage-teaser workflow.
---

# Slon news placement

The site's redesign replaced the homepage sidebar with a news block and an
archive. For new or edited news, read
`../slon-site-content/SKILL.md` and use its shared content templates.

Create or update the full article under `content/site/`, register it in the
`news` array of `content/site.json`, and select it in `featured_news` when the
user wants it on the homepage. Then regenerate with
`python3 scripts/render-content.py --build`.

Preserve supplied Russian text and dates; an illustration is optional. Do not
restore `.sidebar_container` or insert hand-written blocks into generated
`index.html`. For an explicit request concerning a historical site revision,
inspect that revision's layout before editing it.
