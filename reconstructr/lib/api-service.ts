"use client"

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true'

// Force mock mode for development
console.log("API Service initialized with USE_MOCK:", USE_MOCK)

// Mock data for development
const MOCK_DELAY = 1500

// Type definitions
export interface TimelineEvent {
  id: string
  videoId: string
  timestamp: string
  confidence: number
  thumbnailUrl?: string
  description: string
  startTime: number
  endTime: number
}

export interface GraphNode {
  id: string
  type: string
  label: string
  imageUrl?: string
}

export interface GraphEdge {
  source: string
  target: string
  label: string
}

export interface VisualTimelineEvent {
  id: string
  time: string
  location: string
  description: string
  isLocationChange: boolean
  thumbnailUrl?: string
}

export interface VideoFeed {
  id: string
  name: string
  location: string
  timestamp: string
  duration: number
  size: number
  fileUrl: string
  thumbnailUrl: string
  processed: boolean
}

export async function uploadVideo(
  file: File,
  metadata: {
    name?: string
    location?: string
    timestamp?: string
  },
): Promise<VideoFeed> {
  if (process.env.NEXT_PUBLIC_USE_MOCK === "true") {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Generate a random ID for the video
    const videoId = `video-${Math.random().toString(36).substring(2, 15)}`

    // Return mock data
    return {
      id: videoId,
      name: metadata.name || file.name,
      location: metadata.location || "Unknown",
      timestamp: metadata.timestamp || new Date().toISOString(),
      duration: Math.floor(Math.random() * 300) + 60, // Random duration between 60-360 seconds
      size: file.size,
      fileUrl: `/videos/${videoId}.mp4`,
      thumbnailUrl: "/placeholder.svg", // Use placeholder that exists
      processed: false,
    }
  }

  // Real API call
  const formData = new FormData()
  formData.append("file", file)
  formData.append("metadata", JSON.stringify(metadata))

  const response = await fetch(`${API_BASE_URL}/videos/upload`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Error uploading video: ${response.statusText}`)
  }

  return response.json()
}

export async function getVideos(): Promise<VideoFeed[]> {
  if (USE_MOCK) {
    // Simulate API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          {
            id: "video-1",
            name: "Main Entrance CCTV",
            location: "Building A Entrance",
            timestamp: "2023-04-15T09:30:00",
            duration: 120,
            size: 45000000,
            fileUrl: "/videos/video1.mp4",
            thumbnailUrl: "/placeholder.svg", // Use placeholder that exists
            processed: true,
          },
          {
            id: "video-2",
            name: "Parking Lot Camera",
            location: "North Parking Lot",
            timestamp: "2023-04-15T09:35:00",
            duration: 180,
            size: 65000000,
            fileUrl: "/videos/video2.mp4",
            thumbnailUrl: "/placeholder.svg", // Use placeholder that exists
            processed: true,
          },
          {
            id: "video-3",
            name: "Hallway Camera",
            location: "Building B Hallway",
            timestamp: "2023-04-15T09:40:00",
            duration: 150,
            size: 55000000,
            fileUrl: "/videos/video3.mp4",
            thumbnailUrl: "/placeholder.svg", // Use placeholder that exists
            processed: true,
          },
        ])
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
export interface Suspect {
  id: string
  name: string
  description: string
  imageUrl: string
  uploadedAt?: string
}

export async function uploadSuspect(
  file: File,
  metadata: {
    name?: string
    description?: string
  },
): Promise<Suspect> {
  if (process.env.NEXT_PUBLIC_USE_MOCK === "true") {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Generate a random ID for the suspect
    const suspectId = `suspect-${Math.random().toString(36).substring(2, 15)}`

    // Return mock data
    return {
      id: suspectId,
      name: metadata.name || "Unknown Suspect",
      description: metadata.description || "",
      imageUrl: "/placeholder.svg", // Use placeholder that exists
      uploadedAt: new Date().toISOString(),
    }
  }

  // Real API call
  const formData = new FormData()
  formData.append("file", file)
  formData.append("metadata", JSON.stringify(metadata))

  const response = await fetch(`${API_BASE_URL}/suspects/upload`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Error uploading suspect: ${response.statusText}`)
  }

  return response.json()
}

// Analysis API
export interface AnalysisRequest {
  suspectId?: string
  videoIds: string[]
  environmentVideoId?: string
  options?: {
    includeNarration?: boolean
    language?: string
    detectSuspiciousActivity?: boolean
    includeEnvironment?: boolean
  }
}

