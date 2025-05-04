import type { VideoFeed, Suspect, TimelineEvent, GraphData, AnalysisRequest, AnalysisResult, Query, EnhancedAnalysisResult, VisualTimelineEvent } from "@/types"

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

// Mock data for development
const MOCK_DELAY = 1500

// Using types directly from the types file
import type { GraphNode, GraphEdge } from "@/types"

// Video API
export async function uploadVideo(file: File, metadata: Partial<VideoFeed>): Promise<VideoFeed> {
  console.log("Uploading video:", file.name, metadata)
  
  if (USE_MOCK) {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: `video-${Date.now()}`,
          name: metadata.name || file.name,
          location: metadata.location || "Unknown",
          timestamp: metadata.timestamp || new Date().toISOString(),
          duration: 120, // 2 minutes
          fileUrl: URL.createObjectURL(file),
          thumbnailUrl: `/placeholder.svg?height=180&width=320&query=CCTV%20${file.name}`,
          size: file.size,
          processed: false,
        })
      }, MOCK_DELAY)
    })
  }
  
  // Real API call
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', metadata.name || file.name)
  formData.append('location', metadata.location || 'Unknown')
  formData.append('timestamp', metadata.timestamp || new Date().toISOString())
  
  const response = await fetch(`${API_BASE_URL}/videos/upload`, {
    method: 'POST',
    body: formData,
  })
  
  if (!response.ok) {
    throw new Error(`Failed to upload video: ${response.statusText}`)
  }
  
  return await response.json()
}

export async function getVideos(): Promise<VideoFeed[]> {
  if (USE_MOCK) {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([])
      }, MOCK_DELAY)
    })
  }
  
  // Real API call
  const response = await fetch(`${API_BASE_URL}/videos`)
  
  if (!response.ok) {
    throw new Error(`Failed to get videos: ${response.statusText}`)
  }
  
  return await response.json()
}

// Suspect API
export async function uploadSuspect(file: File, metadata: Partial<Suspect>): Promise<Suspect> {
  console.log("Uploading suspect image:", file.name, metadata)
  
  if (USE_MOCK) {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: `suspect-${Date.now()}`,
          imageUrl: URL.createObjectURL(file),
          name: metadata.name || "Unknown",
          description: metadata.description || "",
        })
      }, MOCK_DELAY)
    })
  }
  
  // Real API call
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', metadata.name || 'Unknown')
  formData.append('description', metadata.description || '')
  
  const response = await fetch(`${API_BASE_URL}/suspects/upload`, {
    method: 'POST',
    body: formData,
  })
  
  if (!response.ok) {
    throw new Error(`Failed to upload suspect: ${response.statusText}`)
  }
  
  return await response.json()
}

