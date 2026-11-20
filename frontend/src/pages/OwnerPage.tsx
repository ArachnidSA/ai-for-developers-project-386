import { type FormEvent, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { createEventType, listEventTypes, type EventType } from '@/api/eventTypes'
import { Button } from '@/components/ui/button'

function OwnerPage() {
  const [eventTypes, setEventTypes] = useState<EventType[]>([])
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [duration, setDuration] = useState('30')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listEventTypes()
      .then(setEventTypes)
      .catch(() => setError('Не удалось загрузить типы событий'))
  }, [])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    try {
      await createEventType({
        name,
        description,
        duration_minutes: Number(duration),
      })
      setEventTypes(await listEventTypes())
      setName('')
      setDescription('')
      setDuration('30')
    } catch {
      setError('Не удалось создать тип события')
    }
  }

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 p-8">
      <h1 className="text-3xl font-bold tracking-tight">Админка</h1>

      <section className="flex flex-col gap-3">
        <h2 className="text-xl font-semibold">Типы событий</h2>
        {eventTypes.length === 0 ? (
          <p className="text-muted-foreground">Типы событий пока не заведены</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {eventTypes.map((eventType) => (
              <li key={eventType.id} className="rounded-md border p-3">
                <div className="font-medium">{eventType.name}</div>
                <div className="text-muted-foreground text-sm">{eventType.description}</div>
                <div className="text-sm">{eventType.duration_minutes} мин</div>
              </li>
            ))}
          </ul>
        )}
      </section>

      <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
        <h2 className="text-xl font-semibold">Новый тип события</h2>
        <label className="flex flex-col gap-1 text-sm" htmlFor="event-type-name">
          Название
          <input
            id="event-type-name"
            className="rounded-md border px-3 py-2"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm" htmlFor="event-type-description">
          Описание
          <textarea
            id="event-type-description"
            className="rounded-md border px-3 py-2"
            value={description}
            onChange={(event) => setDescription(event.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm" htmlFor="event-type-duration">
          Длительность, мин
          <input
            id="event-type-duration"
            className="rounded-md border px-3 py-2"
            max={720}
            min={5}
            required
            type="number"
            value={duration}
            onChange={(event) => setDuration(event.target.value)}
          />
        </label>
        {error !== null && <p className="text-sm text-red-600">{error}</p>}
        <Button type="submit">Создать тип</Button>
      </form>

      <Link className="text-sm underline underline-offset-4" to="/">
        На главную
      </Link>
    </main>
  )
}

export { OwnerPage }