export interface AnalysisResult {
  id: string
  suspectId?: string
  timeline: TimelineEvent[]
  graph: {
    nodes: GraphNode[]
    edges: GraphEdge[]
  }
  summary: string
  narrationUrl?: string
  // Enhanced narrative features
  enhancedNarrative?: string
  activitySummary?: string
  locations?: string[]
  duration?: number
  firstSeen?: string
  lastSeen?: string
  visualTimeline?: VisualTimelineEvent[]
}

// Mock environment context for testing
const mockEnvironmentContext = {
  id: `env-${Date.now()}`,
  videoId: "mock-env-video",
  description: "The environment is a modern office building with multiple areas including a lobby, hallways, dining area, and office spaces. The building has a main entrance with glass doors leading to a spacious lobby with a reception desk. From the lobby, hallways lead to different areas including a dining area with tables and chairs, a kitchen for food preparation, meeting rooms, and open office spaces.",
  locations: [
    {name: "Main Entrance", description: "The main entrance to the building with glass doors"},
    {name: "Lobby", description: "Large open area with reception desk"},
    {name: "Hallway", description: "Long corridor connecting different areas"},
    {name: "Dining Area", description: "Open space with tables and chairs for eating"},
    {name: "Kitchen", description: "Food preparation area with appliances"},
    {name: "Meeting Room", description: "Enclosed space with conference table"},
    {name: "Office Area", description: "Open plan workspace with desks and computers"}
  ],
  status: "complete"
}

export async function runSuspectTracking(request: AnalysisRequest): Promise<AnalysisResult> {
  console.log("Running suspect tracking:", request)

  // Validate the request
  if (!request.suspectId) {
    throw new Error("Suspect ID is required")
  }

  if (!request.videoIds || request.videoIds.length === 0) {
    throw new Error("At least one video ID is required")
  }
  
  // Process environment video if specified and includeEnvironment is true
  if (request.environmentVideoId && request.options?.includeEnvironment) {
    try {
      await processEnvironmentVideo({videoId: request.environmentVideoId})
      console.log("Environment video processed successfully")
    } catch (error) {
      console.warn("Failed to process environment video, continuing without it:", error)
    }
  }
  
  // Always include environment context
  if (!request.options) {
    request.options = {}
  }
  request.options.includeEnvironment = true

  // Use mock data if specified in environment
  if (USE_MOCK) {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Generate a unique ID for this analysis
    const analysisId = `analysis-${Date.now()}`

    // Generate mock timeline and graph
    const timeline = generateMockTimeline(request)
    const graph = generateMockGraph(request)

    // Create a result with the unique ID
    const result: AnalysisResult = {
      id: analysisId,
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
    }

    // Return mock data with unique ID
    return result
  }

  // Real API call
  const response = await fetch(`${API_BASE_URL}/analysis/track-suspect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Error running analysis: ${response.statusText}`)
  }

  return response.json()
}

