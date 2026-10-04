#!/usr/bin/env python3
"""Generate static Slon pages from shared templates and JSON content."""
import argparse
from datetime import date
from html import escape
import json
import os
from pathlib import Path
import re
import struct
from string import Template
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'templates' / 'content'
SECTIONS = {'film': ('films', 'Фильмы'), 'book': ('books', 'Книги'), 'news': ('news', 'Новости'), 'page': ('about', 'О студии')}
NAVIGATION = [('films', 'Фильмы'), ('books', 'Книги'), ('testimonials', 'Команда'), ('contact', 'Контакты')]
RESERVED_SLUGS = {'index', 'films', 'books', 'news', 'testimonials', 'contact', 'ourwork', 'projects'}


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Text fields must contain non-empty strings')
    return escape(value, quote=True)


def valid_slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
        raise ValueError('slug must be a lowercase hyphenated filename without an extension')
    return value


def link_url(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        raise ValueError('Links must be URLs without whitespace')
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        raise ValueError('External links must use http or https')
    return escape(value, quote=True)


def image_size(path):
    raw = path.read_bytes()
    if raw[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', raw[16:24])
    if raw[:3] == b'GIF':
        return struct.unpack('<HH', raw[6:10])
    if raw[:2] == b'\xff\xd8':
        offset = 2
        while offset < len(raw):
            if raw[offset] != 255:
                break
            while raw[offset] == 255:
                offset += 1
            marker = raw[offset]
            offset += 1
            if marker in (0xD8, 0xD9):
                continue
            length = int.from_bytes(raw[offset:offset + 2], 'big')
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                height, width = struct.unpack('>HH', raw[offset + 3:offset + 7])
                return width, height
            offset += length
    raise ValueError('Cannot read image dimensions: ' + str(path))


def image_html(data, prefix, css_class, lazy=False):
    if not data.get('image'):
        return ''
    path = Path(data['image'])
    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != 'images':
        raise ValueError('image must be a repository-relative path under images/')
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT / 'images') or not resolved.is_file():
        raise ValueError('Image file does not exist: ' + str(path))
    width, height = image_size(resolved)
    loading = ' loading="lazy"' if lazy else ''
    return '<img class="' + css_class + '" src="' + escape(prefix + '/' + path.as_posix(), quote=True) + '" alt="' + text(data['image_alt']) + '" width="' + str(width) + '" height="' + str(height) + '"' + loading + ' decoding="async" />'


def paragraphs_html(paragraphs):
    if not isinstance(paragraphs, list) or not paragraphs:
        raise ValueError('paragraphs must be a non-empty list')
    return '\n'.join('<p>' + text(p).replace('\n', '<br />\n') + '</p>' for p in paragraphs)


def links_html(links):
    if not links:
        return ''
    items = ['<li><a href="' + link_url(item['url']) + '" target="_blank" rel="noopener">' + text(item['label']) + '</a></li>' for item in links]
    return '<ul class="content-links">' + ''.join(items) + '</ul>'


def date_html(value):
    if not value:
        return ''
    published = date.fromisoformat(value)
    return '<time datetime="' + published.isoformat() + '">' + published.strftime('%d.%m.%Y') + '</time>'


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def navigation(prefix, active):
    return '\n        '.join('<a href="' + escape(prefix, quote=True) + '/' + slug + '.html"' + (' aria-current="page"' if slug == active else '') + '>' + label + '</a>' for slug, label in NAVIGATION)


def shell(title, description, content, slug, prefix='.', active='', draft=False, lead='', page_class='article-page', image=None):
    title, description = text(title), text(description)
    document_title = title if 'Слон' in title else title + ' — Слон'
    canonical = 'https://slon.media/' + ('' if slug == 'index' else valid_slug(slug) + '.html')
    if draft:
        metadata = '<meta name="robots" content="noindex, nofollow" />'
        analytics = ''
    else:
        metadata = '<link rel="canonical" href="' + canonical + '" />\n  <meta property="og:title" content="' + document_title + '" />\n  <meta property="og:description" content="' + description + '" />\n  <meta property="og:url" content="' + canonical + '" />\n  <meta property="og:type" content="website" />'
        if image:
            metadata += '\n  <meta property="og:image" content="https://slon.media/' + text(image) + '" />'
        analytics = (TEMPLATES / 'analytics.html').read_text()
    page = Template((TEMPLATES / 'base.html').read_text()).substitute(
        title=title, document_title=document_title, description=description, content=content, asset_prefix=escape(prefix, quote=True),
        metadata=metadata, navigation=navigation(prefix, active), page_class=page_class, page_lead=lead, analytics=analytics)
    return '\n'.join(line.rstrip() for line in page.splitlines()) + '\n'


def render(data, asset_prefix='.', draft=True):
    kind = data['type']
    if kind not in SECTIONS:
        raise ValueError('type must be film, book, news, or page')
    slug = valid_slug(data['slug'])
    if not data['paragraphs'] and not data.get('sections'):
        raise ValueError('Content must have paragraphs or sections')
    body = paragraphs_html(data['paragraphs']) if data['paragraphs'] else ''
    toc_items = []
    for number, section in enumerate(data.get('sections', []), 1):
        anchor = 'section-' + str(number)
        heading = text(section['heading'])
        body += '\n<h2 id="' + anchor + '">' + heading + '</h2>\n' + paragraphs_html(section['paragraphs'])
        toc_items.append('<li><a href="#' + anchor + '">' + heading + '</a></li>')
    toc = '<details class="article-toc"><summary>Содержание</summary><ul>' + ''.join(toc_items) + '</ul></details>' if toc_items else ''
    gallery = ''
    if data.get('gallery'):
        gallery_items = ['<a href="' + escape(asset_prefix + '/' + item['image'], quote=True) + '">' + image_html(item, asset_prefix, 'gallery-image', True) + '</a>' for item in data['gallery']]
        gallery = '<div class="film-gallery" aria-label="Кадры фильма">' + ''.join(gallery_items) + '</div>'
    rendered = Template((TEMPLATES / (kind + '.html')).read_text()).substitute(
        title=text(data.get('display_title', data['title'])), label=text(data.get('label', SECTIONS[kind][1])), body=body,
        image=image_html(data, asset_prefix, 'book-cover' if kind == 'book' else 'article-image'),
        links=links_html(data.get('links')), date=date_html(data.get('date')), gallery=gallery, toc=toc)
    section, section_label = SECTIONS[kind]
    lead = '<nav class="breadcrumbs" aria-label="Путь по сайту"><a href="' + escape(asset_prefix, quote=True) + '/index.html">Главная</a> / <a href="' + escape(asset_prefix, quote=True) + '/' + section + '.html">' + section_label + '</a></nav>' if kind != 'page' else ''
    if draft:
        lead = '<p class="eyebrow">Пример страницы · черновой макет</p>' + lead
    return slug, shell(data['title'], data['description'], rendered, slug, asset_prefix, section, draft, lead, image=data.get('image'))


def card(data, prefix, kind):
    slug = valid_slug(data['slug'])
    title = text(data.get('card_title', data['title']))
    if data.get('image') and kind in ('film', 'book'):
        illustration = image_html(data, prefix, 'cover' if kind == 'book' else 'film-frame', True)
    elif kind == 'film':
        illustration = '<div class="film-title-frame" aria-hidden="true">' + title + '</div>'
    else:
        illustration = ''
    action = {'film': 'О фильме', 'book': 'О книге', 'news': 'Читать новость'}[data['type']]
    label = date_html(data.get('date')) if kind == 'news' else text(data.get('label', SECTIONS[kind][1]))
    meta = '<p class="meta">' + label + '</p>' if label else ''
    href = escape(prefix, quote=True) + '/' + slug + '.html'
    if illustration:
        illustration = '<a class="project-cover" href="' + href + '" aria-label="' + action + ' «' + title + '»">' + illustration + '</a>'
    card_class = 'news-card' if kind == 'news' else kind
    return '<article class="project-card ' + card_class + '">\n' + illustration + meta + '<h3><a href="' + href + '">' + title + '</a></h3><p>' + text(data.get('teaser', data['description'])) + '</p><a class="project-link" href="' + href + '">' + action + '</a></article>'


def home(manifest, entries, prefix='.', draft=False):
    values = {
        'intro': text(manifest['home_intro']),
        'films': ''.join(card(entries[s], prefix, 'film') for s in manifest['films']),
        'books': ''.join(card(entries[s], prefix, 'book') for s in manifest['books']),
        'news': ''.join(card(entries[s], prefix, 'news') for s in manifest['featured_news']),
        'asset_prefix': escape(prefix, quote=True),
    }
    body = Template((TEMPLATES / 'home.html').read_text()).substitute(values)
    return shell(manifest['home_title'], manifest['home_description'], body, 'index', prefix, draft=draft, page_class='home-page')


def listing(kind, slugs, entries):
    section, title = SECTIONS[kind]
    intros = {'film': 'Короткометражные фильмы и авторские работы студии «Слон».', 'book': 'Книги Марии Артеменко-Якушевой: рассказы, детективы и фантастика.', 'news': 'Новости студии и авторских проектов. Здесь сохранены и первые записи о создании «Слона».'}
    author = '<p class="eyebrow">Мария Артеменко-Якушева</p>' if kind == 'book' else ''
    body = '<div class="intro">' + author + '<h1>' + title + '</h1><p>' + intros[kind] + '</p></div><div class="' + section + ' catalog">' + ''.join(card(entries[s], '.', kind) for s in slugs) + '</div>'
    return shell(title, intros[kind], body, section, active=section)


def team_page():
    data = load_json(ROOT / 'content/team.json')
    groups = []
    for index, group in enumerate(data['groups'], 1):
        people = []
        for person in group['people']:
            portrait = image_html(person, '.', 'person-portrait', True)
            role = '<p class="meta">' + text(person['role']) + '</p>' if person.get('role') else ''
            biography = paragraphs_html(person['paragraphs']) if person.get('paragraphs') else ''
            people.append('<article class="person-card">' + portrait + '<div><h3>' + text(person['name']) + '</h3>' + role + '<div class="person-biography">' + biography + '</div>' + links_html(person.get('links')) + '</div></article>')
        groups.append('<section aria-labelledby="team-' + str(index) + '"><h2 id="team-' + str(index) + '">' + text(group['heading'].rstrip(':')) + '</h2><div class="team-grid">' + ''.join(people) + '</div></section>')
    partners = []
    for partner in data['partners']:
        partners.append('<a href="' + link_url(partner['url']) + '" target="_blank" rel="noopener">' + image_html(partner, '.', 'partner-logo', True) + '<span>' + text(partner['name']) + '</span></a>')
    intro = '<div class="intro"><p class="eyebrow">Проект «Неля»</p><h1>Команда</h1><p>Участники, съёмочная группа и актёры фильма «Неля».</p><a href="film-nelya.html">О фильме «Неля»</a></div>'
    body = intro + ''.join(groups) + '<section><h2>Партнёры проекта</h2><div class="partners">' + ''.join(partners) + '</div></section>'
    return shell(data['title'], data['description'], body, 'testimonials', active='testimonials', page_class='team-page')


def site_inputs():
    manifest = load_json(ROOT / 'content/site.json')
    entries = {}
    for group in ('films', 'books', 'news', 'pages'):
        for slug in manifest[group]:
            valid_slug(slug)
            if slug in RESERVED_SLUGS:
                raise ValueError('Content slug conflicts with a site section: ' + slug)
            if slug in entries:
                raise ValueError('Duplicate entry in site manifest: ' + slug)
            data = load_json(ROOT / 'content/site' / (slug + '.json'))
            if data['slug'] != slug:
                raise ValueError('Content slug does not match filename: ' + slug)
            if group != 'pages' and SECTIONS[data['type']][0] != group:
                raise ValueError('Content is listed under the wrong section: ' + slug)
            entries[slug] = data
    return manifest, entries


def build_site():
    manifest, entries = site_inputs()
    # Render and validate everything before replacing any generated page.
    pages = {'index': home(manifest, entries), 'testimonials': team_page()}
    for data in entries.values():
        slug, rendered = render(data, draft=False)
        pages[slug] = rendered
    for kind, group in (('film', 'films'), ('book', 'books'), ('news', 'news')):
        pages[group] = listing(kind, manifest[group], entries)
    pages['contact'] = shell('Контакты', 'Контактная форма и сообщества фильма «Неля». Связь со студией «Слон».', (TEMPLATES / 'contact.html').read_text(), 'contact', active='contact', page_class='contact-page')
    for slug, destination in (('ourwork', 'films'), ('projects', 'index')):
        page = shell('Перейти к проектам студии', 'Фильмы и книги студии «Слон».', '<h1>Проекты студии</h1><p><a href="' + destination + '.html">Перейти к проектам</a></p>', slug, draft=True)
        page = page.replace('<meta name="robots" content="noindex, nofollow" />', '<meta name="robots" content="noindex" />\n  <meta http-equiv="refresh" content="0; url=' + destination + '.html" />\n  <link rel="canonical" href="https://slon.media/' + (destination + '.html' if destination != 'index' else '') + '" />')
        pages[slug] = page
    for slug, page in pages.items():
        (ROOT / (slug + '.html')).write_text(page, encoding='utf-8')
    paths = ['https://slon.media/' + ('' if slug == 'index' else slug + '.html') for slug in pages if slug not in ('ourwork', 'projects')]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('  <url><loc>' + url + '</loc></url>\n' for url in paths) + '</urlset>\n'
    (ROOT / 'sitemap.xml').write_text(sitemap)
    print('Generated ' + str(len(pages)) + ' HTML pages and sitemap.xml')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, nargs='?', help='JSON content file for a draft')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--home', action='store_true', help='Regenerate the homepage preview')
    modes.add_argument('--build', action='store_true', help='Regenerate all published static pages from content/site.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'docs/design/examples')
    parser.add_argument('--replace', action='store_true', help='Replace an existing generated draft')
    args = parser.parse_args()
    try:
        if args.build or args.home:
            if args.input:
                raise ValueError('--build/--home cannot be combined with a content input')
            if args.build:
                build_site()
            else:
                manifest, entries = site_inputs()
                (ROOT / 'docs/design/home-wireframe.html').write_text(home(manifest, entries, '../..', True), encoding='utf-8')
                print('Regenerated homepage preview')
            return
        if not args.input:
            raise ValueError('Provide a JSON input, --home, or --build')
        output_dir = args.output_dir.resolve()
        if not output_dir.is_relative_to(ROOT / 'docs/design'):
            raise ValueError('Draft output must stay under docs/design/')
        prefix = Path(os.path.relpath(ROOT, output_dir)).as_posix()
        slug, page = render(load_json(args.input), prefix)
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / (slug + '.html')
        with output.open('w' if args.replace else 'x', encoding='utf-8') as stream:
            stream.write(page)
        print(output)
    except (ValueError, KeyError, OSError, TypeError, struct.error) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
