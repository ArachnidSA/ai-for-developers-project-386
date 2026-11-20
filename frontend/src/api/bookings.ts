import { client } from '@/api/client'
import {
  calendarApiCreateBooking,
  type ApiError,
  type Booking,
  type BookingCreate,
} from '@/api/generated'

export type { Booking, BookingCreate }

/** Конфликт: выбранный слот уже занят (`409` по контракту). */
export class BookingConflictError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'BookingConflictError'
  }
}

function detailOf(error: ApiError | undefined, fallback: string): string {
  return error?.detail ?? fallback
}

/** Создать запись гостем через сгенерированный SDK. */
export async function createBooking(body: BookingCreate): Promise<Booking> {
  const { data, error, response } = await calendarApiCreateBooking({ client, body })
  if (response?.status === 409) {
    throw new BookingConflictError(detailOf(error, 'Это время уже занято, выберите другой слот'))
  }
  if (data === undefined) {
    throw new Error(detailOf(error, 'Не удалось создать запись'))
  }
  return data
}
