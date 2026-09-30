---
name: sidebar-news
description: Add or update news entries in the left sidebar of the Slon media static website, with or without a cover image.
---

# Sidebar News

Use this skill for requests to publish a new sidebar news entry on the Slon media site. Do not use it for main-content news pages, unrelated sidebar blocks, or site-wide redesigns.

The homepage sidebar is in `index.html`, inside `.sidebar_container > .sidebar`; each entry is a `.sidebar_item`. Place a new news item before the existing block headed `Новость`, unless the user specifies a different placement.

Include a suitable `<h2>` heading when one is supplied or can be unambiguously derived. Preserve the user's Russian text, XHTML-style markup, and the surrounding two-space indentation convention.

## Illustration

An illustration is optional. When one is attached, copy it into `images/` with a lowercase, hyphenated, descriptive filename. Add an `<img>` before the entry text, using a concise Russian `alt` that identifies the image or cover. Do not add an image element when no illustration is provided.

Existing sidebar CSS limits images to a responsive width; reuse it rather than adding inline dimensions or new styling unless the request explicitly calls for a layout change.

## Verification

Check the edited markup and image path. Run `git diff --check`; preserve unrelated working-tree changes.
