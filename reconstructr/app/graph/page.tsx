"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Network,
  User,
  MapPin,
  Package,
  Users,
  ZoomIn,
  ZoomOut,
  Maximize,
  Volume2,
  VolumeX,
  AlertCircle,
  Info,
} from "lucide-react"
import type { GraphData, GraphNode, AnalysisResult } from "@/types"
import { runSuspectTracking } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

// Mock D3 force simulation
const ForceGraph = ({ data, onNodeClick }: { data: GraphData; onNodeClick: (node: GraphNode) => void }) => {
  return (
    <div className="relative h-full w-full overflow-hidden rounded-md bg-black/20 p-4">
      <div className="absolute right-4 top-4 flex space-x-2">
        <Button variant="outline" size="icon">
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon">
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon">
          <Maximize className="h-4 w-4" />
        </Button>
      </div>

      {/* This is a placeholder for the actual D3 force graph */}
      <div className="flex h-full flex-col items-center justify-center">
        <p className="mb-4 text-sm text-muted-foreground">Interactive Force Graph Visualization</p>
        <p className="text-xs text-muted-foreground">
          (In a real implementation, this would be a D3.js force-directed graph)
        </p>

        <div className="mt-8 grid grid-cols-2 gap-8">
          {data.nodes.slice(0, 6).map((node) => (
            <div
              key={node.id}
              className="flex cursor-pointer flex-col items-center space-y-2"
              onClick={() => onNodeClick(node)}
            >
              <div
                className={`flex h-16 w-16 items-center justify-center rounded-full ${
                  node.type === "suspect"
                    ? "bg-detective-primary"
                    : node.type === "location"
                      ? "bg-detective-secondary"
                      : node.type === "person"
                        ? "bg-detective-accent"
                        : "bg-muted"
                }`}
              >
                {node.type === "suspect" && <User className="h-8 w-8 text-white" />}
                {node.type === "location" && <MapPin className="h-8 w-8 text-white" />}
                {node.type === "person" && <Users className="h-8 w-8 text-white" />}
                {node.type === "object" && <Package className="h-8 w-8 text-white" />}
              </div>
              <span className="text-xs font-medium">{node.label}</span>
            </div>
          ))}
        </div>

        <div className="mt-8">
          <p className="text-xs text-muted-foreground">Click on a node to view details</p>
        </div>
      </div>
    </div>
  )
}

