# Render MCP и схема `opencode.json`

Исследование по wayfinder-тикету [#27 «Render MCP и схема opencode.json»](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/27).

Вопрос: как подключить MCP-сервер Render в проектный `opencode.json` и как через него
задеплоить приложение. Ниже — факты из первичных источников (официальная документация Render,
исходники/пакет `render-oss/render-mcp-server`, документация OpenCode) и конкретные фрагменты
конфигурации без секретов.

Все версии и URL проверены 2026-11-20. Каждый факт снабжён ссылкой на источник; там, где
источник неоднозначен, это отмечено явно (раздел «Что осталось неясным»).

---

## Краткая рекомендация

- **Сервер**: официальный **hosted remote** `https://mcp.render.com/mcp` (Streamable HTTP).
  Render прямо советует его вместо локального запуска.
- **Аутентификация в OpenCode**: **API-ключ через заголовок** с подстановкой
  `{env:RENDER_API_KEY}` — это документированный самим Render вариант для OpenCode
  ([render.com/agents/opencode](https://render.com/agents/opencode)). OAuth в OpenCode
  подключается по умолчанию, но с Render он для OpenCode штатно не заявлен (см. ниже).
- **Секреты**: в `opencode.json` попадает только **имя** переменной окружения
  (`{env:RENDER_API_KEY}`), не значение. В `render.yaml` секреты помечаются `sync: false`.
- **Деплой**: сервис создаётся инструментом `create_web_service` (`runtime: docker`,
  `plan: free`, `dockerfilePath`), публичный URL берётся из `get_service`
  (`serviceDetails.url`), статус — из `list_deploys` / `get_deploy` (до `live`).

---

## 1. Какой MCP-сервер Render актуален

Источник: [Render MCP Server — официальная документация](https://render.com/docs/mcp-server),
[render-oss/render-mcp-server (GitHub)](https://github.com/render-oss/render-mcp-server),
[changelog о hosted-сервере](https://render.com/changelog/render-mcp-server-is-now-generally-available).

**Актуален hosted remote сервер:**

- URL: `https://mcp.render.com/mcp`.
- Транспорт: Streamable HTTP (сервер также поддерживает stdio для локального запуска).
- Аутентификация: OAuth (заявлен для Claude Code, Codex, Cursor) **и** API-ключ через
  заголовок `Authorization: Bearer <RENDER_API_KEY>`. Render «strongly recommends» hosted
  вместо локального.

**Локальный stdio сервер (альтернатива):**

- Требует `RENDER_API_KEY` в окружении.
- Вариант 1 — Docker-образ:
  `ghcr.io/render-oss/render-mcp-server` (запускается как
  `docker run -i --rm -e RENDER_API_KEY -v render-mcp-server-config:/config ghcr.io/render-oss/render-mcp-server`).
- Вариант 2 — локальный исполняемый файл `render-mcp-server` (install-скрипт для Linux/macOS
  либо `go build` из репозитория). На Windows install-скрипта нет.

**Рекомендация: hosted remote + API-ключ.** Обоснование: Render сам рекомендует hosted;
документированная Render схема для OpenCode — именно API-ключ из `RENDER_API_KEY`; hosted
получает новые возможности сразу. Локальный stdio в этом репозитории неудобен: нужен Docker
и он не даёт преимуществ.

---

## 2. Точная форма блока `mcp` в `opencode.json` (OpenCode V2)

Источники: [OpenCode — MCP servers](https://opencode.ai/docs/mcp-servers),
[OpenCode — Config](https://opencode.ai/docs/config), локальный скил `opencode`
(«Version policy: answer for V2»).

**Важно (V2):** имена серверов живут **внутри** `mcp.servers.<name>`, а не прямо под `mcp`
(«V2 does not place server names directly under `mcp`»). Флаг «не подключать» — это
`disabled: true`; **поля `enabled` в V2 нет** (это форма V1/legacy, её не используем).

Поддерживаемые поля:

| `type` | Поля |
| --- | --- |
| `remote` | `url` (обязателен, абсолютный Streamable HTTP endpoint), `headers`, `oauth` (`false` либо объект настроек), `disabled`, `timeout`, `codemode`, `protocol`, `pool` |
| `local`  | `command` (обязателен, массив: исполняемый файл + аргументы), `cwd`, `environment`, `disabled`, `timeout`, `codemode`, `protocol`, `pool` |

- **Подстановка секретов**: `{env:NAME}` и `{file:path}` прямо в строках JSON. Shell-выражения
  (`$NAME`) в JSON **не** раскрываются. Если переменная не задана — подставляется пустая строка.
- **OAuth-вход**: для remote-серверов OAuth включён по умолчанию. Вход — через `/mcps`
  (выбрать сервер и войти) либо `opencode mcp auth render`. Токены хранятся вне проекта, в
  `~/.local/share/opencode/mcp-auth.json`. `oauth: false` отключает OAuth и заставляет
  использовать заголовок.
- **Предрегистрированный клиент** (если сервер не поддерживает CIMD/DCR):
  ```jsonc
  "oauth": { "client_id": "{env:MCP_CLIENT_ID}", "client_secret": "{env:MCP_CLIENT_SECRET}" }
  ```

### Фрагмент `opencode.json` (рекомендуемый, API-ключ, без секретов)

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
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

Переменную `RENDER_API_KEY` задают в окружении хоста (shell/CI/секреты Render), а не в файле.
Инструменты сервера `render` в OpenCode получают имена вида `render_<tool>`; в Code Mode —
`tools.render.<tool>(...)` ([OpenCode — MCP servers, раздел Names](https://opencode.ai/docs/mcp-servers)).

### Вариант с OAuth (без ключа в файле вообще)

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "render": { "type": "remote", "url": "https://mcp.render.com/mcp" }
    }
  }
}
```

После этого — `/mcps` → выбрать `render` → войти в браузере (или `opencode mcp auth render`).
Секрет в репозиторий не попадает: токены лежат вне проекта.

### Вариант с локальным stdio (если очень нужен)

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "render": {
        "type": "local",
        "command": [
          "docker", "run", "-i", "--rm",
          "-e", "RENDER_API_KEY",
          "-v", "render-mcp-server-config:/config",
          "ghcr.io/render-oss/render-mcp-server"
        ],
        "environment": { "RENDER_API_KEY": "{env:RENDER_API_KEY}" }
      }
    }
  }
}
```

> Примечание о расхождениях. Официальный пример Render для OpenCode
> ([render-examples/opencode-on-render](https://github.com/render-examples/opencode-on-render),
> `start.sh`) и часть сторонних гайдов используют **V1-форму** `"mcp": { "render": { ..., "enabled": true } }`
> и поле `env` (это форма для `mcpServers` Claude/Cursor). Для V2 корректны `mcp.servers.*`,
> `disabled` вместо `enabled` и `environment` вместо `env`.

---

## 3. Инструменты Render MCP для Docker Web Service, публичный URL и статус деплоя

Источник: [render-oss/render-mcp-server — README, раздел Tools](https://github.com/render-oss/render-mcp-server#tools)
и исходники `pkg/service/tools.go`, `pkg/deploy/tools.go`, `pkg/mcpserver/common.go`,
`pkg/validate/params.go` в том же репозитории.

### Создание сервиса

`create_web_service` — создаёт web service. Для репозитория с Dockerfile:

| Параметр | Значение |
| --- | --- |
| `name` | обязателен; из него генерируется поддомен URL |
| `runtime` | `docker` |
| `repo` | Git URL репозитория (без ветки) |
| `branch` | ветка (по умолчанию — дефолтная ветка репозитория) |
| `dockerfilePath` | путь к Dockerfile от корня репозитория, по умолчанию `./Dockerfile` |
| `dockerContext` | контекст сборки, по умолчанию `.` |
| `dockerCommand` | переопределение команды запуска (иначе `ENTRYPOINT`/`CMD` образа) |
| `plan` | `free` (значение по умолчанию), а также `starter`, `standard`, `pro`, `pro_max`, `pro_plus`, `pro_ultra` |
| `autoDeploy` | `yes` (по умолчанию) / `no` |
| `region` | `oregon` (по умолчанию), `frankfurt`, `singapore`, `ohio`, `virginia` |
| `envVars` | массив объектов `{ "key": ..., "value": ... }` |

Особенности:

- Для `runtime: docker` поля `buildCommand` и `startCommand` **не требуются** (они нужны для
  нативных рантаймов).
- `plan: free` действительно принимается: в исходниках `ValidServicePlanValues` начинается с
  `"free"`, а `create_web_service` по умолчанию ставит `free`
  (`pkg/mcpserver/common.go`, `pkg/service/tools.go`). Примечание: README-таблица «Tools» перечисляет
  у `create_web_service` только платные планы — это устаревший/неполный список, код включает `free`.
- Создание сервиса из prebuilt-образа реестра контейнеров не поддерживается.
- Прямое редактирование сервиса через MCP недоступно: `update_web_service` лишь возвращает
  ссылку на Dashboard.

### Публичный URL

`create_web_service` возвращает созданный сервис и первый деплой. Получить детали (в т.ч.
публичный URL) можно через `get_service` — он возвращает объект сервиса Render API, где:

- `id` — идентификатор (`srv-...`);
- `serviceDetails.url` — публичный URL (для web service это `https://<name>.onrender.com`);
- там же `healthCheckPath`, `plan`, `region`, `runtime`.

Источник формы: [Render API — Retrieve service (OpenAPI)](https://api-docs.render.com/reference/retrieve-service):
`serviceDetails` для web service содержит обязательное поле `url` (и `healthCheckPath`,
`plan`, `region`, `buildPlan` и т.д.).

### Статус деплоя

- `list_deploys` — история деплоев сервиса (со `status`, `commit`, `startedAt`, `finishedAt`).
- `get_deploy` — детали конкретного деплоя.
- `trigger_deploy` — ручной деплой (для сервисов с выключенным авто-деплоем; после push при
  включённом авто-деплое вызывать не нужно).
- `list_events`, `list_logs` — события и логи (в т.ч. причины падения).
- `list_services` — все сервисы аккаунта.

Словарь статусов деплоя (11 значений; из OpenAPI Render —
[cancel-deploy](https://api-docs.render.com/reference/cancel-deploy), согласуется с ADR о
паритете REST/MCP):

```
created, queued, build_in_progress, update_in_progress, live,
deactivated, build_failed, update_failed, canceled,
pre_deploy_in_progress, pre_deploy_failed
```

Успешно выкаченный деплой — `live`; ждать его нужно между `build_in_progress` /
`update_in_progress` и одним из финальных значений.

### Альтернативный путь: Blueprint-инструменты

Сервер также отдаёт альфа-инструменты `create_blueprint`, `plan_blueprint`, `approve_blueprint`,
`get_blueprint`, `update_blueprint` (управление `render.yaml`-Blueprint'ом). Это другой путь:
сервис создаётся не напрямую, а из Blueprint. **Нельзя** одновременно управлять одним
ресурсом и Blueprint'ом, и через `create_web_service`.

---

## 4. Поля `render.yaml` для Docker-сервиса

Источник: [Render — Blueprint YAML Reference](https://render.com/docs/blueprint-spec),
[Render API — Retrieve service (OpenAPI)](https://api-docs.render.com/reference/retrieve-service)
для `plan`/`region`/`autoDeployTrigger`,
[Render — Environment variables](https://render.com/docs/configure-environment-variables).

```yaml
# yaml-language-server: $schema=https://render.com/schema/render.yaml.json
services:
  - type: web
    name: calendar            # уникальное имя; задаёт поддомен
    runtime: docker
    region: oregon            # oregon (default) | frankfurt | singapore | ohio | virginia
    plan: free
    dockerfilePath: ./Dockerfile   # по умолчанию ./Dockerfile
    dockerContext: .               # по умолчанию корень репозитория
    healthCheckPath: /api/healthcheck
    autoDeployTrigger: commit      # commit | checksPass | off
    envVars:
      - key: APP_SECRET
        generateValue: true        # Render сгенерирует значение, в репозитории секрета нет
      - key: DATABASE_URL
        sync: false                # значение запрашивается в Dashboard, не коммитится
```

Пояснения к полям:

- `dockerfilePath` — путь к Dockerfile от корня; по умолчанию `./Dockerfile`. Для монорепо
  (у нас `backend/Dockerfile`) указывается явно.
- `dockerContext` — контекст сборки; по умолчанию корень репозитория.
- `healthCheckPath` — путь, который Render проверяет перед переключением трафика. Маршрут
  должен реально существовать в приложении, иначе деплой не пройдёт проверку. У нас подходит
  `GET /api/healthcheck`.
- `plan: free` — валидный план; у free web service есть спин-даун после ~15 минут без трафика и
  холодный старт.
- `autoDeploy` **устарел**; актуальное поле — `autoDeployTrigger` со значениями
  `commit` (деплой на каждый push), `checksPass` (после успешных CI), `off`. Нельзя задавать
  оба поля одновременно.
- `region` — значения как у MCP (`oregon` по умолчанию).
- `envVars` — варианты: `value` (жёстко), `generateValue: true`, `sync: false` (запрос в
  Dashboard), `fromDatabase`, `fromService`, `fromGroup`. Секреты в репозиторий не кладут —
  только `sync: false`/`generateValue`.

**Связь с MCP.** `create_web_service` создаёт сервис напрямую и **не** читает `render.yaml`.
`render.yaml` нужен, если выбран путь Blueprint (`create_blueprint` → `plan_blueprint` →
`approve_blueprint`) либо деплой «из дашборда». Пути взаимоисключающие для одного ресурса:
сервис, созданный через `create_web_service`, и Blueprint не должны управлять одним и тем же.

---

## 5. Как обойтись без секретов в репозитории

- **OpenCode + API-ключ**: в `opencode.json` пишется только имя переменной —
  `"Authorization": "Bearer {env:RENDER_API_KEY}"`. Ключ задаётся в окружении хоста
  (`RENDER_API_KEY`), в репозиторий не коммитится.
- **OpenCode + OAuth**: в файле нет ни ключа, ни секрета — только `url`; токены хранятся вне
  проекта (`~/.local/share/opencode/mcp-auth.json`).
- **`render.yaml`**: значения секретов не коммитятся — `sync: false` (запрос в Dashboard) либо
  `generateValue: true` (генерация Render). `.env` в репозиторий не кладём.
- Ключ Render создаётся в Dashboard (Workspace Settings → API Keys) —
  [render.com/docs/api-keys](https://render.com/docs/api-keys).

---

## Что осталось неясным / требует проверки

1. **OAuth в OpenCode против Render MCP.** Render заявляет OAuth с предрегистрированными
   клиентами для Claude Code, Codex и Cursor. Автоматический OAuth OpenCode опирается на CIMD
   или DCR; поддерживает ли их auth-server Render для клиента OpenCode — не подтверждено
   первичным источником. Документированная Render схема для OpenCode использует **API-ключ**,
   а не OAuth ([render.com/agents/opencode](https://render.com/agents/opencode): «OpenCode's
   documented Render setup does not use OAuth»). Поэтому рекомендация — API-ключ; OAuth стоит
   проверять отдельно на живом сервере.
2. **Совместимость form-фактора V1/V2.** Существующие примеры Render и сторонние гайды дают
   V1-форму (`mcp.<name>`, `enabled`). Точная поддержка V2-поля `disabled` и `mcp.servers`
   проверена по документации V2, но не проверялась на живом OpenCode против Render.
3. **Поля ответа `create_web_service`/`get_service`.** `serviceDetails.url` подтверждён схемой
   Render API, но практическое имя поля в JSON-ответе MCP стоит сверить на реальном вызове.
4. **`plan: free` в MCP.** Код `render-mcp-server` включает `free` в допустимые планы и ставит
   его по умолчанию, однако README-таблица инструментов перечисляет только платные планы —
   расхождение, следует проверить на живом вызове.
5. **`healthCheckPath` и `/api/healthcheck`.** Форматы ответа: бэкенд отдаёт JSON
   healthcheck; нужно убедиться, что Render считает ответ `2xx` здоровым (обычно да), и что путь
   доступен без аутентификации.
6. **Где именно хранить `RENDER_API_KEY`** в этом репозитории (локальный shell, секреты CI,
   секреты Render) — вне области этого тикета; в `opencode.json` попадает только имя.

---

## Источники

- Render MCP Server (официальная документация): https://render.com/docs/mcp-server
- Render MCP Server (GitHub, официальный, инструменты): https://github.com/render-oss/render-mcp-server
- Render changelog — hosted-сервер: https://render.com/changelog/render-mcp-server-is-now-generally-available
- Render — Deploy with OpenCode: https://render.com/agents/opencode
- Render-examples/opencode-on-render: https://github.com/render-examples/opencode-on-render
- Render — Blueprint YAML Reference: https://render.com/docs/blueprint-spec
- Render — Environment Variables and Secrets: https://render.com/docs/configure-environment-variables
- Render API — Retrieve service (OpenAPI): https://api-docs.render.com/reference/retrieve-service
- Render API — Cancel deploy (OpenAPI, статусы деплоя): https://api-docs.render.com/reference/cancel-deploy
- Render — API keys: https://render.com/docs/api-keys
- OpenCode — MCP servers: https://opencode.ai/docs/mcp-servers
- OpenCode — Config: https://opencode.ai/docs/config
