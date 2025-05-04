"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import {
  Users,
  Video,
  TimerIcon as Timeline,
  Network,
  MessageSquare,
  Volume2,
  VolumeX,
  Play,
  Pause,
} from "lucide-react"
import type { CrewMember } from "@/types"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// Mock crew members
const crewMembers: CrewMember[] = [
  {
    id: "crew-1",
    name: "Video Analyst",
    role: "Video Processing Specialist",
    avatarUrl: "/placeholder.svg?height=100&width=100&query=Video%20Analyst",
    expertise: ["Video Processing", "Object Detection", "Scene Analysis"],
    description:
      "Specializes in analyzing video feeds to identify suspects, objects, and activities. Uses computer vision algorithms to enhance footage and extract key details.",
  },
  {
    id: "crew-2",
    name: "Timeline Builder",
    role: "Chronology Expert",
    avatarUrl: "/placeholder.svg?height=100&width=100&query=Timeline%20Builder",
    expertise: ["Event Sequencing", "Time Analysis", "Pattern Recognition"],
    description:
      "Creates comprehensive timelines of suspect movements and activities. Identifies patterns in behavior and movement across multiple camera feeds.",
  },
  {
    id: "crew-3",
    name: "Suspect Tracker",
    role: "Identification Specialist",
    avatarUrl: "/placeholder.svg?height=100&width=100&query=Suspect%20Tracker",
    expertise: ["Facial Recognition", "Gait Analysis", "Clothing Analysis"],
    description:
      "Tracks suspects across multiple camera feeds using advanced recognition techniques. Specializes in identifying individuals even with partial views or disguises.",
  },
  {
    id: "crew-4",
    name: "Knowledge Grapher",
    role: "Relationship Analyst",
    avatarUrl: "/placeholder.svg?height=100&width=100&query=Knowledge%20Grapher",
    expertise: ["Network Analysis", "Relationship Mapping", "Spatial Analysis"],
    description:
      "Maps connections between people, places, and objects in an investigation. Creates visual representations of complex relationships and movement patterns.",
  },
  {
    id: "crew-5",
    name: "Query Assistant",
    role: "Investigation Guide",
    avatarUrl: "/placeholder.svg?height=100&width=100&query=Query%20Assistant",
    expertise: ["Natural Language Processing", "Evidence Retrieval", "Case Analysis"],
    description:
      "Answers questions about the investigation using natural language. Retrieves relevant evidence and provides insights based on the collected data.",
  },
]

