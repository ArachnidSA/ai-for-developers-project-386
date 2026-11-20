import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

function HomePage() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 p-8">
      <h1 className="text-3xl font-bold tracking-tight">Calendar</h1>
      <Card>
        <CardHeader>
          <CardTitle>Запись на звонок</CardTitle>
        </CardHeader>
        <CardContent>
          <Button asChild>
            <Link to="/book">
              Записаться
              <ArrowRight />
            </Link>
          </Button>
        </CardContent>
      </Card>
    </main>
  )
}

export { HomePage }
