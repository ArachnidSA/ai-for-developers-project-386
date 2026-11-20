import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@service(#{ title: "Calendar API" })
@server("http://127.0.0.1:8000", "Локальный сервер разработки")
namespace Calendar;

/** Статус типа события: действующий или архивный. */
enum EventTypeStatus {
  /** Тип доступен для выбора гостю. */
  active: "active",
  /** Тип скрыт от гостей, но записи по нему сохраняются. */
  archived: "archived",
}

/** Вид встречи, который заводит владелец. */
model EventType {
  /** Системный идентификатор. */
  id: int32;
  /** Название типа события. */
  name: string;
  /** Описание типа события. */
  description: string;
  /** Длительность встречи в минутах (5–720). */
  @minValue(5)
  @maxValue(720)
  duration_minutes: int32;
  /** Статус типа события. */
  status: EventTypeStatus;
}

/** Данные для создания типа события. */
model EventTypeCreate {
  /** Название типа события. */
  name: string;
  /** Описание типа события. */
  description: string;
  /** Длительность встречи в минутах (5–720). */
  @minValue(5)
  @maxValue(720)
  duration_minutes: int32;
}

@route("/api")
namespace CalendarApi {
  /** Список типов событий. Гостю — только действующие, владельцу — все. */
  @route("/event-types")
  @get
  op listEventTypes(): EventType[];

  /** Создать тип события. */
  @route("/event-types")
  @post
  op createEventType(@body body: EventTypeCreate): {
    @statusCode statusCode: 201;
    @body body: EventType;
  };
}
