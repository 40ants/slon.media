# Slon Media

Статический сайт студии Slon. Сборка и менеджер пакетов не нужны.

## Добавление контента и оформление

Главная — обзор проектов. Фильмы, книги и новости имеют отдельные страницы;
`testimonials.html` содержит команду, `contact.html` — способы связи.

Исходные материалы хранятся в `content/site/*.json`, порядок проектов — в
`content/site.json`, команда — в `content/team.json`. Общие шапка, меню и подвал
задаются в `templates/content/base.html`, оформление — в `css/style.css`.
После изменения исходников обновите готовые HTML и карту сайта:

```sh
python3 scripts/render-content.py --build
```

Python-зависимости не нужны. Готовые HTML входят в репозиторий, поэтому серверу
генератор не требуется. Не правьте сгенерированные страницы напрямую: следующая
генерация заменит такие изменения.

Для нового фильма, книги или новости используйте проектный скилл
[slon-site-content](.agents/skills/slon-site-content/SKILL.md). Предварительный
просмотр одного материала можно создать командой:

```sh
python3 scripts/render-content.py content/site/book-oda-moskve.json --replace
```

Черновики находятся в `docs/design/` и не входят в Docker-образ сайта.

## Запуск на macOS через Colima

Убедитесь, что установлены [Colima](https://github.com/abiosoft/colima) и Docker CLI, затем в корне репозитория выполните:

```sh
colima start
docker build -t slon.media .
docker run --rm --name slon-media -p 8080:80 slon.media
```

Откройте [http://localhost:8080](http://localhost:8080). Контейнер работает в текущем окне терминала; чтобы остановить его, нажмите `Control-C`.

После изменения файлов пересоберите образ и запустите контейнер снова:

```sh
docker build -t slon.media .
docker run --rm --name slon-media -p 8080:80 slon.media
```

Когда сайт больше не нужен, можно остановить виртуальную машину Colima:

```sh
colima stop
```

## Быстрый просмотр без Docker

Для обычной проверки HTML, CSS и изображений достаточно встроенного HTTP-сервера Python 3:

```sh
python3 -m http.server 8080
```

После этого откройте [http://localhost:8080](http://localhost:8080). Изменения в файлах будут доступны после обновления страницы. Остановите сервер сочетанием `Control-C`.
