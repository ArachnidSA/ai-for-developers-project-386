import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { AppRoutes } from './App'

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AppRoutes />
    </MemoryRouter>,
  )
}

describe('маршрутизация', () => {
  it('на / показывает главное окно', () => {
    renderAt('/')

    expect(screen.getByRole('heading', { name: 'Calendar' })).toBeTruthy()
  })

  it('на /book показывает экран записи', () => {
    renderAt('/book')

    expect(screen.getByRole('heading', { name: 'Запись на звонок' })).toBeTruthy()
  })

  it('на /owner показывает экран владельца', () => {
    renderAt('/owner')

    expect(screen.getByRole('heading', { name: 'Админка' })).toBeTruthy()
  })

  it('на неизвестном пути показывает «страница не найдена»', () => {
    renderAt('/нет-такой-страницы')

    expect(screen.getByRole('heading', { name: 'Страница не найдена' })).toBeTruthy()
  })
})
