import { client } from '@/api/client'
import {
  calendarApiCreateEventType,
  calendarApiListEventTypes,
  type EventType,
  type EventTypeCreate,
} from '@/api/generated'

export type { EventType, EventTypeCreate }

/** Список действующих типов событий (через сгенерированный SDK). */
export async function listEventTypes(): Promise<EventType[]> {
  const { data } = await calendarApiListEventTypes({ client })
  return data ?? []
}

/** Создать тип события (через сгенерированный SDK). */
export async function createEventType(body: EventTypeCreate): Promise<EventType> {
  const { data } = await calendarApiCreateEventType({ client, body })
  if (data === undefined) {
    throw new Error('Тип события не создан')
  }
  return data
}
