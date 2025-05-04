"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileVideo, Upload, X, Play, Info } from "lucide-react"
import type { VideoFeed } from "@/types"
import { uploadVideo } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

export default function VideoUploadPage() {
  const [videos, setVideos] = useState<VideoFeed[]>([])
  const [uploading, setUploading] = useState(false)
  const [currentVideo, setCurrentVideo] = useState<VideoFeed | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    location: "",
    timestamp: new Date().toISOString().slice(0, 16),
  })

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return

      setUploading(true)

      try {
        const newVideos = await Promise.all(
          acceptedFiles.map(async (file) => {
            const video = await uploadVideo(file, {
              name: formData.name || file.name,
              location: formData.location,
              timestamp: formData.timestamp,
            })
            return video
          }),
        )

        setVideos((prev) => [...prev, ...newVideos])
      } catch (error) {
        console.error("Error uploading videos:", error)
      } finally {
        setUploading(false)
        // Reset form after upload
        setFormData({
          name: "",
          location: "",
          timestamp: new Date().toISOString().slice(0, 16),
        })
      }
    },
    [formData],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".avi", ".mov", ".mkv"],
    },
    disabled: uploading,
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Video Upload Dashboard</h1>

      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="upload">Upload Videos</TabsTrigger>
          <TabsTrigger value="manage">Manage Videos ({videos.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="upload">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Camera Name</Label>
                    <Input
                      id="name"
                      name="name"
                      placeholder="e.g., North Entrance CCTV"
                      value={formData.name}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      name="location"
                      placeholder="e.g., Main Building, Floor 1"
                      value={formData.location}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timestamp">Timestamp</Label>
                    <Input
                      id="timestamp"
                      name="timestamp"
                      type="datetime-local"
                      value={formData.timestamp}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <div
              {...getRootProps()}
              className={`flex h-[250px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors ${
                isDragActive ? "border-primary bg-primary/10" : "border-muted"
              }`}
            >
              <input {...getInputProps()} />
              <FileVideo className="mb-4 h-10 w-10 text-muted-foreground" />
              {uploading ? (
                <div className="text-center">
                  <p className="mb-2 text-sm font-medium">Uploading...</p>
                  <Skeleton className="h-2 w-48" />
                </div>
              ) : (
                <>
                  <p className="mb-1 text-sm font-medium">
                    {isDragActive ? "Drop the files here" : "Drag & drop video files here"}
                  </p>
                  <p className="text-xs text-muted-foreground">or click to select files</p>
                  <Button variant="outline" size="sm" className="mt-4" disabled={uploading}>
                    <Upload className="mr-2 h-4 w-4" />
                    Select Files
                  </Button>
                </>
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="manage">
          {videos.length === 0 ? (
            <div className="flex h-[300px] flex-col items-center justify-center rounded-lg border border-dashed">
              <FileVideo className="mb-4 h-10 w-10 text-muted-foreground" />
              <p className="text-sm font-medium">No videos uploaded yet</p>
              <p className="text-xs text-muted-foreground">Upload videos to start your investigation</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {videos.map((video) => (
                <Card key={video.id} className="overflow-hidden">
                  <div className="relative aspect-video">
                    <img
                      src={video.thumbnailUrl || "/placeholder.svg"}
                      alt={video.name}
                      className="h-full w-full object-cover"
                    />
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity hover:opacity-100">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-white"
                              onClick={() => setCurrentVideo(video)}
                            >
                              <Play className="h-8 w-8" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Play Video</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    <Badge variant="secondary" className="absolute right-2 top-2">
                      {formatDuration(video.duration)}
                    </Badge>
                  </div>
                  <CardContent className="p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <h3 className="font-medium">{video.name}</h3>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <Info className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Video Details</DialogTitle>
                            <DialogDescription>Information about the video feed</DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <h4 className="text-sm font-medium">Name</h4>
                              <p className="text-sm text-muted-foreground">{video.name}</p>
                            </div>
                            <Separator />
                            <div>
                              <h4 className="text-sm font-medium">Location</h4>
                              <p className="text-sm text-muted-foreground">{video.location}</p>
                            </div>
                            <Separator />
                            <div>
                              <h4 className="text-sm font-medium">Timestamp</h4>
                              <p className="text-sm text-muted-foreground">
                                {new Date(video.timestamp).toLocaleString()}
                              </p>
                            </div>
                            <Separator />
                            <div>
                              <h4 className="text-sm font-medium">File Size</h4>
                              <p className="text-sm text-muted-foreground">{formatFileSize(video.size)}</p>
                            </div>
                            <Separator />
                            <div>
                              <h4 className="text-sm font-medium">Duration</h4>
                              <p className="text-sm text-muted-foreground">{formatDuration(video.duration)}</p>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                    <div className="flex flex-col space-y-1 text-xs text-muted-foreground">
                      <p>{video.location}</p>
                      <p>{new Date(video.timestamp).toLocaleString()}</p>
                      <p>{formatFileSize(video.size)}</p>
                    </div>
                    <div className="mt-4 flex justify-between">
                      <Badge
                        variant={video.processed ? "default" : "outline"}
                        className={video.processed ? "bg-green-600" : ""}
                      >
                        {video.processed ? "Processed" : "Pending"}
                      </Badge>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => {
                          setVideos((prev) => prev.filter((v) => v.id !== video.id))
                        }}
                      >
                        <X className="mr-1 h-3 w-3" /> Remove
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Video Preview Dialog */}
      {currentVideo && (
        <Dialog
          open={!!currentVideo}
          onOpenChange={(open) => {
            if (!open) setCurrentVideo(null)
          }}
        >
          <DialogContent className="sm:max-w-[800px]">
            <DialogHeader>
              <DialogTitle>{currentVideo.name}</DialogTitle>
              <DialogDescription>
                {currentVideo.location} - {new Date(currentVideo.timestamp).toLocaleString()}
              </DialogDescription>
            </DialogHeader>
            <div className="aspect-video overflow-hidden rounded-md">
              <video src={currentVideo.fileUrl} controls className="h-full w-full" />
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}
