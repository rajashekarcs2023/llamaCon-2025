"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Separator } from "@/components/ui/separator"
import { Checkbox } from "@/components/ui/checkbox"
import { User, Upload, ArrowRight } from "lucide-react"
import type { Suspect, VideoFeed, AnalysisRequest, AnalysisResult } from "@/types"
import { uploadSuspect, runSuspectTracking } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { useRouter } from "next/navigation"

// Mock video data for demonstration
const mockVideos: VideoFeed[] = [
  {
    id: "video-1",
    name: "North Entrance CCTV",
    location: "Main Building, Floor 1",
    timestamp: new Date().toISOString(),
    duration: 120,
    fileUrl: "#",
    thumbnailUrl: "/placeholder.svg?key=gqu8k",
    size: 1024 * 1024 * 15,
    processed: true,
  },
  {
    id: "video-2",
    name: "Main Hall Camera",
    location: "Main Building, Floor 1",
    timestamp: new Date().toISOString(),
    duration: 180,
    fileUrl: "#",
    thumbnailUrl: "/placeholder.svg?key=o85uy",
    size: 1024 * 1024 * 20,
    processed: true,
  },
  {
    id: "video-3",
    name: "East Exit Camera",
    location: "Main Building, Floor 1",
    timestamp: new Date().toISOString(),
    duration: 150,
    fileUrl: "#",
    thumbnailUrl: "/placeholder.svg?key=1ovk9",
    size: 1024 * 1024 * 18,
    processed: true,
  },
  {
    id: "video-4",
    name: "Parking Lot Camera",
    location: "Exterior",
    timestamp: new Date().toISOString(),
    duration: 200,
    fileUrl: "#",
    thumbnailUrl: "/placeholder.svg?key=coibw",
    size: 1024 * 1024 * 25,
    processed: true,
  },
]

export default function SuspectIdentificationPage() {
  const router = useRouter()
  const [suspect, setSuspect] = useState<Suspect | null>(null)
  const [uploading, setUploading] = useState(false)
  const [selectedVideos, setSelectedVideos] = useState<string[]>([])
  const [includeNarration, setIncludeNarration] = useState(true)
  const [language, setLanguage] = useState("en")
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
  })

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return

      setUploading(true)

      try {
        const file = acceptedFiles[0] // Only use the first file
        const uploadedSuspect = await uploadSuspect(file, {
          name: formData.name,
          description: formData.description,
        })

        setSuspect(uploadedSuspect)
      } catch (error) {
        console.error("Error uploading suspect image:", error)
      } finally {
        setUploading(false)
      }
    },
    [formData],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png"],
    },
    maxFiles: 1,
    disabled: uploading || !!suspect,
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleVideoToggle = (videoId: string) => {
    setSelectedVideos((prev) => (prev.includes(videoId) ? prev.filter((id) => id !== videoId) : [...prev, videoId]))
  }

  const handleRunAnalysis = async () => {
    if (!suspect || selectedVideos.length === 0) return

    setAnalyzing(true)

    try {
      const request: AnalysisRequest = {
        suspectId: suspect.id,
        videoIds: selectedVideos,
        options: {
          includeNarration,
          language,
        },
      }

      const result = await runSuspectTracking(request)
      setAnalysisResult(result)

      // Navigate to timeline page with the analysis result
      router.push(`/timeline?analysis=${result.id}`)
    } catch (error) {
      console.error("Error running analysis:", error)
    } finally {
      setAnalyzing(false)
    }
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Suspect Identification</h1>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Suspect Information</CardTitle>
          </CardHeader>
          <CardContent>
            {suspect ? (
              <div className="space-y-4">
                <div className="overflow-hidden rounded-md">
                  <img
                    src={suspect.imageUrl || "/placeholder.svg"}
                    alt="Suspect"
                    className="h-64 w-full object-cover"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Name</Label>
                  <p className="text-sm">{suspect.name || "Unknown"}</p>
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <p className="text-sm">{suspect.description || "No description provided"}</p>
                </div>
                <Button variant="outline" onClick={() => setSuspect(null)} className="w-full">
                  Clear and Upload Different Image
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div
                  {...getRootProps()}
                  className={`flex h-64 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors ${
                    isDragActive ? "border-primary bg-primary/10" : "border-muted"
                  }`}
                >
                  <input {...getInputProps()} />
                  <User className="mb-4 h-10 w-10 text-muted-foreground" />
                  {uploading ? (
                    <div className="text-center">
                      <p className="mb-2 text-sm font-medium">Uploading...</p>
                      <Skeleton className="h-2 w-48" />
                    </div>
                  ) : (
                    <>
                      <p className="mb-1 text-sm font-medium">
                        {isDragActive ? "Drop the image here" : "Drag & drop suspect image here"}
                      </p>
                      <p className="text-xs text-muted-foreground">or click to select an image</p>
                      <Button variant="outline" size="sm" className="mt-4" disabled={uploading}>
                        <Upload className="mr-2 h-4 w-4" />
                        Select Image
                      </Button>
                    </>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="name">Name (if known)</Label>
                  <Input
                    id="name"
                    name="name"
                    placeholder="e.g., John Doe"
                    value={formData.name}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    name="description"
                    placeholder="e.g., Male, approximately 6ft tall, wearing a dark jacket"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={3}
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Select Video Feeds</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Select the video feeds you want to analyze for the suspect
              </p>

              <div className="max-h-[400px] space-y-2 overflow-y-auto pr-2">
                {mockVideos.map((video) => (
                  <div key={video.id} className="flex items-center space-x-3 rounded-md border p-3">
                    <Checkbox
                      id={video.id}
                      checked={selectedVideos.includes(video.id)}
                      onCheckedChange={() => handleVideoToggle(video.id)}
                    />
                    <div className="h-16 w-24 overflow-hidden rounded">
                      <img
                        src={video.thumbnailUrl || "/placeholder.svg"}
                        alt={video.name}
                        className="h-full w-full object-cover"
                      />
                    </div>
                    <div className="flex-1">
                      <Label htmlFor={video.id} className="cursor-pointer font-medium">
                        {video.name}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {video.location} - {new Date(video.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <Separator className="my-4" />

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="narration">Voice Narration</Label>
                    <p className="text-xs text-muted-foreground">Generate audio narration of findings</p>
                  </div>
                  <Switch id="narration" checked={includeNarration} onCheckedChange={setIncludeNarration} />
                </div>

                {includeNarration && (
                  <div className="space-y-2">
                    <Label htmlFor="language">Narration Language</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger id="language">
                        <SelectValue placeholder="Select language" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="de">German</SelectItem>
                        <SelectItem value="zh">Chinese</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>

              <Button
                className="w-full"
                disabled={!suspect || selectedVideos.length === 0 || analyzing}
                onClick={handleRunAnalysis}
              >
                {analyzing ? (
                  <>Analyzing...</>
                ) : (
                  <>
                    Run Analysis <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
