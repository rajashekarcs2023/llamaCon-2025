// Video types
export interface VideoFeed {
  id: string
  name: string
  location: string
  timestamp: string
  duration: number
  fileUrl: string
  thumbnailUrl: string
  size: number
  processed: boolean
}

// Suspect types
export interface Suspect {
  id: string
  imageUrl: string
  name?: string
  description?: string
  lastSeen?: string
}

// Timeline types
export interface TimelineEvent {
  id: string
  suspectId: string
  videoId: string
  timestamp: string
  confidence: number
  thumbnailUrl: string
  description: string
  startTime: number
  endTime: number
}

// Graph types
export interface GraphNode {
  id: string
  type: "suspect" | "location" | "person" | "object"
  label: string
  imageUrl?: string
  details?: string
  timestamp?: string
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  label: string
  timestamp?: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

// Query types
export interface Query {
  id: string
  text: string
  timestamp: string
  response?: {
    text: string
    visualData?: any
  }
}

// Crew member types
export interface CrewMember {
  id: string
  name: string
  role: string
  avatarUrl: string
  expertise: string[]
  description: string
}

// Analysis types
export interface AnalysisRequest {
  suspectId: string
  videoIds: string[]
  timeframe?: {
    start: string
    end: string
  }
  options?: {
    includeNarration: boolean
    language: string
  }
}

export interface AnalysisResult {
  id: string
  suspectId: string
  timeline: TimelineEvent[]
  graph: GraphData
  summary: string
  narrationUrl?: string
}
