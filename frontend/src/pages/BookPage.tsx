import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { listEventTypes, type EventType } from '@/api/eventTypes'
import { listEventTypeSlots, type Slot } from '@/api/slots'

// Окно записи: 14 календарных дней от «сегодня» (см. GLOSSARY.md).
const BOOKING_WINDOW_DAYS = 14

const dayLabelFormatter = new Intl.DateTimeFormat('ru-RU', {
  day: 'numeric',
  month: 'short',
  weekday: 'short',
})

const timeFormatter = new Intl.DateTimeFormat('ru-RU', {
  hour: '2-digit',
  minute: '2-digit',
})

/** Календарный день как `YYYY-MM-DD` по локальной дате. */
function toIsoDay(day: Date): string {
  const month = String(day.getMonth() + 1).padStart(2, '0')
  const date = String(day.getDate()).padStart(2, '0')
  return `${day.getFullYear()}-${month}-${date}`
}

/** Ближайшие `count` календарных дней, начиная с сегодняшнего. */
function nextDays(count: number): string[] {
  const today = new Date()
  return Array.from({ length: count }, (_, index) =>
    toIsoDay(new Date(today.getFullYear(), today.getMonth(), today.getDate() + index)),
  )
}

function formatDay(iso: string): string {
  const [year, month, date] = iso.split('-').map(Number)
  return dayLabelFormatter.format(new Date(year, month - 1, date))
}

/** Время слота в локальном поясе гостя (в API слот приходит в UTC). */
function formatSlot(slot: Slot): string {
  return `${timeFormatter.format(new Date(slot.start))}–${timeFormatter.format(new Date(slot.end))}`
}

function BookPage() {
  const [eventTypes, setEventTypes] = useState<EventType[]>([])
  const [selectedTypeId, setSelectedTypeId] = useState<number | null>(null)
  const [selectedDay, setSelectedDay] = useState<string | null>(null)
  const [slotResult, setSlotResult] = useState<{
    key: string
    slots: Slot[] | null
    error: string | null
  }>({ key: '', slots: null, error: null })

  const days = nextDays(BOOKING_WINDOW_DAYS)

  useEffect(() => {
    listEventTypes()
      .then(setEventTypes)
      .catch(() => setEventTypes([]))
  }, [])

  useEffect(() => {
    if (selectedTypeId === null || selectedDay === null) {
      return
    }
    let active = true
    const key = `${selectedTypeId}:${selectedDay}`
    listEventTypeSlots(selectedTypeId, selectedDay)
      .then((result) => {
        if (active) setSlotResult({ key, slots: result, error: null })
      })
      .catch(() => {
        if (active) {
          setSlotResult({ key, slots: [], error: 'Не удалось загрузить свободные слоты' })
        }
      })
    return () => {
      active = false
    }
  }, [selectedTypeId, selectedDay])

  const selectionKey =
    selectedTypeId !== null && selectedDay !== null ? `${selectedTypeId}:${selectedDay}` : null
  const currentResult = selectionKey !== null && slotResult.key === selectionKey ? slotResult : null
  const slots = currentResult?.slots ?? null
  const slotsError = currentResult?.error ?? null

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 p-8">
      <h1 className="text-3xl font-bold tracking-tight">Запись на звонок</h1>
      <p className="text-muted-foreground">Выберите подходящий тип события.</p>

      {eventTypes.length > 0 ? (
        <ul aria-label="Типы событий" className="flex flex-col gap-2">
          {eventTypes.map((eventType) => (
            <li key={eventType.id}>
              <button
                className={`flex w-full flex-col rounded-md border p-3 text-left ${
                  selectedTypeId === eventType.id ? 'border-foreground' : ''
                }`}
                type="button"
                onClick={() => setSelectedTypeId(eventType.id)}
              >
                <span className="font-medium">{eventType.name}</span>
                <span className="text-muted-foreground text-sm">{eventType.description}</span>
                <span className="text-sm">{eventType.duration_minutes} мин</span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-muted-foreground">Типы событий пока не заведены</p>
      )}

      <section className="flex flex-col gap-2">
        <h2 className="text-xl font-semibold">День</h2>
        <div aria-label="Выберите день" className="flex flex-wrap gap-2" role="group">
          {days.map((day) => (
            <button
              key={day}
              className={`rounded-md border px-3 py-1 text-sm ${
                selectedDay === day ? 'border-foreground font-medium' : ''
              }`}
              type="button"
              onClick={() => setSelectedDay(day)}
            >
              {formatDay(day)}
            </button>
          ))}
        </div>
      </section>

      {selectedTypeId !== null && selectedDay !== null && (
        <section className="flex flex-col gap-2">
          <h2 className="text-xl font-semibold">Свободные слоты</h2>
          {slotsError !== null ? (
            <p className="text-sm text-red-600">{slotsError}</p>
          ) : slots === null ? (
            <p className="text-muted-foreground">Загрузка…</p>
          ) : slots.length === 0 ? (
            <p className="text-muted-foreground">Нет свободных слотов</p>
          ) : (
            <ul aria-label="Свободные слоты" className="flex flex-wrap gap-2">
              {slots.map((slot) => (
                <li key={slot.start} className="rounded-md border px-3 py-1 text-sm" data-testid="slot">
                  {formatSlot(slot)}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      <Link className="text-sm underline underline-offset-4" to="/">
        На главную
      </Link>
    </main>
  )
}

export { BookPage }
