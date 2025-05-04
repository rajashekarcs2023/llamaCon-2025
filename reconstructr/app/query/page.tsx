"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, Send, Volume2, VolumeX, Loader2 } from "lucide-react"
import type { Query } from "@/types"
import { queryAnalysis } from "@/lib/api-service"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default function QueryPanelPage() {
  const [queries, setQueries] = useState<Query[]>([])
  const [inputValue, setInputValue] = useState("")
  const [loading, setLoading] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!inputValue.trim() || loading) return

    setLoading(true)

    try {
      // Use a mock analysis ID for now
      const analysisId = "analysis-123";
      const queryText = inputValue;
      
      // Call queryAnalysis with the analysis ID and query text
      const response = await queryAnalysis(analysisId, { text: queryText });
      
      // Create a query object to match the expected structure
      const query: Query = {
        id: `query-${Date.now()}`,
        text: queryText,
        timestamp: new Date().toISOString(),
        response: {
          text: response,
          visualData: {
            type: "text",
            content: response
          }
        }
      };
      
      setQueries((prev) => [...prev, query]);
      setInputValue("");

      // Scroll to bottom
      setTimeout(() => {
        if (scrollAreaRef.current) {
          scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
        }
      }, 100)
    } catch (error) {
      console.error("Error submitting query:", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled)
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Query Panel</h1>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Query Chat */}
        <div className="md:col-span-2">
          <Card className="flex h-[600px] flex-col">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Investigation Assistant</CardTitle>
                <CardDescription>Ask questions about your investigation</CardDescription>
              </div>
              <Button variant="ghost" size="icon" onClick={toggleVoice}>
                {voiceEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
              </Button>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-0">
              <ScrollArea className="h-[calc(100%-80px)] px-6" ref={scrollAreaRef}>
                {queries.length === 0 ? (
                  <div className="flex h-full flex-col items-center justify-center">
                    <MessageSquare className="mb-4 h-10 w-10 text-muted-foreground" />
                    <p className="text-sm font-medium">No queries yet</p>
                    <p className="text-xs text-muted-foreground">Ask a question to get started</p>
                  </div>
                ) : (
                  <div className="space-y-4 py-4">
                    {queries.map((query) => (
                      <div key={query.id} className="space-y-4">
                        <div className="flex items-start space-x-3">
                          <Avatar>
                            <AvatarFallback className="bg-muted">U</AvatarFallback>
                            <AvatarImage src="/placeholder.svg?key=icf4r" />
                          </Avatar>
                          <div className="space-y-1">
                            <div className="flex items-center space-x-2">
                              <p className="text-sm font-medium">You</p>
                              <span className="text-xs text-muted-foreground">{formatTime(query.timestamp)}</span>
                            </div>
                            <div className="rounded-md bg-muted p-3">
                              <p className="text-sm">{query.text}</p>
                            </div>
                          </div>
                        </div>

                        {query.response && (
                          <div className="flex items-start space-x-3">
                            <Avatar>
                              <AvatarFallback className="bg-detective-primary text-white">AI</AvatarFallback>
                              <AvatarImage src="/placeholder.svg?height=40&width=40&query=AI%20assistant" />
                            </Avatar>
                            <div className="space-y-1">
                              <div className="flex items-center space-x-2">
                                <p className="text-sm font-medium">AI Assistant</p>
                                <span className="text-xs text-muted-foreground">{formatTime(query.timestamp)}</span>
                              </div>
                              <div className="space-y-3">
                                <div className="rounded-md bg-detective-primary/10 p-3">
                                  <p className="text-sm">{query.response.text}</p>
                                </div>

                                {query.response.visualData && (
                                  <div className="overflow-hidden rounded-md">
                                    <img
                                      src={query.response.visualData.url || "/placeholder.svg"}
                                      alt="Visual response"
                                      className="h-48 w-full object-cover"
                                    />
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        <Separator />
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>

              <div className="border-t p-4">
                <form onSubmit={handleSubmit} className="flex space-x-2">
                  <Input
                    placeholder="Ask a question about your investigation..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    disabled={loading}
                    className="flex-1"
                  />
                  <Button type="submit" disabled={loading || !inputValue.trim()}>
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                    <span className="ml-2 sr-only md:not-sr-only">Send</span>
                  </Button>
                </form>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Suggested Queries */}
        <div>
          <Card className="h-[600px]">
            <CardHeader>
              <CardTitle>Suggested Queries</CardTitle>
              <CardDescription>Common questions to ask about your investigation</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[calc(100%-80px)]">
                <div className="space-y-4">
                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("Where was the suspect last seen?")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        Location
                      </Badge>
                      <p className="text-sm font-medium">Where was the suspect last seen?</p>
                    </div>
                  </div>

                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("What objects was the suspect carrying?")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        Objects
                      </Badge>
                      <p className="text-sm font-medium">What objects was the suspect carrying?</p>
                    </div>
                  </div>

                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("Who did the suspect interact with?")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        People
                      </Badge>
                      <p className="text-sm font-medium">Who did the suspect interact with?</p>
                    </div>
                  </div>

                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("What was the suspect's path through the building?")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        Path
                      </Badge>
                      <p className="text-sm font-medium">What was the suspect's path through the building?</p>
                    </div>
                  </div>

                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("What time did the suspect enter the building?")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        Time
                      </Badge>
                      <p className="text-sm font-medium">What time did the suspect enter the building?</p>
                    </div>
                  </div>

                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("Summarize all suspect activities in chronological order")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        Summary
                      </Badge>
                      <p className="text-sm font-medium">Summarize all suspect activities</p>
                    </div>
                  </div>

                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("What is the confidence level of the suspect identification?")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        Confidence
                      </Badge>
                      <p className="text-sm font-medium">What is the confidence level of the identification?</p>
                    </div>
                  </div>

                  <div
                    className="cursor-pointer rounded-md border p-3 transition-colors hover:bg-muted/50"
                    onClick={() => {
                      setInputValue("Show me all cameras where the suspect appeared")
                    }}
                  >
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="bg-detective-primary/10">
                        Cameras
                      </Badge>
                      <p className="text-sm font-medium">Show me all cameras where the suspect appeared</p>
                    </div>
                  </div>
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
