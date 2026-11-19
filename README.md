### Hexlet tests and linter status:
[![Actions Status](https://github.com/ArachnidSA/ai-for-developers-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/ArachnidSA/ai-for-developers-project-386/actions)

# ai-for-developers-project-386

Простой бэкенд (FastAPI) и фронтенд (React + Vite + TypeScript) в одном репозитории.
Окружение разработки описывается через [mise](https://mise.jdx.dev/): `mise.toml` фиксирует версии
инструментов, задачи и фоновые сервисы.

## Структура

```
backend/    FastAPI-приложение (uv-проект)
frontend/   React + Vite + TypeScript
mise.toml   инструменты, задачи, демоны, хуки
hk.pkl      git-хуки (проверки перед коммитом)
.github/    CI (hexlet-check, ci, opencode)
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
| `mise run lint` | `ruff` (бэкенд) и `oxlint` (фронт) |
| `mise run typecheck` | `mypy` (Python) и `tsc` (TypeScript) |
| `mise run test` | дымовые тесты: `pytest` (бэкенд) и `vitest` (фронт) |
| `mise run check` | всё вместе — используется в CI и в git-хуке |
| `mise dev` | бэкенд и фронт как демоны |

## Разработка

- Бэкенд: http://127.0.0.1:8000 (Swagger на `/docs`), роут `GET /api/healthcheck`.
- Фронтенд: http://127.0.0.1:5173; запросы к `/api/*` проксируются на бэкенд
  (`frontend/vite.config.ts`), поэтому CORS не нужен.

Запуск по отдельности:

```sh
cd backend  && uv run fastapi dev app/main.py
cd frontend && npm run dev
```

## CI

`.github/workflows/ci.yml` на каждый push запускает `mise run check` — те же проверки, что и локально.
`.github/workflows/hexlet-check.yml` — проверки курса Hexlet (не редактируется).
