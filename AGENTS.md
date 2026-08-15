# Repository Guidelines

## Project Structure & Module Organization

This repository is a small static website for the Slon studio. HTML pages live
at the repository root: `index.html` is the main page, with `contact.html`,
`testimonials.html`, `ourwork.html`, and `projects.html` providing supporting
pages. Shared presentation rules are in `css/style.css`; browser libraries and
site behavior are in `js/`. Put site images in `images/`, keeping related photo
sets in a descriptive subdirectory such as `images/photos/`. `CNAME` configures
the published custom domain.

## Build, Test, and Development Commands

There is no package manager, compilation step, or automated test suite. Review
changes by opening the affected HTML page in a browser and checking navigation,
images, links, and layout at typical desktop and mobile widths.

Build the production image with:

```sh
docker build -t slon.media .
docker run --rm -p 8080:80 slon.media
```

Then visit `http://localhost:8080`. The `Dockerfile` copies the repository into
the standard Nginx web root. CI configuration in `.drone.yml` currently only
lists the workspace before publishing the Docker image.

## Coding Style & Naming Conventions

Preserve the existing XHTML-style markup and UTF-8 Russian content. Use two
spaces for new HTML indentation and follow the surrounding formatting when
editing an existing block. Reuse existing IDs and CSS selectors; use lowercase,
hyphenated names for new classes and asset filenames (for example,
`images/behind-the-scenes.jpg`). Keep relative paths valid from the page that
uses them. Do not reformat vendored files under `js/`.

## Testing Guidelines

Manually verify every edited page, including linked images and JavaScript-driven
elements such as the homepage slider. For content changes, confirm that the
Russian text renders correctly and that external links open the intended target.

## Commit & Pull Request Guidelines

Recent history uses short, imperative summaries in either Russian or English,
such as `Добавил ссылку.` or `Add CNAME.` Keep commits focused on one content or
layout change. Pull requests should state the pages changed, summarize visible
effects, link any relevant issue, and include screenshots for visual updates.
