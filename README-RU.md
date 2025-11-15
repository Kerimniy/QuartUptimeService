In English <a href="https://github.com/Kerimniy/QuartUptimeService/blob/main/README.md">click</a>

<img src="https://github.com/Kerimniy/QuartUptimeService/blob/main/for_readme/QUS.png" style="width: 70px">

# QuartUptimeService


## Что это такое
Монитор Аптайма — это асинхронный веб-сервис, построенный на Python (Quart + asyncio), предназначенный для мониторинга доступности веб-сайтов и API. Он периодически отправляет HTTP-запросы к указанным URL, логирует статусы в SQLite и генерирует графики аптайма (за последний час). Поддерживает группы сервисов, аутентификацию и простой дашборд.

<img src="https://github.com/Kerimniy/QuartUptimeService/blob/main/for_readme/QUSP.png" style="width: 95%; margin-left: 2vh; position: relative; left:50%; transform: translateX(-50%)">


## Установка
1. **Зависимости** (Python 3.12+):
   ```
   pip install requirements.txt
   ```

2. **Файлы**: Клонируйте репозиторий.

3. **Запуск**:
   ```
   python app.py
   ```
   - Сервер запускается по адресу `http://localhost:5000`.
   - При первом запуске: регистрация (логин/пароль). База данных (`uptime.db`) создаётся автоматически (SQLite-файл в корневой папке).


## Что вы можете делать
- **Мониторинг**: Добавляйте URL (с интервалом от 3 секунд, таймаутом, поддержкой редиректов, группами). Сервис выполняет пинги асинхронно.


- **Просмотр**: На дашборде (`/`): графики аптайма (цвета: зелёный/красный по RGB-формуле), авто-обновление. Настраиваемое Markdown-описание и логотип.


- **Администрирование** (`/admin/` после входа):
  - Создание/редактирование/удаление мониторов.
  - Загрузка логотипа (PNG/JPG и др., до 50 МБ).
  - Изменение заголовка и Markdown.

- **API**: GET/POST для статистики (`/api/hourinfo`), мониторов (`/api/createMonitor` и т.д.). Ограничение скорости: 15 запросов/5 сек.