export default function GraphViewPage() {
  const searchParams = useSearchParams()
  const analysisId = searchParams.get("analysis")

  const [loading, setLoading] = useState(true)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [filterType, setFilterType] = useState<string | null>(null)

  // Fetch analysis data
  useEffect(() => {
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
      } catch (error) {
        console.error("Error fetching analysis:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [analysisId])

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node)
  }

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled)
  }

  const getFilteredGraph = () => {
    if (!analysis || !filterType) return analysis?.graph

    const filteredNodes = analysis.graph.nodes.filter((node) => !filterType || node.type === filterType)

    const nodeIds = new Set(filteredNodes.map((node) => node.id))

    const filteredEdges = analysis.graph.edges.filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))

    return {
      nodes: filteredNodes,
      edges: filteredEdges,
    }
  }

  const getNodeTypeCount = (type: string) => {
    if (!analysis) return 0
    return analysis.graph.nodes.filter((node) => node.type === type).length
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="mb-6 text-3xl font-bold tracking-tight">Knowledge Graph</h1>
        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2">
            <Card className="h-[600px]">
              <CardHeader>
                <Skeleton className="h-8 w-48" />
              </CardHeader>
              <CardContent className="h-[calc(100%-80px)]">
                <Skeleton className="h-full w-full" />
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
                  <Skeleton className="h-24 w-full" />
                  <Separator />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
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
        <h1 className="mb-6 text-3xl font-bold tracking-tight">Knowledge Graph</h1>
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
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Knowledge Graph</h1>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Graph Visualization */}
        <div className="md:col-span-2">
          <Card className="h-[600px]">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Suspect Movement Graph</CardTitle>
                <CardDescription>
                  Visualizing connections between suspect, locations, people, and objects
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="icon" onClick={toggleVoice}>
                  {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
                </Button>
                <Dialog>
                  <DialogTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <Info className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>About the Knowledge Graph</DialogTitle>
                      <DialogDescription>Understanding the visualization</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <p className="text-sm">
                        This knowledge graph visualizes the connections between the suspect, locations, people, and
                        objects identified in the analysis.
                      </p>
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium">Node Types:</h4>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="flex items-center space-x-2">
                            <div className="h-4 w-4 rounded-full bg-detective-primary" />
                            <span className="text-xs">Suspect</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="h-4 w-4 rounded-full bg-detective-secondary" />
                            <span className="text-xs">Location</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="h-4 w-4 rounded-full bg-detective-accent" />
                            <span className="text-xs">Person</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <div className="h-4 w-4 rounded-full bg-muted" />
                            <span className="text-xs">Object</span>
                          </div>
                        </div>
                      </div>
                      <p className="text-sm">
                        Click on any node to view more details about it. You can filter the graph by node type using the
                        tabs above the visualization.
                      </p>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent className="h-[calc(100%-80px)]">
              <Tabs defaultValue="all" className="h-full">
                <TabsList className="mb-4">
                  <TabsTrigger value="all" onClick={() => setFilterType(null)}>
                    All
                  </TabsTrigger>
                  <TabsTrigger value="suspect" onClick={() => setFilterType("suspect")}>
                    Suspect ({getNodeTypeCount("suspect")})
                  </TabsTrigger>
                  <TabsTrigger value="location" onClick={() => setFilterType("location")}>
                    Locations ({getNodeTypeCount("location")})
                  </TabsTrigger>
                  <TabsTrigger value="person" onClick={() => setFilterType("person")}>
                    People ({getNodeTypeCount("person")})
                  </TabsTrigger>
                  <TabsTrigger value="object" onClick={() => setFilterType("object")}>
                    Objects ({getNodeTypeCount("object")})
                  </TabsTrigger>
                </TabsList>

                <div className="h-[calc(100%-40px)]">
                  <ForceGraph data={getFilteredGraph() || { nodes: [], edges: [] }} onNodeClick={handleNodeClick} />
                </div>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        {/* Node Details */}
        <div>
          <Card className="h-[600px]">
            <CardHeader>
              <CardTitle>Node Details</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedNode ? (
                <div className="space-y-4">
                  <div className="flex items-center space-x-4">
                    <div
                      className={`flex h-12 w-12 items-center justify-center rounded-full ${
                        selectedNode.type === "suspect"
                          ? "bg-detective-primary"
                          : selectedNode.type === "location"
                            ? "bg-detective-secondary"
                            : selectedNode.type === "person"
                              ? "bg-detective-accent"
                              : "bg-muted"
                      }`}
                    >
                      {selectedNode.type === "suspect" && <User className="h-6 w-6 text-white" />}
                      {selectedNode.type === "location" && <MapPin className="h-6 w-6 text-white" />}
                      {selectedNode.type === "person" && <Users className="h-6 w-6 text-white" />}
                      {selectedNode.type === "object" && <Package className="h-6 w-6 text-white" />}
                    </div>
                    <div>
                      <h3 className="text-lg font-medium">{selectedNode.label}</h3>
                      <Badge variant="outline" className="capitalize">
                        {selectedNode.type}
                      </Badge>
                    </div>
                  </div>

                  {selectedNode.imageUrl && (
                    <div className="overflow-hidden rounded-md">
                      <img
                        src={selectedNode.imageUrl || "/placeholder.svg"}
                        alt={selectedNode.label}
                        className="h-48 w-full object-cover"
                      />
                    </div>
                  )}

                  <Separator />

                  {selectedNode.details && (
                    <div>
                      <h4 className="mb-1 text-sm font-medium">Details</h4>
                      <p className="text-sm text-muted-foreground">{selectedNode.details}</p>
                    </div>
                  )}

                  {selectedNode.timestamp && (
                    <div>
                      <h4 className="mb-1 text-sm font-medium">Timestamp</h4>
                      <p className="text-sm text-muted-foreground">
                        {new Date(selectedNode.timestamp).toLocaleString()}
                      </p>
                    </div>
                  )}

                  <div>
                    <h4 className="mb-1 text-sm font-medium">Connections</h4>
                    <ScrollArea className="h-[150px]">
                      <div className="space-y-2">
                        {analysis.graph.edges
                          .filter((edge) => edge.source === selectedNode.id || edge.target === selectedNode.id)
                          .map((edge) => {
                            const otherNodeId = edge.source === selectedNode.id ? edge.target : edge.source
                            const otherNode = analysis.graph.nodes.find((node) => node.id === otherNodeId)

                            if (!otherNode) return null

                            return (
                              <div
                                key={edge.id}
                                className="flex cursor-pointer items-center justify-between rounded-md p-2 hover:bg-muted/50"
                                onClick={() => setSelectedNode(otherNode)}
                              >
                                <div className="flex items-center space-x-2">
                                  <div
                                    className={`h-3 w-3 rounded-full ${
                                      otherNode.type === "suspect"
                                        ? "bg-detective-primary"
                                        : otherNode.type === "location"
                                          ? "bg-detective-secondary"
                                          : otherNode.type === "person"
                                            ? "bg-detective-accent"
                                            : "bg-muted"
                                    }`}
                                  />
                                  <span className="text-xs font-medium">{otherNode.label}</span>
                                </div>
                                <Badge variant="outline" className="text-xs">
                                  {edge.source === selectedNode.id ? edge.label : `was ${edge.label} by`}
                                </Badge>
                              </div>
                            )
                          })}
                      </div>
                    </ScrollArea>
                  </div>
                </div>
              ) : (
                <div className="flex h-full flex-col items-center justify-center">
                  <Network className="mb-4 h-10 w-10 text-muted-foreground" />
                  <p className="text-sm font-medium">No node selected</p>
                  <p className="text-xs text-muted-foreground">Click on a node in the graph to view details</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