export async function runGeneralAnalysis(request: AnalysisRequest): Promise<AnalysisResult> {
  console.log("Running general analysis:", request)

  // Validate the request
  if (!request.videoIds || request.videoIds.length === 0) {
    throw new Error("At least one video ID is required")
  }
  
  // Always include environment context
  if (!request.options) {
    request.options = {}
  }
  request.options.includeEnvironment = true

  // Use mock data if specified in environment
  if (USE_MOCK) {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Generate a unique ID for this analysis
    const analysisId = `analysis-${Date.now()}`

    // Generate mock timeline and graph
    const timeline = generateMockTimeline(request)
    const graph = generateMockGraph(request)

    // Create a result with the unique ID
    const result: AnalysisResult = {
      id: analysisId,
      timeline: timeline,
      graph: graph,
      summary: "Multiple individuals were tracked across multiple camera feeds.",
      narrationUrl: request.options?.includeNarration ? "/mock-narration.mp3" : undefined,
      // Enhanced narrative features
      enhancedNarrative: "Multiple individuals were observed entering the mall through the north entrance. They proceeded to various locations, including the food court, electronics store, and clothing retailer.",
      activitySummary: "The individuals spent a total of 2 hours and 15 minutes in the mall, visiting 6 distinct locations. They interacted with at least 5 individuals.",
      locations: ["North Entrance", "Food Court", "Electronics Store", "Clothing Store", "South Exit"],
      duration: 135, // minutes
      firstSeen: timeline[0]?.timestamp || new Date().toISOString(),
      lastSeen: timeline[timeline.length - 1]?.timestamp || new Date().toISOString(),
      visualTimeline: generateMockVisualTimeline(timeline, graph)
    }

    // Return mock data with unique ID
    return result
  }

  // Real API call
  const response = await fetch(`${API_BASE_URL}/analysis/track-suspect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Error running analysis: ${response.statusText}`)
  }

  return response.json()
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
export async function generateKnowledgeGraph(analysisId: string): Promise<{ nodes: GraphNode[], edges: GraphEdge[] }> {
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
export interface Query {
  text: string
  language?: string
}

export async function queryAnalysis(analysisId: string, query: Query): Promise<string> {
  console.log("Querying analysis:", { analysisId, query })

  if (process.env.NEXT_PUBLIC_USE_MOCK === "true") {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // Return mock response based on query
    switch (query.text.toLowerCase()) {
      case "what time did the suspect enter the mall?":
        return "The suspect entered the mall at 10:15 AM through the north entrance."
      case "did the suspect interact with anyone?":
        return "Yes, the suspect interacted with a store employee in the electronics store for approximately 5 minutes, and later met with another individual wearing a red cap at the south exit."
      case "what did the suspect do in the clothing store?":
        return "The suspect selected several items in the clothing store and proceeded to the fitting rooms at 11:05 AM. They remained in the fitting room area for 7 minutes before exiting with what appears to be fewer items than they entered with, which may indicate suspicious behavior."
      case "summarize the suspect's path":
        return "The suspect entered through the north entrance at 10:15 AM, proceeded to the food court where they stayed for 12 minutes, then moved to the electronics store on the second floor. After spending time examining mobile phones and laptops, they went to the adjacent clothing retailer and used the fitting rooms. Finally, they exited through the south exit at 11:18 AM, where they met another individual."
      default:
        return "I don't have specific information about that query. Please try asking something about the suspect's movements, interactions, or activities observed in the footage."
    }
  }

  // Real API call
  const response = await fetch(`${API_BASE_URL}/analysis/${analysisId}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(query),
  })

  if (!response.ok) {
    throw new Error(`Error querying analysis: ${response.statusText}`)
  }

  const data = await response.json()
  return data.response
}



// Helper functions to generate mock data
export function generateMockTimeline(request: AnalysisRequest): TimelineEvent[] {
  const { suspectId, videoIds } = request

  // Generate random timeline events for each video
  const events: TimelineEvent[] = []

  videoIds.forEach((videoId, videoIndex) => {
    // Generate 3-5 events per video
    const numEvents = 3 + Math.floor(Math.random() * 3)
    
    for (let i = 0; i < numEvents; i++) {
      const timestamp = new Date()
      timestamp.setHours(10 + videoIndex)
      timestamp.setMinutes(15 + i * 10)
      
      events.push({
        id: `event-${videoId}-${i}`,
        videoId,
        timestamp: timestamp.toISOString(),
        confidence: 0.7 + Math.random() * 0.3,
        thumbnailUrl: "/placeholder.svg", // Use placeholder that exists
        description: `${suspectId ? 'Suspect' : 'Person'} detected in ${["entrance", "hallway", "cafeteria", "office", "exit"][i % 5]}`,
        startTime: i * 30,
        endTime: i * 30 + 15,
      })
    }
  })

  // Sort by timestamp
  return events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
}

// Generate visual timeline events for enhanced view
export function generateMockVisualTimeline(timeline: TimelineEvent[], graph: { nodes: GraphNode[], edges: GraphEdge[] }): VisualTimelineEvent[] {
  return timeline.map((event, index) => {
    // Find location name from graph
    const locationNode = graph.nodes.find((node: GraphNode) => node.id === event.videoId)
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

export function generateMockGraph(request: AnalysisRequest): { nodes: GraphNode[], edges: GraphEdge[] } {
  const { suspectId, videoIds } = request

  // Generate random graph data
  const nodes: GraphNode[] = []
  const edges: GraphEdge[] = []

  // Add suspect node if there is a suspectId
  if (suspectId) {
    nodes.push({
      id: suspectId,
      type: "suspect",
      label: "Suspect",
      imageUrl: "/placeholder.svg", // Use placeholder that exists
    })
  }

  // Add location nodes
  const locations = ["North Entrance", "Food Court", "Electronics Store", "Clothing Store", "South Exit"]
  
  locations.forEach((location, i) => {
    nodes.push({
      id: `location-${i}`,
      type: "location",
      label: location,
    })
  })

  // Add person nodes (other people in the video)
  const numPeople = 2 + Math.floor(Math.random() * 3)
  
  for (let i = 0; i < numPeople; i++) {
    nodes.push({
      id: `person-${i}`,
      type: "person",
      label: `Person ${i + 1}`,
      imageUrl: "/placeholder.svg", // Use placeholder that exists
    })
  }

  // Add edges between suspect and locations if there is a suspectId
  if (suspectId) {
    locations.forEach((_, i) => {
      if (Math.random() > 0.3) { // 70% chance to add an edge
        edges.push({
          source: suspectId,
          target: `location-${i}`,
          label: "visited",
        })
      }
    })

    // Add edges between suspect and people
    for (let i = 0; i < numPeople; i++) {
      if (Math.random() > 0.5) { // 50% chance to add an edge
        edges.push({
          source: suspectId,
          target: `person-${i}`,
          label: "interacted with",
        })
      }
    }
  }

  // Add edges between people and locations
  for (let i = 0; i < numPeople; i++) {
    const numLocations = 1 + Math.floor(Math.random() * 3)
    const locationIndices = new Set<number>()
    
    while (locationIndices.size < numLocations) {
      locationIndices.add(Math.floor(Math.random() * locations.length))
    }
    
    locationIndices.forEach(locationIndex => {
      edges.push({
        source: `person-${i}`,
        target: `location-${locationIndex}`,
        label: "visited",
      })
    })
  }

  return { nodes, edges }
}

// Suspicious behavior detection API
export interface SuspiciousAnalysisRequest {
  videoIds: string[]
}

export interface SuspiciousEvent {
  id: string
  videoId: string
  location: string
  frameNumber: number
  timestamp: string
  description: string
  confidence: number
  thumbnailUrl: string
}

export interface SuspiciousAnalysisResult {
  id: string
  status: string
  videoIds: string[]
  suspiciousEvents: SuspiciousEvent[]
  summary: string
}

export async function detectSuspiciousBehavior(request: SuspiciousAnalysisRequest): Promise<SuspiciousAnalysisResult> {
  console.log("Detecting suspicious behavior:", request)

  // Use mock data if specified in environment
  if (USE_MOCK) {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Generate a unique ID for this analysis
    const analysisId = `suspicious-${Date.now()}`

    // Generate mock suspicious events
    const suspiciousEvents: SuspiciousEvent[] = request.videoIds.flatMap((videoId, videoIndex) => {
      // Generate 1-3 suspicious events per video
      const numEvents = 1 + Math.floor(Math.random() * 3)
      const events: SuspiciousEvent[] = []
      
      for (let i = 0; i < numEvents; i++) {
        const timestamp = new Date()
        timestamp.setHours(10 + videoIndex)
        timestamp.setMinutes(15 + i * 10)
        
        events.push({
          id: `suspicious-${videoId}-${i}`,
          videoId,
          location: ["North Entrance", "Food Court", "Electronics Store", "Clothing Store", "South Exit"][videoIndex % 5],
          frameNumber: 10 + i * 20,
          timestamp: timestamp.toISOString(),
          description: [
            "Individual appears to be concealing an item in their jacket",
            "Person looking around suspiciously before taking an item from shelf",
            "Individual lingering in restricted area without apparent purpose",
            "Person making furtive movements near high-value merchandise",
            "Individual appears to be tampering with security equipment"
          ][i % 5],
          confidence: 70 + Math.floor(Math.random() * 20),
          thumbnailUrl: "/placeholder.svg" // Use placeholder that exists
        })
      }
      
      return events
    })

    // Create a result with the unique ID
    const result: SuspiciousAnalysisResult = {
      id: analysisId,
      status: "completed",
      videoIds: request.videoIds,
      suspiciousEvents,
      summary: "Multiple suspicious behaviors were detected across the analyzed videos. The most concerning include potential theft in the electronics store and tampering with security equipment near the south exit."
    }

    // Return mock data with unique ID
    return result
  }

  // Real API call to the suspicious behavior detection endpoint
  const response = await fetch(`${API_BASE_URL}/analysis/suspicious`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      videoIds: request.videoIds
    }),
  })

  if (!response.ok) {
    throw new Error(`Error detecting suspicious behavior: ${response.statusText}`)
  }

  return response.json()
}

// Environment context API
export interface EnvironmentProcessRequest {
  videoId: string
}

export interface EnvironmentContext {
  id: string
  videoId: string
  description: string
  locations: Array<{
    name: string
    description: string
  }>
}

export async function processEnvironmentVideo(request: EnvironmentProcessRequest): Promise<EnvironmentContext> {
  console.log("Processing environment video:", request)

  // Use mock data if specified in environment
  if (USE_MOCK) {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Generate a unique ID for this environment context
    const contextId = `env-${Date.now()}`

    // Return mock data
    return {
      id: contextId,
      videoId: request.videoId,
      description: "The environment is a modern office building with multiple areas including a lobby, hallways, dining area, and office spaces. The building has a main entrance with glass doors leading to a spacious lobby with a reception desk. From the lobby, hallways lead to different areas including a dining area with tables and chairs, a kitchen for food preparation, meeting rooms, and open office spaces.",
      locations: [
        {name: "Main Entrance", description: "The main entrance to the building with glass doors"},
        {name: "Lobby", description: "Large open area with reception desk"},
        {name: "Hallway", description: "Long corridor connecting different areas"},
        {name: "Dining Area", description: "Open space with tables and chairs for eating"},
        {name: "Kitchen", description: "Food preparation area with appliances"},
        {name: "Meeting Room", description: "Enclosed space with conference table"},
        {name: "Office Area", description: "Open plan workspace with desks and computers"}
      ]
    }
  }

  // Real API call to the environment processing endpoint
  const response = await fetch(`${API_BASE_URL}/environment/process`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      videoId: request.videoId
    }),
  })

  if (!response.ok) {
    throw new Error(`Error processing environment video: ${response.statusText}`)
  }

  return response.json()
}

// Enhanced timeline generation API
export interface TimelineGenerationRequest {
  analysisId: string
}

export interface EnhancedTimeline {
  id: string
  analysisId: string
  status: string
  events: TimelineEvent[]
  narrative: string
  visualTimeline: VisualTimelineEvent[]
}

export async function generateEnhancedTimeline(request: TimelineGenerationRequest): Promise<EnhancedTimeline> {
  console.log("Generating enhanced timeline:", request)

  // Use mock data if specified in environment
  if (USE_MOCK) {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Generate a unique ID for this timeline
    const timelineId = `timeline-${Date.now()}`

    // Get the timeline events from the analysis
    const timeline = generateMockTimeline({ videoIds: ["video-1", "video-2", "video-3"] })
    
    // Generate visual timeline
    const visualTimeline = generateMockVisualTimeline(timeline, { nodes: [], edges: [] })

    // Create a result with the unique ID
    const result: EnhancedTimeline = {
      id: timelineId,
      analysisId: request.analysisId,
      status: "completed",
      events: timeline,
      narrative: "The suspect was first observed entering the mall at 10:15 AM through the north entrance. Wearing a dark jacket and jeans, they proceeded directly to the food court where they remained for approximately 12 minutes.\n\nAt 10:27 AM, the suspect moved to the electronics store on the second floor, spending considerable time examining mobile phones and laptops. Security footage shows them engaging with a store employee for approximately 5 minutes, appearing to ask questions about specific products.\n\nAt 10:52 AM, the suspect left the electronics store and entered the adjacent clothing retailer. They selected several items and proceeded to the fitting rooms at 11:05 AM. The suspect remained in the fitting room area for 7 minutes before exiting with what appears to be fewer items than they entered with.\n\nThe suspect then proceeded to the mall's south exit at 11:18 AM, where they were observed meeting with another individual. This second person, wearing a red cap and light-colored jacket, engaged in conversation with the suspect for approximately 3 minutes before both individuals departed the premises together.",
      visualTimeline
    }

    // Return mock data with unique ID
    return result
  }

  // Real API call to the enhanced timeline generation endpoint
  const response = await fetch(`${API_BASE_URL}/timeline/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      analysisId: request.analysisId
    }),
  })

  if (!response.ok) {
    throw new Error(`Error generating enhanced timeline: ${response.statusText}`)
  }

  return response.json()
}
