import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { listEventTypes, type EventType } from '@/api/eventTypes'

function BookPage() {
  const [eventTypes, setEventTypes] = useState<EventType[]>([])

  useEffect(() => {
    listEventTypes()
      .then(setEventTypes)
      .catch(() => setEventTypes([]))
  }, [])

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 p-8">
      <h1 className="text-3xl font-bold tracking-tight">Запись на звонок</h1>
      <p className="text-muted-foreground">Выберите подходящий тип события.</p>
      {eventTypes.length > 0 && (
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
      <Link className="text-sm underline underline-offset-4" to="/">
        На главную
      </Link>
    </main>
  )
}

export { BookPage }
