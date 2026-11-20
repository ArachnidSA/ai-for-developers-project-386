# Changelog

## [0.2.0](https://github.com/ArachnidSA/ai-for-developers-project-386/compare/v0.1.0...v0.2.0) (2026-11-20)


### Features

* **backend:** добавить каркас FastAPI-приложения ([ba2d57c](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/ba2d57c31a31422f55c0008a623821730be9edc9))
* **backend:** модель записи и свободные слоты по типу и дате ([#16](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/16)) ([e963522](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/e96352200400afc4bb54cac3770eb62c696494c2))
* **backend:** правка, архивация и удаление типа события ([#21](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/21)) ([2ad691e](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/2ad691e06773bd89d81c502f222792f4e2f139ae))
* **backend:** создание записи с проверкой непересечения ([#15](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/15)) ([b311898](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/b311898de723e2d9f9f1152bbff3b23d8bb77f4f))
* **backend:** список предстоящих записей и удаление ([#20](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/20)) ([75c57e5](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/75c57e5aef349139c24bf84b8ff5500f01576b2f))
* **backend:** эндпоинты типов событий ([#17](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/17)) ([e6d998b](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/e6d998b1f4a7225275a1da424eb8dc254708e83b))
* **frontend:** выбор дня и свободные слоты на экране записи ([#16](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/16)) ([3196c66](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/3196c66cae54228e6b34d5f9d41bd490aef59062))
* **frontend:** добавить каркас React + Vite + TypeScript ([8247a67](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/8247a67e639ac4d49016419d68ed06c2169c7e67))
* **frontend:** добавить сгенерированный SDK типов событий ([#17](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/17)) ([baa65e4](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/baa65e44fae26c45225672e56a8b49509a2d0301))
* **frontend:** подключить Tailwind, shadcn/ui и роутер ([c6ed286](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/c6ed286d903a24f532634ead56e000b869eadb06)), closes [#2](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/2)
* **frontend:** показать типы событий на экранах владельца и записи ([#17](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/17)) ([9ef3e30](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/9ef3e30c2f3320787fc2eb3eb9be48458a387091))
* **frontend:** секция предстоящих записей у владельца ([#20](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/20)) ([549650c](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/549650cbe5656322aaa377697a20b010ba4a7313))
* **frontend:** собрать лендинг главного окна ([8bc50a5](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/8bc50a51b297b13757c0de67119b63131e520470)), closes [#4](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/4)
* **frontend:** управление типами событий у владельца ([#21](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/21)) ([c7dfe7f](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/c7dfe7fc35f52d723bc0522a91ced02ce044d4e7))
* **frontend:** форма и подтверждение записи гостя ([#15](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/15)) ([2f9e226](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/2f9e22679abcb0f2d73e273458d73e132d92f48e))
* собрать Docker-образ приложения и локальную smoke-проверку ([#36](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/36)) ([8fc5bb2](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/8fc5bb2c8b6ce501144431ffd1b178a416c04e37))


### Bug Fixes

* **backend:** не отдавать null в опциональных полях и типизировать ошибки в контракте ([#14](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/14)) ([eaba409](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/eaba40940f47cc677c29d95d7bde51d7e733f0db))
* **frontend:** добавить лиловый тон в фон лендинга ([2fd7e74](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/2fd7e74785387fc8be7848909b0a31fd5fc7a05a))
* **frontend:** считать окно дат гостя в поясе владельца ([#14](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/14)) ([7c0fc67](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/7c0fc674c975465a240d01b4626483c6656c410c))
* закрыть обход каталога в раздаче статики SPA ([#36](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/36)) ([b832a22](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/b832a22731395fd200a1bb43abfb2b45c7a6d62c))
* перевести MCP Render на protocol auto ([#37](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/37)) ([1284565](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/12845658f8ad3ddf8113716109ea13243a804000))
* перейти на API-ключ для MCP Render, OAuth недоступен ([#37](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/37)) ([ea1f85e](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/ea1f85e5c4f8bb37c9f01f02f3c80b5aed73b003))


### Code Refactoring

* **backend:** вынести общие хелперы тестов в conftest ([#14](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/14)) ([2538752](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/2538752662c3d16826e342e4f1b51e33c942faaf))
* **backend:** свести доменные помощники в сервисы ([#14](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/14)) ([fcc8262](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/fcc8262f0d54ae046b2189f9e3de0a5050dccf47))
* **frontend:** переименовать маршрут /admin в /owner ([c3265a3](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/c3265a3fea9f3c98d5dcbc0c5ada6c179685bc7d))
* **frontend:** убрать дублирование и типизировать e2e ([#14](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/14)) ([0ca0d5e](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/0ca0d5e1e30264e53ca4611f36c0b349c0dc5350))
* убрать дублирование и уточнить имена в smoke-скрипте ([#36](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/36)) ([ad146ea](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/ad146ea9a885a537a5d15ffb4f68461161e0baff))


### Documentation

* добавить глоссарий и ADR по записи на звонок ([24c2f7d](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/24c2f7df89b09aeb7fea6e1bdd67c12062434e69))
* зафиксировать эфемерное хранение на хостинге ADR ([#38](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/38)) ([a34bd4c](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/a34bd4c95a5c36f6070654545b1dfc03c4e57d50))
* настроить скилы агента под репозиторий ([e16721f](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/e16721f5f824353e15f68984a94ebd1d84570850))
* описать check/check:fast, дрейф контракта и E2E ([#18](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/18)) ([89a2c01](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/89a2c01072802d961f579dfae8526a83fc6e83d3))
* описать деплой, публичную ссылку и хранение в README ([#41](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/41)) ([8dc328a](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/8dc328ad008ca99485870028bae0e9e2a9d6d3c7))
* описать запуск E2E в README ([#23](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/23)) ([df58372](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/df583729fb205ee44c79141e6f891c34419de3a1))
* описать кодогенерацию контракта ([#22](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/22)) ([9d2e690](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/9d2e6900375cbc1a156d0ecab4a250f6bafd3b5c))
* описать проект в README и AGENTS.md ([e18c5f0](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/e18c5f0874bfbfbb39a3c576be6dd8df4027cc1b))
* описать релизы через release-please ([#19](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/19)) ([e6d9c24](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/e6d9c24caed41475ef85016802e12254c01e5fee))
* описать установку и обновление скилов агента ([d3ba6c4](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/d3ba6c4fd62d7b565c1937ccac72b4c60512a803))
* привести глоссарий и ADR к брифу (управляемые типы) ([e1d1d47](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/e1d1d47d1f2ceece8b65b24b73156954b54fec11))
* разрешить подпись «Админка» для экрана владельца ([fe931ea](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/fe931eab8e1da2ec4fec2d771ea5452378006d51))
* сделать «Запись» каноническим термином вместо «Бронь» ([95f5034](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/95f50341484e9ffea269c136323a55c09e83c003))
* ссылаться на тикет в коммите реализации ([b9e2cff](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/b9e2cff5f202868ca15dba995c51ded8d19de0b7))
* уточнить OAuth, ветку деплоя и envVars в render.yaml ([#39](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/39), [#41](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/41)) ([dfe1c22](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/dfe1c22efb7c7254f91a227d5f7f5cb470947818))


### Tests

* **frontend:** браузерный E2E сценария гостя ([#23](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/23)) ([53d6b66](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/53d6b66120ee5b3afceeb28b951ead85dda64385))


### Continuous Integration

* единая команда check с contract и e2e, лёгкая check:fast ([#18](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/18)) ([e63fda4](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/e63fda4f9ec10848868106dea24330ad2a238e21))
* запускать mise run check на push ([ce79058](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/ce79058b71f6f4109f2c03c120131c276e103c32))
* подключить release-please по Conventional Commits ([#19](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/19)) ([0d8e6fa](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/0d8e6fa7b1318d86a9242364ac1db3d6785fd2e2))
* проверять дрейф кодогенерации ([#22](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/22)) ([c57fa44](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/c57fa4477447776552dc9cb5b6f68f62de7b9ba8))


### Miscellaneous Chores

* держать сгенерированные артефакты в LF ([#17](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/17)) ([c78ac95](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/c78ac958ff6f769d1bccc43a969eccb0acb1236f))
* добавить gh CLI в инструменты ([45c5a49](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/45c5a49b08a7ff5e2434176f1f49f460b41b14f8))
* добавить render.yaml как справку по сервису Render ([#39](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/39)) ([de93abe](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/de93abe33e342f5d49eb79284321e1e54db79313))
* добавить TypeSpec-контракт и генерацию OpenAPI/SDK ([#17](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/17)) ([f58b4a8](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/f58b4a8da742754d1a98f1c0d2fe73483495ec64))
* задача mise run e2e ([#23](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/23)) ([90607f9](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/90607f9d10f52bd4d8ccd1105d98171404162197))
* зафиксировать набор скилов в skills-lock.json ([ae2a66a](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/ae2a66ad8646c124e4e6b386c11b43ff6c74e3c9))
* контракт жизненного цикла типа события и SDK ([#21](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/21)) ([b2921e9](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/b2921e9e3f1d97c3f423644b3bb979b1ee34140b))
* контракт свободных слотов и SDK ([#16](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/16)) ([a89dfe3](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/a89dfe3c268d97b019c5463ec5a2f82e67dac421))
* контракт создания записи и SDK ([#15](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/15)) ([baf6aa5](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/baf6aa55e1238798f933ee53aa188892fbfc39a8))
* контракт списка предстоящих записей и удаления ([#20](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/20)) ([4f16dd7](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/4f16dd7b63d29f7b3dea0fa0d92f391b707f3e95))
* настроить окружение mise и git-хуки hk ([218e239](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/218e2399c05f1169d970c364149bb6fd99cd2f07))
* подключить MCP-сервер Render в opencode.json без секретов ([#37](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/37)) ([40457b3](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/40457b34bc3d4d662345938875db8b468196fd9b))
* читать MCP-ключ Render из корневого файла и держать его вне сборки ([#37](https://github.com/ArachnidSA/ai-for-developers-project-386/issues/37)) ([135eabc](https://github.com/ArachnidSA/ai-for-developers-project-386/commit/135eabc799c2bd8dbbd8a414af3261d4e4fc2787))
