import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { createEventType, listEventTypes, type EventType } from '@/api/eventTypes'

import { OwnerPage } from './OwnerPage'

vi.mock('@/api/eventTypes', () => ({
  listEventTypes: vi.fn(),
  createEventType: vi.fn(),
}))

const listEventTypesMock = vi.mocked(listEventTypes)
const createEventTypeMock = vi.mocked(createEventType)

const CONSULTATION: EventType = {
  id: 1,
  name: 'Консультация',
  description: 'Разбор задачи',
  duration_minutes: 30,
  status: 'active',
}

function renderOwner() {
  return render(
    <MemoryRouter>
      <OwnerPage />
    </MemoryRouter>,
  )
}

describe('экран владельца', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('показывает типы событий, полученные через сгенерированный SDK', async () => {
    listEventTypesMock.mockResolvedValue([CONSULTATION])

    renderOwner()

    expect(await screen.findByText('Консультация')).toBeTruthy()
    expect(screen.getByText('Разбор задачи')).toBeTruthy()
    expect(screen.getByText('30 мин')).toBeTruthy()
    expect(listEventTypesMock).toHaveBeenCalledTimes(1)
  })

  it('показывает пустое состояние, когда типов ещё нет', async () => {
    listEventTypesMock.mockResolvedValue([])

    renderOwner()

    expect(await screen.findByText('Типы событий пока не заведены')).toBeTruthy()
  })

  it('создаёт тип через SDK и обновляет список', async () => {
    listEventTypesMock.mockResolvedValueOnce([]).mockResolvedValueOnce([CONSULTATION])
    createEventTypeMock.mockResolvedValue(CONSULTATION)

    renderOwner()
    await screen.findByText('Типы событий пока не заведены')

    fireEvent.change(screen.getByLabelText('Название'), {
      target: { value: 'Консультация' },
    })
    fireEvent.change(screen.getByLabelText('Описание'), {
      target: { value: 'Разбор задачи' },
    })
    fireEvent.change(screen.getByLabelText('Длительность, мин'), {
      target: { value: '30' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Создать тип' }))

    await waitFor(() =>
      expect(createEventTypeMock).toHaveBeenCalledWith({
        name: 'Консультация',
        description: 'Разбор задачи',
        duration_minutes: 30,
      }),
    )
    expect(await screen.findByText('Консультация')).toBeTruthy()
  })
})
