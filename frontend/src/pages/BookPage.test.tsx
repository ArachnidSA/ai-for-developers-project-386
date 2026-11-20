import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { listEventTypes, type EventType } from '@/api/eventTypes'

import { BookPage } from './BookPage'

vi.mock('@/api/eventTypes', () => ({
  listEventTypes: vi.fn(),
  createEventType: vi.fn(),
}))

const listEventTypesMock = vi.mocked(listEventTypes)

const MEETING: EventType = {
  id: 1,
  name: 'Встреча 60 минут',
  description: 'Обсуждение проекта',
  duration_minutes: 60,
  status: 'active',
}

describe('экран записи гостя', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('показывает доступные типы событий через сгенерированный SDK', async () => {
    listEventTypesMock.mockResolvedValue([MEETING])

    render(
      <MemoryRouter>
        <BookPage />
      </MemoryRouter>,
    )

    expect(await screen.findByText('Встреча 60 минут')).toBeTruthy()
    expect(screen.getByText('60 мин')).toBeTruthy()
    expect(listEventTypesMock).toHaveBeenCalledTimes(1)
  })
})
