import { Link } from 'react-router-dom'

function BookPage() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 p-8">
      <h1 className="text-3xl font-bold tracking-tight">Запись на звонок</h1>
      <p className="text-muted-foreground">Экран записи гостя появится здесь.</p>
      <Link className="text-sm underline underline-offset-4" to="/">
        На главную
      </Link>
    </main>
  )
}

export { BookPage }
