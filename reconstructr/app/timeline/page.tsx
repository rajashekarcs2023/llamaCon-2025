"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Slider } from "@/components/ui/slider"
import { 
  Play, Pause, Volume2, VolumeX, MapPin, RefreshCw, Filter,
  Clock, Video, AlertCircle, Info, ChevronRight
} from "lucide-react"
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { Suspect, GraphNode, AnalysisResult, TimelineEvent, EnhancedAnalysisResult, VisualTimelineEvent } from "@/types"
import { runSuspectTracking } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import TimelineNarrative from "@/components/TimelineNarrative"
import VisualTimeline from "@/components/VisualTimeline"

export default function TimelinePage() {
  const searchParams = useSearchParams()
  const analysisId = searchParams.get("analysis")

  const [loading, setLoading] = useState(true)
  const [analysis, setAnalysis] = useState<EnhancedAnalysisResult | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null)
  const [playing, setPlaying] = useState(false)
  const [volume, setVolume] = useState(80)
  const [muted, setMuted] = useState(false)
  const [narrationEnabled, setNarrationEnabled] = useState(true)
  const [viewMode, setViewMode] = useState<'combined' | 'individual'>('combined')
  const [showEnhancedView, setShowEnhancedView] = useState(true)
  const [activeTab, setActiveTab] = useState<'narrative' | 'timeline'>('narrative')

  // Helper functions
  const formatTime = (timestamp: string) => {
    if (!timestamp) return ""
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  const formatDate = (timestamp: string) => {
    if (!timestamp) return ""
    return new Date(timestamp).toLocaleDateString()
  }

  const formatConfidence = (confidence: number) => {
    return `${Math.round(confidence)}%`
  }

  // Event handlers
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

  // Convert standard timeline events to visual timeline events
  const getVisualTimelineEvents = (): VisualTimelineEvent[] => {
    if (!analysis) return []

    // If we have pre-generated visual timeline, use it
    if (analysis.visualTimeline && analysis.visualTimeline.length > 0) {
      return analysis.visualTimeline
    }

    // Otherwise, convert standard timeline events
    return analysis.timeline.map((event, index) => {
      // Determine if this event represents a location change
      const prevEvent = index > 0 ? analysis.timeline[index - 1] : null
      const prevLocation = prevEvent ? 
        analysis.graph.nodes.find(node => node.id === prevEvent.videoId)?.label : ""
      const currentLocation = analysis.graph.nodes.find(node => node.id === event.videoId)?.label || "Unknown"
      const isLocationChange = prevLocation !== currentLocation && index > 0

      return {
        id: event.id,
        time: formatTime(event.timestamp),
        location: currentLocation,
        activity: event.description,
        thumbnailUrl: event.thumbnailUrl || "/placeholder.svg",
        confidence: event.confidence,
        isLocationChange,
        description: event.description
      }
    })
  }

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
            includeDetailedNarrative: true, // Enable enhanced narrative generation
          },
        }

        const result = await runSuspectTracking(mockRequest) as EnhancedAnalysisResult
        
        // Add enhanced narrative features for demo
        result.enhancedNarrative = "The suspect was first observed entering the mall at 10:15 AM through the north entrance. Wearing a dark jacket and jeans, they proceeded directly to the food court where they remained for approximately 12 minutes.\n\nAt 10:27 AM, the suspect moved to the electronics store on the second floor, spending considerable time examining mobile phones and laptops. Security footage shows them engaging with a store employee for approximately 5 minutes, appearing to ask questions about specific products.\n\nAt 10:52 AM, the suspect left the electronics store and entered the adjacent clothing retailer. They selected several items and proceeded to the fitting rooms at 11:05 AM. The suspect remained in the fitting room area for 7 minutes before exiting with what appears to be fewer items than they entered with.\n\nThe suspect then proceeded to the mall's south exit at 11:18 AM, where they were observed meeting with another individual. This second person, wearing a red cap and light-colored jacket, engaged in conversation with the suspect for approximately 3 minutes before both individuals departed the premises together."
        
        result.activitySummary = "The suspect spent 1 hour and 3 minutes in the mall, visiting 4 distinct locations: the north entrance, food court, electronics store, and clothing retailer. They interacted with at least 2 individuals: a store employee and an unidentified person wearing a red cap. The suspect appeared to be primarily interested in electronic devices and may have concealed merchandise while in the fitting room area."
        
        result.locations = ["North Entrance", "Food Court", "Electronics Store", "Clothing Store", "South Exit"]
        result.duration = 63 // minutes
        result.firstSeen = result.timeline[0]?.timestamp || ""
        result.lastSeen = result.timeline[result.timeline.length - 1]?.timestamp || ""
        
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

  // Loading state
  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight">Timeline Analysis</h1>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Label htmlFor="view-mode">View Mode:</Label>
              <Select 
                value={viewMode} 
                onValueChange={(value) => setViewMode(value as 'combined' | 'individual')}
              >
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select view mode" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="combined">Combined Timeline</SelectItem>
                  <SelectItem value="individual">Individual Videos</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button 
              onClick={() => {
                // Regenerate timeline
                setLoading(true);
                setTimeout(() => {
                  setLoading(false);
                }, 1500);
              }}
            >
              <RefreshCw className="mr-2 h-4 w-4" /> Regenerate Timeline
            </Button>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_350px]">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Video Evidence</CardTitle>
              </CardHeader>

              <CardContent className="p-0">
                {selectedEvent ? (
                  <div className="aspect-video w-full" />
                ) : (
                  <Skeleton className="aspect-video w-full" />
                )}
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

  // No analysis data
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

  // Main content
  return (
    <div className="container mx-auto p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Timeline Analysis</h1>
        <div className="flex items-center gap-2">
          <Button
            variant={showEnhancedView ? "default" : "outline"}
            size="sm"
            onClick={() => setShowEnhancedView(true)}
          >
            Enhanced View
          </Button>
          <Button
            variant={!showEnhancedView ? "default" : "outline"}
            size="sm"
            onClick={() => setShowEnhancedView(false)}
          >
            Standard View
          </Button>
        </div>
      </div>

      {showEnhancedView ? (
        // Enhanced view with detailed narrative
        <>
          <Tabs defaultValue="narrative" className="mb-6">
            <TabsList>
              <TabsTrigger value="narrative">Narrative View</TabsTrigger>
              <TabsTrigger value="timeline">Timeline View</TabsTrigger>
            </TabsList>
            
            <TabsContent value="narrative">
              <TimelineNarrative
                narrative={analysis.enhancedNarrative || "Detailed narrative is being generated..."}
                activitySummary={analysis.activitySummary || "Activity summary is being generated..."}
                locations={analysis.locations || ["Unknown"]}
                duration={analysis.duration || 0}
                firstSeen={analysis.firstSeen || analysis.timeline[0]?.timestamp}
                lastSeen={analysis.lastSeen || analysis.timeline[analysis.timeline.length - 1]?.timestamp}
              />
            </TabsContent>
            
            <TabsContent value="timeline">
              <div className="mb-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Suspect Movement Timeline</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="relative">
                      {/* Timeline line */}
                      <div className="absolute left-[7.5%] top-0 bottom-0 w-1 bg-muted" />
                      
                      {/* Timeline events */}
                      {(analysis.locations || []).map((location, index) => (
                        <div key={location} className="relative mb-8 flex">
                          {/* Location marker */}
                          <div className="absolute left-[7.5%] -ml-3 mt-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground">
                            <MapPin className="h-3 w-3" />
                          </div>
                          
                          {/* Location content */}
                          <div className="ml-[15%] flex-1">
                            <h3 className="text-lg font-semibold">{location}</h3>
                            <p className="text-sm text-muted-foreground">
                              {index === 0 
                                ? `First seen at ${formatTime(analysis.firstSeen || '')}` 
                                : index === ((analysis.locations || []).length - 1)
                                ? `Last seen at ${formatTime(analysis.lastSeen || '')}`
                                : `Visited at ${formatTime(analysis.timeline[index]?.timestamp || '')}`}
                            </p>
                            
                            {/* Events at this location */}
                            <div className="mt-2 space-y-2">
                              {getVisualTimelineEvents()
                                .filter(event => event.location === location)
                                .map(event => (
                                  <div 
                                    key={event.id} 
                                    className="flex cursor-pointer items-center gap-3 rounded-md border p-2 hover:bg-muted/50"
                                    onClick={() => {
                                      const originalEvent = analysis.timeline.find(e => e.id === event.id);
                                      if (originalEvent) handleEventSelect(originalEvent);
                                    }}
                                  >
                                    <div className="h-12 w-16 flex-shrink-0 overflow-hidden rounded">
                                      <img
                                        src={event.thumbnailUrl}
                                        alt={`Event at ${event.time}`}
                                        className="h-full w-full object-cover"
                                      />
                                    </div>
                                    <div>
                                      <p className="text-sm font-medium">{event.time}</p>
                                      <p className="text-xs text-muted-foreground">{event.activity}</p>
                                    </div>
                                    <Badge variant="outline" className="ml-auto">
                                      {formatConfidence(event.confidence)}
                                    </Badge>
                                  </div>
                                ))}
                            </div>
                            
                            {/* Connection arrow to next location */}
                            {index < (analysis.locations || []).length - 1 && (
                              <div className="mt-4 flex items-center text-muted-foreground">
                                <div className="h-px flex-1 bg-muted" />
                                <ChevronRight className="mx-2 h-4 w-4" />
                                <div className="h-px flex-1 bg-muted" />
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
          
          <div className="grid gap-6 md:grid-cols-3">
            <div className="md:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Video Evidence</CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedEvent ? (
                    <>
                      <div className="aspect-video overflow-hidden rounded-md bg-muted">
                        <img
                          src={selectedEvent.thumbnailUrl || "/placeholder.svg"}
                          alt={`Event ${selectedEvent.id}`}
                          className="h-full w-full object-cover"
                        />
                      </div>
                      <div className="mt-4 space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">{formatTime(selectedEvent.timestamp)}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <MapPin className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">
                                {analysis.graph.nodes.find((node) => node.id === selectedEvent.videoId)?.label || "Unknown location"}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Video className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm">
                                Video {selectedEvent.videoId}
                              </span>
                            </div>
                          </div>
                          <Badge>Confidence: {formatConfidence(selectedEvent.confidence)}</Badge>
                        </div>

                        <div className="flex items-center justify-between">
                          <Button variant="outline" size="icon" onClick={togglePlay}>
                            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                          </Button>
                          <div className="flex items-center gap-4">
                            <Button variant="outline" size="icon" onClick={toggleMute}>
                              {muted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                            </Button>
                            <div className="w-24">
                              <Slider
                                disabled={muted}
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
                          <h3 className="mb-2 text-sm font-medium">Event Details</h3>
                          <p className="text-sm text-muted-foreground">{selectedEvent?.description || 'No description available'}</p>
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

            <div>
              <VisualTimeline
                events={getVisualTimelineEvents()}
                locations={analysis.locations || []}
                onEventSelect={(eventId) => {
                  const event = analysis.timeline.find(e => e.id === eventId);
                  if (event) handleEventSelect(event);
                }}
                selectedEventId={selectedEvent?.id}
              />
            </div>
          </div>
        </>
      ) : (
        // Standard view (original)
        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Video Evidence</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedEvent ? (
                  <>
                    <div className="aspect-video overflow-hidden rounded-md bg-muted">
                      <img
                        src={selectedEvent.thumbnailUrl || "/placeholder.svg"}
                        alt={`Event ${selectedEvent.id}`}
                        className="h-full w-full object-cover"
                      />
                    </div>
                    <div className="mt-4 space-y-4">
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">{formatTime(selectedEvent?.timestamp || '')}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              {analysis.graph.nodes.find((node) => node.id === selectedEvent?.videoId)?.label || "Unknown location"}
                            </span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Video className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              Video {selectedEvent?.videoId}
                            </span>
                          </div>
                        </div>
                        <Badge>Confidence: {formatConfidence(selectedEvent.confidence)}</Badge>
                      </div>

                      <div className="flex items-center justify-between">
                        <Button variant="outline" size="icon" onClick={togglePlay}>
                          {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        </Button>
                        <div className="flex items-center gap-4">
                          <Button variant="outline" size="icon" onClick={toggleMute}>
                            {muted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                          </Button>
                          <div className="w-24">
                            <Slider
                              disabled={muted}
                              value={[volume]}
                              max={100}
                              step={1}
                              onValueChange={(value) => setVolume(value[0])}
                            />
                          </div>
                          <div className="flex items-center space-x-2">
                            <Label htmlFor="narration-standard" className="text-xs">
                              Narration
                            </Label>
                            <Switch id="narration-standard" checked={narrationEnabled} onCheckedChange={setNarrationEnabled} />
                          </div>
                        </div>
                        <div className="h-2 rounded-full bg-muted">
                          <div className="h-full rounded-full bg-primary" style={{ width: `${playing ? 50 : 0}%` }} />
                        </div>
                      </div>

                      <div className="rounded-md bg-muted p-4">
                        <h3 className="mb-2 text-sm font-medium">AI Analysis</h3>
                        <p className="text-sm text-muted-foreground">{analysis?.summary || 'No summary available'}</p>
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
      )}
    </div>
  )
}
