import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { listEventTypes, type EventType } from '@/api/eventTypes'
import { listEventTypeSlots, type Slot } from '@/api/slots'

import { BookPage } from './BookPage'

vi.mock('@/api/eventTypes', () => ({
  listEventTypes: vi.fn(),
  createEventType: vi.fn(),
}))

vi.mock('@/api/slots', () => ({
  listEventTypeSlots: vi.fn(),
}))

const listEventTypesMock = vi.mocked(listEventTypes)
const listEventTypeSlotsMock = vi.mocked(listEventTypeSlots)

const MEETING: EventType = {
  id: 1,
  name: 'Встреча 60 минут',
  description: 'Обсуждение проекта',
  duration_minutes: 60,
  status: 'active',
}

const MORNING_SLOT: Slot = {
  start: '2026-11-20T04:00:00Z',
  end: '2026-11-20T05:00:00Z',
}

function localIso(offsetDays = 0): string {
  const now = new Date()
  const day = new Date(now.getFullYear(), now.getMonth(), now.getDate() + offsetDays)
  const month = String(day.getMonth() + 1).padStart(2, '0')
  const date = String(day.getDate()).padStart(2, '0')
  return `${day.getFullYear()}-${month}-${date}`
}

function renderBookPage() {
  return render(
    <MemoryRouter>
      <BookPage />
    </MemoryRouter>,
  )
}

function selectDay(offsetDays = 0) {
  const group = screen.getByRole('group', { name: 'Выберите день' })
  fireEvent.click(within(group).getAllByRole('button')[offsetDays])
}

describe('экран записи гостя', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('показывает доступные типы событий через сгенерированный SDK', async () => {
    listEventTypesMock.mockResolvedValue([MEETING])

    renderBookPage()

    expect(await screen.findByText('Встреча 60 минут')).toBeTruthy()
    expect(screen.getByText('60 мин')).toBeTruthy()
    expect(listEventTypesMock).toHaveBeenCalledTimes(1)
  })

  it('запрашивает слоты только после выбора типа и дня', async () => {
    listEventTypesMock.mockResolvedValue([MEETING])
    listEventTypeSlotsMock.mockResolvedValue([MORNING_SLOT])

    renderBookPage()
    await screen.findByText('Встреча 60 минут')
    expect(listEventTypeSlotsMock).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: /Встреча 60 минут/ }))
    expect(listEventTypeSlotsMock).not.toHaveBeenCalled()

    selectDay(0)

    await waitFor(() =>
      expect(listEventTypeSlotsMock).toHaveBeenCalledWith(MEETING.id, localIso(0)),
    )
  })

  it('показывает свободные слоты выбранного дня', async () => {
    listEventTypesMock.mockResolvedValue([MEETING])
    listEventTypeSlotsMock.mockResolvedValue([MORNING_SLOT])

    renderBookPage()
    await screen.findByText('Встреча 60 минут')
    fireEvent.click(screen.getByRole('button', { name: /Встреча 60 минут/ }))
    selectDay(0)

    expect(await screen.findByTestId('slot')).toBeTruthy()
  })

  it('показывает сообщение, когда свободных слотов нет', async () => {
    listEventTypesMock.mockResolvedValue([MEETING])
    listEventTypeSlotsMock.mockResolvedValue([])

    renderBookPage()
    await screen.findByText('Встреча 60 минут')
    fireEvent.click(screen.getByRole('button', { name: /Встреча 60 минут/ }))
    selectDay(0)

    expect(await screen.findByText('Нет свободных слотов')).toBeTruthy()
  })

  it('предлагает выбрать день из окна в 14 дней', async () => {
    listEventTypesMock.mockResolvedValue([MEETING])

    renderBookPage()
    await screen.findByText('Встреча 60 минут')

    const group = screen.getByRole('group', { name: 'Выберите день' })
    expect(within(group).getAllByRole('button')).toHaveLength(14)
  })
})
