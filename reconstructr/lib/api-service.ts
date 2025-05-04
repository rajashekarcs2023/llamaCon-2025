import type { VideoFeed, Suspect, TimelineEvent, GraphData, AnalysisRequest, AnalysisResult, Query } from "@/types"

// Mock data for development
const MOCK_DELAY = 1500

// Define GraphNode and GraphEdge interfaces
interface GraphNode {
  id: string
  type: string
  label: string
  imageUrl?: string
}

interface GraphEdge {
  id: string
  source: string
  target: string
  label: string
  timestamp?: string
}

// Video API
export async function uploadVideo(file: File, metadata: Partial<VideoFeed>): Promise<VideoFeed> {
  console.log("Uploading video:", file.name, metadata)
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

export async function getVideos(): Promise<VideoFeed[]> {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([])
    }, MOCK_DELAY)
  })
}

// Suspect API
export async function uploadSuspect(file: File, metadata: Partial<Suspect>): Promise<Suspect> {
  console.log("Uploading suspect image:", file.name, metadata)
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

// Analysis API
export async function runSuspectTracking(request: AnalysisRequest): Promise<AnalysisResult> {
  console.log("Running suspect tracking:", request)
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: `analysis-${Date.now()}`,
        suspectId: request.suspectId,
        timeline: generateMockTimeline(request),
        graph: generateMockGraph(request),
        summary:
          "Suspect was tracked across multiple camera feeds. First appeared at the north entrance at 10:15 AM, then moved through the main hall at 10:22 AM, and was last seen exiting through the east door at 10:45 AM.",
        narrationUrl: request.options?.includeNarration ? "/mock-narration.mp3" : undefined,
      })
    }, MOCK_DELAY * 2)
  })
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

  for (let i = 0; i < 5; i++) {
    const eventTime = new Date(baseTime)
    eventTime.setMinutes(baseTime.getMinutes() + i * 15)

    events.push({
      id: `event-${i}`,
      suspectId: request.suspectId,
      videoId: request.videoIds[Math.floor(Math.random() * request.videoIds.length)],
      timestamp: eventTime.toISOString(),
      confidence: 75 + Math.floor(Math.random() * 20),
      thumbnailUrl: `/placeholder.svg?height=180&width=320&query=Suspect%20sighting%20${i}`,
      description: `Suspect spotted at location ${i + 1}`,
      startTime: i * 30,
      endTime: i * 30 + 10,
    })
  }

  return events
}

function generateMockGraph(request: AnalysisRequest): GraphData {
  const nodes: GraphNode[] = [
    {
      id: "suspect-1",
      type: "suspect",
      label: "Suspect",
      imageUrl: `/placeholder.svg?height=50&width=50&query=Suspect%20face`,
    },
  ]

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
  const edges: GraphEdge[] = []

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
