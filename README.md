### Hexlet tests and linter status:
[![Actions Status](https://github.com/ArachnidSA/ai-for-developers-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/ArachnidSA/ai-for-developers-project-386/actions)

# ai-for-developers-project-386

Простой бэкенд (FastAPI) и фронтенд (React + Vite + TypeScript) в одном репозитории.
Окружение разработки описывается через [mise](https://mise.jdx.dev/): `mise.toml` фиксирует версии
инструментов, задачи и фоновые сервисы.

## Структура

```
backend/           FastAPI-приложение (uv-проект)
frontend/          React + Vite + TypeScript
contract/          TypeSpec-контракт API (источник истины) и генерация SDK
mise.toml          инструменты, задачи, демоны, хуки
hk.pkl             git-хуки (проверки перед коммитом)
.github/           CI (hexlet-check, ci, opencode)
skills-lock.json   версии скилов coding-агентов (см. «Скилы агента: установка и обновление»)
```

## Быстрый старт

```sh
mise install          # поставит python/uv/node/hk/pitchfork и зависимости проекта
mise run check        # линтер + проверка типов + дымовые тесты
mise dev              # поднять бэкенд (:8000) и фронт (:5173) как фоновые демоны
mise daemons status   # состояние сервисов
```

## Задачи

| Команда | Что делает |
|---|---|
| `mise run install` | `uv sync` (бэкенд) + `npm ci` (фронт) |
| `mise run gen` | сгенерировать OpenAPI и клиентский SDK из TypeSpec (`contract/`) |
| `mise run contract` | `gen` + проверка, что сгенерированные артефакты не разошлись с закоммиченными |
| `mise run lint` | `ruff` (бэкенд) и `oxlint` (фронт) |
| `mise run typecheck` | `mypy` (Python) и `tsc` (TypeScript) |
| `mise run test` | дымовые тесты: `pytest` (бэкенд) и `vitest` (фронт) |
| `mise run e2e` | браузерный E2E сценария гостя: Playwright сам поднимает бэкенд и фронт |
| `mise run check` | всё вместе — используется в CI и в git-хуке |
| `mise dev` | бэкенд и фронт как демоны |

## Разработка

- Бэкенд: http://127.0.0.1:8000 (Swagger на `/docs`), роуты `GET /api/healthcheck` и
  `GET`/`POST /api/event-types`. Контракт — TypeSpec в `contract/`, клиентский SDK
  генерируется командой `mise run gen` (см. `contract/README.md`).
- Фронтенд: http://127.0.0.1:5173; запросы к `/api/*` проксируются на бэкенд
  (`frontend/vite.config.ts`), поэтому CORS не нужен.

Запуск по отдельности:

```sh
cd backend  && uv run fastapi dev app/main.py
cd frontend && npm run dev
```

## E2E (Playwright)

`mise run e2e` прогоняет браузерный сценарий гостя (выбор типа → календарь → запись →
подтверждение) на **настоящих** серверах: Playwright сам поднимает FastAPI (`127.0.0.1:8000`,
временная БД `backend/e2e.db`) и Vite (`127.0.0.1:5173`). API бронирования не подменяется.
Перед первым запуском поставь браузер Chromium:

```sh
npx --prefix frontend playwright install chromium   # в CI: npx playwright install --with-deps chromium
```

## Скилы агента

Скилы для coding-агентов ([mattpocock/skills](https://github.com/mattpocock/skills))
устанавливаются в `.agents/skills/` (каталог в `.gitignore`), а их версии фиксирует
**`skills-lock.json`** — он коммитится и является источником истины: в нём записаны
коммит-источник и хеш содержимого каждого скила. Требуется Node 22.20+ — из `mise`
он уже доступен.

```sh
npx skills@latest install   # восстановить скилы из skills-lock.json (после клона)
npx skills@latest update -p # обновить проектные скилы до новых версий
npx skills@latest list      # что установлено и не разошлось ли с lock
npx skills@latest add mattpocock/skills   # доставить скилы, которых ещё нет
```

После `update` или `add` закоммить `skills-lock.json`. Правки файлов внутри
`.agents/skills/` в коммит не попадут и будут перезаписаны при следующем `install`.

OpenCode видит скилы из `.agents/skills/` автоматически. Чтобы вызвать конкретный,
упомяните его в промпте как `@<id>`, например `@code-review` или `@tdd` — id
совпадает с именем каталога скила. Список установленного: `npx skills@latest list`.

## CI

`.github/workflows/ci.yml` на каждый push запускает `mise run check` — те же проверки, что и локально.
`.github/workflows/hexlet-check.yml` — проверки курса Hexlet (не редактируется).