// Analysis API
export async function runSuspectTracking(request: AnalysisRequest): Promise<EnhancedAnalysisResult> {
  console.log("Running suspect tracking:", request)
  
  if (USE_MOCK) {
    // Simulate API call with enhanced features
    return new Promise((resolve) => {
      setTimeout(() => {
        const timeline = generateMockTimeline(request)
        const graph = generateMockGraph(request)
        
        // Create enhanced result with narrative
        resolve({
          id: `analysis-${Date.now()}`,
          suspectId: request.suspectId,
          timeline: timeline,
          graph: graph,
          summary: "Suspect was tracked across multiple camera feeds. First appeared at the north entrance at 10:15 AM, then moved through the main hall at 10:22 AM, and was last seen exiting through the east door at 10:45 AM.",
          narrationUrl: request.options?.includeNarration ? "/mock-narration.mp3" : undefined,
          // Enhanced narrative features
          enhancedNarrative: "The suspect was first observed entering the mall at 10:15 AM through the north entrance. Wearing a dark jacket and jeans, they proceeded directly to the food court where they remained for approximately 12 minutes.\n\nAt 10:27 AM, the suspect moved to the electronics store on the second floor, spending considerable time examining mobile phones and laptops. Security footage shows them engaging with a store employee for approximately 5 minutes, appearing to ask questions about specific products.\n\nAt 10:52 AM, the suspect left the electronics store and entered the adjacent clothing retailer. They selected several items and proceeded to the fitting rooms at 11:05 AM. The suspect remained in the fitting room area for 7 minutes before exiting with what appears to be fewer items than they entered with.\n\nThe suspect then proceeded to the mall's south exit at 11:18 AM, where they were observed meeting with another individual. This second person, wearing a red cap and light-colored jacket, engaged in conversation with the suspect for approximately 3 minutes before both individuals departed the premises together.",
          activitySummary: "The suspect spent 1 hour and 3 minutes in the mall, visiting 4 distinct locations: the north entrance, food court, electronics store, and clothing retailer. They interacted with at least 2 individuals: a store employee and an unidentified person wearing a red cap. The suspect appeared to be primarily interested in electronic devices and may have concealed merchandise while in the fitting room area.",
          locations: ["North Entrance", "Food Court", "Electronics Store", "Clothing Store", "South Exit"],
          duration: 63, // minutes
          firstSeen: timeline[0]?.timestamp || new Date().toISOString(),
          lastSeen: timeline[timeline.length - 1]?.timestamp || new Date().toISOString(),
          visualTimeline: generateMockVisualTimeline(timeline, graph)
        })
      }, MOCK_DELAY * 2)
    })
  }
  
  // Real API call
  const response = await fetch(`${API_BASE_URL}/analysis/track-suspect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })
  
  if (!response.ok) {
    throw new Error(`Failed to run suspect tracking: ${response.statusText}`)
  }
  
  return await response.json()
}

// Timeline API
export async function generateTimeline(analysisId: string): Promise<TimelineEvent[]> {
  console.log("Generating timeline for analysis:", analysisId)
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([]) // This would be populated by the runSuspectTracking function
    }, MOCK_DELAY)
  })
}

// Graph API
export async function generateKnowledgeGraph(analysisId: string): Promise<GraphData> {
  console.log("Generating knowledge graph for analysis:", analysisId)
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        nodes: [],
        edges: [],
      }) // This would be populated by the runSuspectTracking function
    }, MOCK_DELAY)
  })
}

// Query API
export async function submitQuery(text: string, analysisId?: string): Promise<Query> {
  console.log("Submitting query:", text, "for analysis:", analysisId)
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: `query-${Date.now()}`,
        text,
        timestamp: new Date().toISOString(),
        response: {
          text: `Based on the analysis, the suspect was last seen at the east exit at 10:45 AM. They were wearing a dark jacket and carrying a backpack. The confidence score for this identification is 87%.`,
          visualData: {
            type: "image",
            url: `/placeholder.svg?height=300&width=400&query=Suspect%20at%20east%20exit`,
          },
        },
      })
    }, MOCK_DELAY)
  })
}

// Helper functions to generate mock data
function generateMockTimeline(request: AnalysisRequest): TimelineEvent[] {
  const events: TimelineEvent[] = []
  const baseTime = new Date()
  const locations = ["North Entrance", "Food Court", "Electronics Store", "Clothing Store", "South Exit"]

  for (let i = 0; i < 5; i++) {
    const eventTime = new Date(baseTime)
    eventTime.setMinutes(baseTime.getMinutes() + i * 15)

    events.push({
      id: `event-${i}`,
      suspectId: request.suspectId,
      videoId: `location-${i}`, // This will match our graph node IDs
      timestamp: eventTime.toISOString(),
      confidence: 75 + Math.floor(Math.random() * 20),
      thumbnailUrl: `/placeholder.svg?height=180&width=320&query=Suspect%20at%20${encodeURIComponent(locations[i])}`,
      description: `Suspect spotted at ${locations[i]}`,
      startTime: i * 30,
      endTime: i * 30 + 10,
    })
  }

  return events
}

// Generate visual timeline events for enhanced view
function generateMockVisualTimeline(timeline: TimelineEvent[], graph: GraphData): VisualTimelineEvent[] {
  return timeline.map((event, index) => {
    // Find location name from graph
    const locationNode = graph.nodes.find(node => node.id === event.videoId)
    const locationName = locationNode?.label || "Unknown"
    
    // Determine if this is a location change
    const isLocationChange = index > 0
    
    // Format time
    const time = new Date(event.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
    
    return {
      id: event.id,
      time,
      location: locationName,
      activity: event.description,
      thumbnailUrl: event.thumbnailUrl,
      confidence: event.confidence,
      isLocationChange,
      description: event.description
    }
  })
}

function generateMockGraph(request: AnalysisRequest): GraphData {
  const nodes: GraphNode[] = [
    {
      id: "suspect-1",
      type: "suspect",
      label: "Suspect",
      imageUrl: `/placeholder.svg?height=50&width=50&query=Suspect%20face`,
    },
  ] as GraphNode[]

  const locations = ["North Entrance", "Main Hall", "Cafeteria", "Corridor B", "East Exit"]
  const objects = ["Backpack", "Phone", "Keys"]
  const people = ["Security Guard", "Receptionist", "Visitor"]

  // Add location nodes
  locations.forEach((location, i) => {
    nodes.push({
      id: `location-${i}`,
      type: "location",
      label: location,
    })
  })

  // Add object nodes
  objects.forEach((object, i) => {
    nodes.push({
      id: `object-${i}`,
      type: "object",
      label: object,
    })
  })

  // Add person nodes
  people.forEach((person, i) => {
    nodes.push({
      id: `person-${i}`,
      type: "person",
      label: person,
    })
  })

  // Create edges
  const edges: GraphEdge[] = [] as GraphEdge[]

  // Connect suspect to locations
  locations.forEach((_, i) => {
    const baseTime = new Date()
    baseTime.setMinutes(baseTime.getMinutes() + i * 15)

    edges.push({
      id: `edge-suspect-location-${i}`,
      source: "suspect-1",
      target: `location-${i}`,
      label: "visited",
      timestamp: baseTime.toISOString(),
    })
  })

  // Connect suspect to objects
  objects.forEach((_, i) => {
    edges.push({
      id: `edge-suspect-object-${i}`,
      source: "suspect-1",
      target: `object-${i}`,
      label: "carried",
    })
  })

  // Connect suspect to people
  people.forEach((_, i) => {
    edges.push({
      id: `edge-suspect-person-${i}`,
      source: "suspect-1",
      target: `person-${i}`,
      label: "interacted with",
    })
  })

  return { nodes, edges }
}
