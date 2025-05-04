"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Play, Pause, Volume2, VolumeX, Clock, MapPin, Video, AlertCircle } from "lucide-react"
import type { TimelineEvent, AnalysisResult } from "@/types"
import { runSuspectTracking } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function TimelinePage() {
  const searchParams = useSearchParams()
  const analysisId = searchParams.get("analysis")

  const [loading, setLoading] = useState(true)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null)
  const [playing, setPlaying] = useState(false)
  const [volume, setVolume] = useState(80)
  const [muted, setMuted] = useState(false)
  const [narrationEnabled, setNarrationEnabled] = useState(true)

  // Fetch analysis data
  useEffect(() => {
    if (!analysisId) return

    const fetchAnalysis = async () => {
      setLoading(true)
      try {
        // In a real app, you would fetch the analysis by ID
        // For now, we'll simulate it with a mock request
        const mockRequest = {
          suspectId: "suspect-1",
          videoIds: ["video-1", "video-2", "video-3"],
          options: {
            includeNarration: true,
            language: "en",
          },
        }

        const result = await runSuspectTracking(mockRequest)
        setAnalysis(result)

        if (result.timeline.length > 0) {
          setSelectedEvent(result.timeline[0])
        }
      } catch (error) {
        console.error("Error fetching analysis:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [analysisId])

  const handleEventSelect = (event: TimelineEvent) => {
    setSelectedEvent(event)
    setPlaying(false)
  }

  const togglePlay = () => {
    setPlaying(!playing)
  }

  const toggleMute = () => {
    setMuted(!muted)
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  const formatConfidence = (confidence: number) => {
    return `${confidence}%`
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="mb-6 text-3xl font-bold tracking-tight">Timeline Analysis</h1>
        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <Skeleton className="h-8 w-48" />
              </CardHeader>
              <CardContent>
                <Skeleton className="aspect-video w-full" />
                <div className="mt-4 space-y-4">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                </div>
              </CardContent>
            </Card>
          </div>
          <div>
            <Card>
              <CardHeader>
                <Skeleton className="h-8 w-32" />
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="flex gap-4">
                      <Skeleton className="h-16 w-24" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-2/3" />
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

  if (!analysis) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="mb-6 text-3xl font-bold tracking-tight">Timeline Analysis</h1>
        <Card>
          <CardContent className="flex h-[300px] flex-col items-center justify-center">
            <AlertCircle className="mb-4 h-10 w-10 text-muted-foreground" />
            <p className="text-lg font-medium">No analysis data found</p>
            <p className="text-sm text-muted-foreground">Please run an analysis from the Suspect Identification page</p>
            <Button className="mt-4" asChild>
              <a href="/suspect">Go to Suspect Identification</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Timeline Analysis</h1>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Video Player and Details */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Suspect Sighting</CardTitle>
              <Badge variant="outline">
                Confidence: {selectedEvent ? formatConfidence(selectedEvent.confidence) : "N/A"}
              </Badge>
            </CardHeader>
            <CardContent>
              {selectedEvent ? (
                <>
                  <div className="relative aspect-video overflow-hidden rounded-md bg-black">
                    <img
                      src={selectedEvent.thumbnailUrl || "/placeholder.svg"}
                      alt="Suspect sighting"
                      className="h-full w-full object-cover"
                    />
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity hover:opacity-100">
                      <Button variant="ghost" size="icon" className="text-white" onClick={togglePlay}>
                        {playing ? <Pause className="h-8 w-8" /> : <Play className="h-8 w-8" />}
                      </Button>
                    </div>
                  </div>

                  <div className="mt-4 space-y-4">
                    <div>
                      <p className="text-sm font-medium">{selectedEvent.description}</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Clock className="mr-1 h-3 w-3" />
                          {formatTime(selectedEvent.timestamp)}
                        </div>
                        <div className="flex items-center text-xs text-muted-foreground">
                          <MapPin className="mr-1 h-3 w-3" />
                          Location ID: {selectedEvent.videoId}
                        </div>
                        <div className="flex items-center text-xs text-muted-foreground">
                          <Video className="mr-1 h-3 w-3" />
                          Clip: {selectedEvent.startTime}s - {selectedEvent.endTime}s
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Button variant="ghost" size="icon" onClick={togglePlay}>
                            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                          </Button>
                          <Button variant="ghost" size="icon" onClick={toggleMute}>
                            {muted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                          </Button>
                          <Slider
                            className="w-24"
                            value={[volume]}
                            max={100}
                            step={1}
                            onValueChange={(value) => setVolume(value[0])}
                          />
                        </div>
                        <div className="flex items-center space-x-2">
                          <Label htmlFor="narration" className="text-xs">
                            Narration
                          </Label>
                          <Switch id="narration" checked={narrationEnabled} onCheckedChange={setNarrationEnabled} />
                        </div>
                      </div>
                      <div className="h-2 rounded-full bg-muted">
                        <div className="h-full rounded-full bg-primary" style={{ width: `${playing ? 50 : 0}%` }} />
                      </div>
                    </div>

                    <div className="rounded-md bg-muted p-4">
                      <h3 className="mb-2 text-sm font-medium">AI Analysis</h3>
                      <p className="text-sm text-muted-foreground">{analysis.summary}</p>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex aspect-video flex-col items-center justify-center rounded-md border">
                  <AlertCircle className="mb-4 h-10 w-10 text-muted-foreground" />
                  <p className="text-sm font-medium">No event selected</p>
                  <p className="text-xs text-muted-foreground">Select an event from the timeline</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Timeline Events */}
        <div>
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Timeline Events</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="relative space-y-4 pl-6">
                  {/* Timeline line */}
                  <div className="absolute inset-y-0 left-2 w-px bg-muted" />

                  {analysis.timeline.map((event) => (
                    <div
                      key={event.id}
                      className={`relative cursor-pointer rounded-md border p-3 transition-colors ${
                        selectedEvent?.id === event.id ? "border-primary bg-primary/10" : "hover:bg-muted/50"
                      }`}
                      onClick={() => handleEventSelect(event)}
                    >
                      {/* Timeline dot */}
                      <div
                        className={`absolute -left-6 top-1/2 h-4 w-4 -translate-y-1/2 rounded-full border-2 ${
                          selectedEvent?.id === event.id
                            ? "border-primary bg-background"
                            : "border-muted-foreground bg-background"
                        }`}
                      />

                      <div className="flex gap-3">
                        <div className="h-16 w-24 flex-shrink-0 overflow-hidden rounded">
                          <img
                            src={event.thumbnailUrl || "/placeholder.svg"}
                            alt={`Event ${event.id}`}
                            className="h-full w-full object-cover"
                          />
                        </div>
                        <div>
                          <p className="text-sm font-medium">{formatTime(event.timestamp)}</p>
                          <p className="text-xs text-muted-foreground">{event.description}</p>
                          <Badge variant="outline" className="mt-1">
                            Confidence: {formatConfidence(event.confidence)}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
