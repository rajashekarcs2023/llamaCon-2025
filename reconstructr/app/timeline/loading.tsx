import { Skeleton } from "@/components/ui/skeleton"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function Loading() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-6 flex items-center justify-between">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-9 w-40" />
      </div>
      
      {/* Narrative skeleton */}
      <Card className="mb-6">
        <CardHeader>
          <Skeleton className="h-8 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <div className="flex flex-wrap gap-2 mt-4">
              <Skeleton className="h-6 w-20" />
              <Skeleton className="h-6 w-24" />
              <Skeleton className="h-6 w-16" />
            </div>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid gap-6 md:grid-cols-3">
        {/* Video evidence skeleton */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-8 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="aspect-video w-full" />
              <div className="mt-4 space-y-4">
                <div className="flex justify-between">
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-48" />
                  </div>
                  <Skeleton className="h-6 w-24" />
                </div>
                <div className="flex justify-between items-center">
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-8 w-8 rounded-full" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                </div>
                <Skeleton className="h-24 w-full" />
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Timeline skeleton */}
        <div>
          <Card>
            <CardHeader>
              <Skeleton className="h-8 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="flex gap-3 p-3 border rounded-md">
                    <Skeleton className="h-16 w-24" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-6 w-28" />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