export default function CrewPage() {
  const [selectedMember, setSelectedMember] = useState<CrewMember>(crewMembers[0])
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [playing, setPlaying] = useState(false)

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled)
  }

  const togglePlay = () => {
    setPlaying(!playing)
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Investigation Crew</h1>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Crew Members List */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>AI Crew Members</CardTitle>
              <CardDescription>Specialized AI assistants for your investigation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {crewMembers.map((member) => (
                  <div
                    key={member.id}
                    className={`flex cursor-pointer items-center space-x-4 rounded-md p-3 transition-colors ${
                      selectedMember.id === member.id ? "bg-detective-primary/10" : "hover:bg-muted/50"
                    }`}
                    onClick={() => setSelectedMember(member)}
                  >
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-detective-primary text-white">
                        {member.name.charAt(0)}
                      </AvatarFallback>
                      <AvatarImage src={member.avatarUrl || "/placeholder.svg"} alt={member.name} />
                    </Avatar>
                    <div>
                      <p className="font-medium">{member.name}</p>
                      <p className="text-xs text-muted-foreground">{member.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Crew Member Details */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>{selectedMember.name}</CardTitle>
                <CardDescription>{selectedMember.role}</CardDescription>
              </div>
              <div className="flex space-x-2">
                <Button variant="ghost" size="icon" onClick={toggleVoice}>
                  {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
                </Button>
                <Button variant="ghost" size="icon" onClick={togglePlay}>
                  {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-3">
                <div className="md:col-span-1">
                  <div className="overflow-hidden rounded-md">
                    <img
                      src={selectedMember.avatarUrl || "/placeholder.svg"}
                      alt={selectedMember.name}
                      className="aspect-square h-full w-full object-cover"
                    />
                  </div>

                  <div className="mt-4 space-y-2">
                    <h3 className="text-sm font-medium">Expertise</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedMember.expertise.map((skill) => (
                        <Badge key={skill} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="md:col-span-2">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium">About</h3>
                      <p className="mt-1 text-sm text-muted-foreground">{selectedMember.description}</p>
                    </div>

                    <Tabs defaultValue="capabilities">
                      <TabsList>
                        <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
                        <TabsTrigger value="examples">Examples</TabsTrigger>
                      </TabsList>
                      <TabsContent value="capabilities" className="space-y-4 pt-4">
                        {selectedMember.id === "crew-1" && (
                          <>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Video className="h-4 w-4 text-detective-primary" />
                                <p className="text-sm font-medium">Video Enhancement</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Enhances low-quality footage to improve visibility and detail.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Video className="h-4 w-4 text-detective-primary" />
                                <p className="text-sm font-medium">Object Detection</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Identifies and tracks objects of interest in video feeds.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Video className="h-4 w-4 text-detective-primary" />
                                <p className="text-sm font-medium">Scene Analysis</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Analyzes scenes to identify relevant context and details.
                              </p>
                            </div>
                          </>
                        )}

                        {selectedMember.id === "crew-2" && (
                          <>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Timeline className="h-4 w-4 text-detective-secondary" />
                                <p className="text-sm font-medium">Event Sequencing</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Creates chronological sequences of events across multiple feeds.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Timeline className="h-4 w-4 text-detective-secondary" />
                                <p className="text-sm font-medium">Time Correlation</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Correlates timestamps across different camera systems.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Timeline className="h-4 w-4 text-detective-secondary" />
                                <p className="text-sm font-medium">Pattern Recognition</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Identifies patterns in suspect behavior and movement.
                              </p>
                            </div>
                          </>
                        )}

                        {selectedMember.id === "crew-3" && (
                          <>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Users className="h-4 w-4 text-detective-accent" />
                                <p className="text-sm font-medium">Facial Recognition</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Identifies individuals based on facial features.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Users className="h-4 w-4 text-detective-accent" />
                                <p className="text-sm font-medium">Gait Analysis</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Recognizes individuals by their walking pattern.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Users className="h-4 w-4 text-detective-accent" />
                                <p className="text-sm font-medium">Clothing Analysis</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Tracks individuals based on clothing characteristics.
                              </p>
                            </div>
                          </>
                        )}

                        {selectedMember.id === "crew-4" && (
                          <>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Network className="h-4 w-4 text-detective-primary" />
                                <p className="text-sm font-medium">Relationship Mapping</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Maps connections between people, places, and objects.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Network className="h-4 w-4 text-detective-primary" />
                                <p className="text-sm font-medium">Spatial Analysis</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Analyzes movement patterns and spatial relationships.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <Network className="h-4 w-4 text-detective-primary" />
                                <p className="text-sm font-medium">Visual Knowledge Graphs</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Creates interactive visualizations of complex relationships.
                              </p>
                            </div>
                          </>
                        )}

                        {selectedMember.id === "crew-5" && (
                          <>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <MessageSquare className="h-4 w-4 text-detective-secondary" />
                                <p className="text-sm font-medium">Natural Language Processing</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Understands and responds to natural language queries.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <MessageSquare className="h-4 w-4 text-detective-secondary" />
                                <p className="text-sm font-medium">Evidence Retrieval</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Retrieves relevant evidence based on queries.
                              </p>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <div className="flex items-center space-x-2">
                                <MessageSquare className="h-4 w-4 text-detective-secondary" />
                                <p className="text-sm font-medium">Multilingual Support</p>
                              </div>
                              <p className="mt-1 text-xs text-muted-foreground">
                                Provides responses in multiple languages.
                              </p>
                            </div>
                          </>
                        )}
                      </TabsContent>
                      <TabsContent value="examples" className="space-y-4 pt-4">
                        <div className="rounded-md bg-muted p-3">
                          <p className="text-sm">
                            "I've analyzed the footage from Camera 3 and enhanced the resolution in the northeast
                            corner. The suspect can be seen carrying what appears to be a black backpack."
                          </p>
                        </div>
                        <div className="rounded-md bg-muted p-3">
                          <p className="text-sm">
                            "Based on the timeline analysis, the suspect entered through the north entrance at 10:15 AM
                            and exited through the east door at 10:45 AM, spending approximately 8 minutes in the main
                            hall."
                          </p>
                        </div>
                        <div className="rounded-md bg-muted p-3">
                          <p className="text-sm">
                            "The knowledge graph shows that the suspect interacted with two individuals during their
                            time in the building, both near the cafeteria area."
                          </p>
                        </div>
                      </TabsContent>
                    </Tabs>
                  </div>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button className="w-full">Activate {selectedMember.name}</Button>
            </CardFooter>
          </Card>
        </div>
      </div>
    </div>
  )
}
