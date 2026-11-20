# MCP-сервер Render в проекте

Проектный [`opencode.json`](../opencode.json) подключает официальный **hosted remote**
MCP-сервер Render (`https://mcp.render.com/mcp`, транспорт Streamable HTTP). Это позволяет
агенту OpenCode управлять сервисом на Render — например, создавать Web Service из
корневого `Dockerfile`.

> Секретов в репозитории нет. В `opencode.json` указан только адрес сервера; учётные данные
> хранятся вне проекта (OAuth-токены — в `~/.local/share/opencode/mcp-auth.json`).

Форма конфигурации — OpenCode V2: имена серверов лежат под `mcp.servers.<имя>`, тип remote
задаётся полем `type`. Подробности — в официальной документации:
<https://opencode.ai/docs/mcp-servers>.

## Вариант 1 (по умолчанию): OAuth, без ключа

Для remote-серверов OAuth включён по умолчанию, поэтому в `opencode.json` достаточно одной
строки `url`. Вход выполняется один раз в браузере:

1. Откройте OpenCode в этом проекте.
2. Выполните `/mcps`, выберите сервер **render** и войдите в браузере.
   В терминале то же самое делает команда `opencode mcp auth render`.
3. Убедитесь, что сервер подключён:

   ```sh
   opencode mcp list
   ```

   До входа статус может быть `needs authentication` — это нормально и секрета не требует;
   после входа — `connected`.

Токены OAuth хранятся вне репозитория и повторный вход переживают.

## Вариант 2 (альтернатива): API-ключ из переменной окружения

Если нужен ключ вместо OAuth, отключите OAuth (`oauth: false`) и передайте ключ заголовком.
В файле хранится **только имя** переменной — значение живёт в окружении хоста и в
репозиторий не попадает:

```json
{
  "mcp": {
    "servers": {
      "render": {
        "type": "remote",
        "url": "https://mcp.render.com/mcp",
        "oauth": false,
        "headers": {
          "Authorization": "Bearer {env:RENDER_API_KEY}"
        }
      }
    }
  }
}
```

Порядок:

1. Создайте ключ в Render: **Dashboard → Workspace Settings → API Keys**
   (<https://render.com/docs/api-keys>).
2. Задайте его в окружении, из которого запускается OpenCode, а не в файле:

   ```sh
   # Linux/macOS
   export RENDER_API_KEY="rnd_..."
   ```

   ```powershell
   # Windows PowerShell
   $env:RENDER_API_KEY = "rnd_..."
   ```

3. Перезапустите сессию и проверьте: `opencode mcp list`.

Кроме `{env:NAME}` OpenCode умеет подставлять содержимое файла — `{file:path/to/file}` (путь
абсолютный, относительный к файлу конфига или начинающийся с `~/`). Shell-выражения вида
`$NAME` в строках JSON не раскрываются; если переменная или файл не заданы, подставляется
пустая строка.

## Проверка подключения

- `opencode mcp list` — список настроенных серверов и их состояний. Сервер `render` в этом
  списке уже означает, что проектный `opencode.json` подхвачен.
- `/mcps` в интерфейсе OpenCode — состояние, вход и отключение сервера.
- Если статус `failed` с ошибкой вида `ECONNRESET`, это проблема сети окружения (прокси или
  файрвол), а не конфигурации: сам эндпоинт `https://mcp.render.com/mcp` на неаутентифицированный
  запрос отвечает `401` с заголовком `WWW-Authenticate` и метаданными OAuth.

## Ссылки

- Render MCP Server: <https://render.com/docs/mcp-server>
- OpenCode — MCP servers (V2): <https://opencode.ai/docs/mcp-servers>
- Исследование по схеме конфигурации: ветка `research/render-mcp`,
  `docs/research/render-mcp-and-opencode-json.md`
