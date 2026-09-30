# Slon Media

Статический сайт студии Slon. Сборка и менеджер пакетов не нужны.

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
