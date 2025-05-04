"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { FileVideo, Upload, X, Play, Info, User, FileImage, AlertCircle, CheckCircle2, Loader2 } from "lucide-react"
import { uploadVideo, uploadSuspect, runSuspectTracking, runGeneralAnalysis, generateEnhancedTimeline, detectSuspiciousBehavior, VideoFeed, Suspect } from "@/lib/api-service"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
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
  // Video states
  const [videos, setVideos] = useState<VideoFeed[]>([])
  const [uploading, setUploading] = useState(false)
  const [currentVideo, setCurrentVideo] = useState<VideoFeed | null>(null)
  const [uploadComplete, setUploadComplete] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    location: "",
    timestamp: new Date().toISOString().slice(0, 16),
  })
  
  // Suspect states
  const [suspect, setSuspect] = useState<Suspect | null>(null)
  const [suspectFile, setSuspectFile] = useState<File | null>(null)
  const [uploadingSuspect, setUploadingSuspect] = useState(false)
  const [suspectFormData, setSuspectFormData] = useState({
    name: "Person of Interest",
    description: "",
  })
  
  // Analysis states
  const [analysisStarted, setAnalysisStarted] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)
  const [analysisMode, setAnalysisMode] = useState<"suspect" | "general">("suspect")

  // State for selected files (before upload)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return
      
      // Just store the files, don't upload yet
      setSelectedFiles(acceptedFiles)
    },
    [],
  )
  
  // Function to handle the actual upload when user clicks the upload button
  const handleUpload = async () => {
    if (selectedFiles.length === 0) return
    
    setUploading(true)
    
    try {
      const newVideos = await Promise.all(
        selectedFiles.map(async (file) => {
          const video = await uploadVideo(file, {
            name: formData.name || file.name,
            location: formData.location,
            timestamp: formData.timestamp,
          })
          return video
        }),
      )
      
      setVideos((prev) => [...prev, ...newVideos])
      setUploadComplete(true)
      // Clear selected files after upload
      setSelectedFiles([])
    } catch (error) {
      console.error("Error uploading videos:", error)
    } finally {
      setUploading(false)
    }
  }
  
  // Function to prepare for uploading another video
  const prepareForNextUpload = () => {
    setUploadComplete(false)
    setSelectedFiles([])
    setFormData({
      name: "",
      location: "",
      timestamp: new Date().toISOString().slice(0, 16),
    })
  }
  
  // Suspect upload functions
  const onSuspectDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return
      setSuspectFile(acceptedFiles[0])
    },
    []
  )
  
  const { getRootProps: getSuspectRootProps, getInputProps: getSuspectInputProps, isDragActive: isSuspectDragActive } = useDropzone({
    onDrop: onSuspectDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png']
    },
    maxFiles: 1,
    multiple: false,
  })
  
  const handleSuspectUpload = async () => {
    if (!suspectFile) return
    
    setUploadingSuspect(true)
    
    try {
      const uploadedSuspect = await uploadSuspect(suspectFile, {
        name: suspectFormData.name,
        description: suspectFormData.description,
      })
      
      setSuspect(uploadedSuspect)
    } catch (error) {
      console.error("Error uploading suspect:", error)
    } finally {
      setUploadingSuspect(false)
    }
  }
  
  // Analysis functions
  const startAnalysis = async () => {
    // Validation based on analysis mode
    if (analysisMode === "suspect" && !suspect) {
      setAnalysisError("Please upload a suspect image before starting analysis")
      return
    }

    if (videos.length === 0) {
      setAnalysisError("Please upload at least one video before starting analysis")
      return
    }

    setAnalysisStarted(true)
    setAnalysisProgress(0)
    setAnalysisError(null)

    try {
      // Set up a progress simulation (in a real app, this would be from the backend)
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          const newProgress = prev + Math.random() * 10
          return newProgress >= 100 ? 100 : newProgress
        })
      }, 1000)

      // Run the actual analysis based on mode
      let result;

      if (analysisMode === "suspect") {
        console.log("Running suspect tracking analysis with:", {
          suspectId: suspect?.id,
          videoIds: videos.map(v => v.id)
        })
        // Suspect tracking analysis
        result = await runSuspectTracking({
          suspectId: suspect?.id || "", // Fix TypeScript error by providing empty string fallback
          videoIds: videos.map(v => v.id),
          options: {
            includeNarration: true,
            language: "en",
          },
        })

        // Generate enhanced timeline for better visualization
        if (result.id) {
          try {
            const timelineResult = await generateEnhancedTimeline({
              analysisId: result.id
            })
            console.log("Generated enhanced timeline:", timelineResult)
          } catch (timelineError) {
            console.error("Error generating enhanced timeline:", timelineError)
          }
        }
      } else {
        console.log("Running general video analysis with:", {
          videoIds: videos.map(v => v.id)
        })
        // General video analysis
        result = await runGeneralAnalysis({
          videoIds: videos.map(v => v.id),
          options: {
            detectSuspiciousActivity: true,
            includeNarration: true,
            language: "en",
          },
        })

        // Also run suspicious behavior detection
        try {
          const suspiciousResult = await detectSuspiciousBehavior({
            videoIds: videos.map(v => v.id)
          })
          console.log("Detected suspicious behavior:", suspiciousResult)
        } catch (suspiciousError) {
          console.error("Error detecting suspicious behavior:", suspiciousError)
        }
      }

      console.log("Analysis result:", result)
      clearInterval(progressInterval)
      setAnalysisProgress(100)
      setAnalysisComplete(true)
      setAnalysisId(result.id)
    } catch (error) {
      console.error("Error running analysis:", error)
      setAnalysisError("Failed to complete analysis. Please try again.")
      setAnalysisStarted(false)
    }
  }

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

  const [activeTab, setActiveTab] = useState("upload")

  // Function to handle tab change
  const handleTabChange = (value: string) => {
    setActiveTab(value)
    console.log("Tab changed to:", value)
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">Video Upload Dashboard</h1>

      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upload">Upload & Prepare</TabsTrigger>
          <TabsTrigger value="analyze">Suspect Tracking</TabsTrigger>
          <TabsTrigger value="general">General Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="upload">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Video Upload Section */}
            <Card>
              <CardHeader>
                <CardTitle>Upload Videos</CardTitle>
                <CardDescription>
                  Upload CCTV footage for analysis. Add metadata for better results.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="name">Video Name</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="Enter a descriptive name"
                      disabled={uploading}
                    />
                  </div>

                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) =>
                        setFormData({ ...formData, location: e.target.value })
                      }
                      placeholder="e.g., Main Entrance, Parking Lot"
                      disabled={uploading}
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="timestamp">Timestamp</Label>
                  <Input
                    id="timestamp"
                    type="datetime-local"
                    value={formData.timestamp}
                    onChange={(e) =>
                      setFormData({ ...formData, timestamp: e.target.value })
                    }
                    disabled={uploading}
                  />
                </div>

                <div
                  {...getRootProps()}
                  className={`mt-4 flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 p-6 text-center hover:bg-gray-50 ${isDragActive ? "bg-blue-50 border-blue-300" : ""} ${uploading || uploadComplete ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  <input {...getInputProps()} disabled={uploadComplete || uploading} />
                  <FileVideo className="mb-4 h-10 w-10 text-gray-400" />
                  <div className="space-y-1">
                    <p className="text-sm text-gray-600">
                      {uploadComplete 
                        ? "Upload complete. Add more videos." 
                        : selectedFiles.length > 0
                          ? `${selectedFiles.length} file(s) selected.`
                          : "Drag and drop video files here, or click to select files"}
                    </p>
                    <p className="text-xs text-gray-500">Supports MP4, AVI, MOV, MKV</p>
                  </div>
                </div>
                
                {/* Selected files preview */}
                {selectedFiles.length > 0 && !uploadComplete && (
                  <div className="mt-4 space-y-2">
                    <h3 className="text-sm font-medium">Selected Files:</h3>
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center justify-between rounded-md border p-2">
                        <div className="flex items-center">
                          <FileVideo className="mr-2 h-4 w-4 text-gray-400" />
                          <span className="text-sm">{file.name}</span>
                        </div>
                        <Badge variant="outline">{(file.size / (1024 * 1024)).toFixed(2)} MB</Badge>
                      </div>
                    ))}
                    
                    <div className="mt-4 flex justify-end space-x-2">
                      <Button 
                        variant="outline" 
                        onClick={() => setSelectedFiles([])}
                        disabled={uploading}
                        size="sm"
                      >
                        Clear
                      </Button>
                      <Button 
                        onClick={handleUpload}
                        disabled={uploading}
                        size="sm"
                      >
                        <Upload className="mr-2 h-4 w-4" /> Upload Video{selectedFiles.length > 1 ? 's' : ''}
                      </Button>
                    </div>
                  </div>
                )}

                {uploading && (
                  <div className="mt-4">
                    <Progress value={75} className="h-2" />
                    <p className="mt-1 text-xs text-center text-muted-foreground">Uploading...</p>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex justify-between">
                {uploadComplete && videos.length > 0 && (
                  <Button 
                    onClick={prepareForNextUpload}
                    variant="outline"
                    size="sm"
                  >
                    <Upload className="mr-2 h-4 w-4" /> Add More Videos
                  </Button>
                )}
              </CardFooter>
            </Card>

            {/* Suspect Upload Section */}
            <Card>
              <CardHeader>
                <CardTitle>Upload Suspect Image</CardTitle>
                <CardDescription>
                  Upload an image of the person to track across all videos.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label htmlFor="suspectName">Suspect Name/ID</Label>
                    <Input
                      id="suspectName"
                      value={suspectFormData.name}
                      onChange={(e) => setSuspectFormData({ ...suspectFormData, name: e.target.value })}
                      placeholder="Person of Interest"
                      disabled={uploadingSuspect || suspect !== null}
                    />
                  </div>

                  <div>
                    <Label htmlFor="suspectDescription">Description (Optional)</Label>
                    <Input
                      id="suspectDescription"
                      value={suspectFormData.description}
                      onChange={(e) =>
                        setSuspectFormData({ ...suspectFormData, description: e.target.value })
                      }
                      placeholder="Brief description of the person"
                      disabled={uploadingSuspect || suspect !== null}
                    />
                  </div>
                </div>

                {!suspect ? (
                  <div
                    {...getSuspectRootProps()}
                    className={`mt-4 flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 p-6 text-center hover:bg-gray-50 ${isSuspectDragActive ? "bg-blue-50 border-blue-300" : ""} ${uploadingSuspect ? "opacity-50 cursor-not-allowed" : ""}`}
                  >
                    <input {...getSuspectInputProps()} disabled={uploadingSuspect || suspect !== null} />
                    <User className="mb-4 h-10 w-10 text-gray-400" />
                    <div className="space-y-1">
                      <p className="text-sm text-gray-600">
                        {suspectFile 
                          ? `${suspectFile.name} selected` 
                          : "Drag and drop a suspect image, or click to select"}
                      </p>
                      <p className="text-xs text-gray-500">Supports JPG, PNG, JPEG</p>
                    </div>
                  </div>
                ) : (
                  <div className="mt-4 flex items-center justify-center">
                    <div className="flex flex-col items-center space-y-2">
                      <div className="relative h-32 w-32 overflow-hidden rounded-lg border">
                        <img 
                          src={suspect.imageUrl} 
                          alt={suspect.name} 
                          className="h-full w-full object-cover" 
                        />
                      </div>
                      <div className="text-center">
                        <p className="text-sm font-medium">{suspect.name}</p>
                        {suspect.description && (
                          <p className="text-xs text-muted-foreground">{suspect.description}</p>
                        )}
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setSuspect(null)}
                      >
                        <X className="mr-2 h-3 w-3" /> Remove
                      </Button>
                    </div>
                  </div>
                )}

                {suspectFile && !suspect && (
                  <div className="mt-4 flex justify-end">
                    <Button 
                      onClick={handleSuspectUpload}
                      disabled={uploadingSuspect}
                      size="sm"
                    >
                      <Upload className="mr-2 h-4 w-4" /> Upload Suspect Image
                    </Button>
                  </div>
                )}

                {uploadingSuspect && (
                  <div className="mt-4">
                    <Progress value={75} className="h-2" />
                    <p className="mt-1 text-xs text-center text-muted-foreground">Uploading suspect image...</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Status Summary Card */}
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Analysis Preparation Status</CardTitle>
                <CardDescription>
                  Ensure all requirements are met before proceeding to analysis.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        {videos.length > 0 ? (
                          <CheckCircle2 className="mr-2 h-5 w-5 text-green-500" />
                        ) : (
                          <AlertCircle className="mr-2 h-5 w-5 text-amber-500" />
                        )}
                        <span>Video Uploads</span>
                      </div>
                      <Badge variant={videos.length > 0 ? "secondary" : "outline"}>
                        {videos.length} videos
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        {suspect ? (
                          <CheckCircle2 className="mr-2 h-5 w-5 text-green-500" />
                        ) : (
                          <AlertCircle className="mr-2 h-5 w-5 text-amber-500" />
                        )}
                        <span>Suspect Image</span>
                      </div>
                      <Badge variant={suspect ? "secondary" : "outline"}>
                        {suspect ? "Uploaded" : "Required"}
                      </Badge>
                    </div>
                  </div>
                  
                  <div>
                    {videos.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-sm font-medium">Uploaded Videos:</h3>
                        <div className="max-h-32 overflow-y-auto space-y-1">
                          {videos.map((video) => (
                            <div key={video.id} className="flex items-center text-sm">
                              <FileVideo className="mr-2 h-3 w-3 text-muted-foreground" />
                              <span className="truncate">{video.name}</span>
                              <span className="ml-auto text-xs text-muted-foreground">{video.location}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button 
                  className="w-full" 
                  disabled={!suspect || videos.length === 0}
                  onClick={() => {
                    setActiveTab("analyze");
                  }}
                >
                  Proceed to Analysis
                </Button>
              </CardFooter>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="analyze">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Suspect Tracking Analysis</CardTitle>
                <CardDescription>
                  Track a specific suspect across all uploaded videos and generate a comprehensive timeline.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!analysisStarted ? (
                  <div className="space-y-6">
                    {/* Suspect Preview */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium">Suspect to Track</h3>
                      {suspect ? (
                        <div className="flex items-center space-x-4">
                          <div className="h-16 w-16 overflow-hidden rounded-lg border">
                            <img 
                              src={suspect.imageUrl} 
                              alt={suspect.name} 
                              className="h-full w-full object-cover" 
                            />
                          </div>
                          <div>
                            <p className="font-medium">{suspect.name}</p>
                            {suspect.description && (
                              <p className="text-xs text-muted-foreground">{suspect.description}</p>
                            )}
                          </div>
                        </div>
                      ) : (
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertTitle>No suspect uploaded</AlertTitle>
                          <AlertDescription>
                            Please upload a suspect image in the Upload & Prepare tab.
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                    
                    {/* Videos Preview */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium">Videos to Analyze</h3>
                      {videos.length > 0 ? (
                        <div className="max-h-32 overflow-y-auto space-y-2">
                          {videos.map((video) => (
                            <div key={video.id} className="flex items-center space-x-3 rounded-md border p-2">
                              <div className="h-10 w-10 overflow-hidden rounded bg-muted">
                                {video.thumbnailUrl ? (
                                  <img
                                    src={video.thumbnailUrl}
                                    alt={video.name}
                                    className="h-full w-full object-cover"
                                  />
                                ) : (
                                  <div className="flex h-full items-center justify-center">
                                    <FileVideo className="h-5 w-5 text-muted-foreground" />
                                  </div>
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium truncate">{video.name}</p>
                                <p className="text-xs text-muted-foreground truncate">{video.location}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertTitle>No videos uploaded</AlertTitle>
                          <AlertDescription>
                            Please upload at least one video in the Upload & Prepare tab.
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                    
                    {/* Analysis Options */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium">Analysis Options</h3>
                      <div className="grid gap-4 md:grid-cols-2">
                        <div>
                          <Label htmlFor="confidence">Confidence Threshold (%)</Label>
                          <Input
                            id="confidence"
                            type="number"
                            placeholder="75"
                            min="0"
                            max="100"
                            defaultValue="75"
                          />
                        </div>
                        <div>
                          <Label htmlFor="narration">Include Narration</Label>
                          <Select defaultValue="en">
                            <SelectTrigger id="narration">
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
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Analysis Progress */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium">Analysis Progress</h3>
                        <span className="text-sm font-medium">{Math.round(analysisProgress)}%</span>
                      </div>
                      <Progress value={analysisProgress} className="h-2" />
                      
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">
                          {analysisProgress < 25 && "Preparing videos for analysis..."}
                          {analysisProgress >= 25 && analysisProgress < 50 && "Detecting suspect in videos..."}
                          {analysisProgress >= 50 && analysisProgress < 75 && "Tracking suspect movements..."}
                          {analysisProgress >= 75 && analysisProgress < 100 && "Generating timeline and narrative..."}
                          {analysisProgress >= 100 && "Analysis complete!"}
                        </p>
                      </div>
                    </div>
                    
                    {/* Error Display */}
                    {analysisError && (
                      <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Analysis Failed</AlertTitle>
                        <AlertDescription>{analysisError}</AlertDescription>
                      </Alert>
                    )}
                  </div>
                )}
              </CardContent>
              <CardFooter>
                {!analysisStarted ? (
                  <Button 
                    className="w-full" 
                    disabled={!suspect || videos.length === 0}
                    onClick={() => {
                      setAnalysisMode("suspect");
                      startAnalysis();
                    }}
                  >
                    Start Suspect Tracking
                  </Button>
                ) : analysisComplete ? (
                  <Button 
                    className="w-full" 
                    onClick={() => {
                      window.location.href = `/timeline?analysis=${analysisId}`;
                    }}
                  >
                    View Timeline Results
                  </Button>
                ) : (
                  <Button className="w-full" disabled>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </Button>
                )}
              </CardFooter>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="general">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>General Video Analysis</CardTitle>
                <CardDescription>
                  Analyze videos for suspicious activities and generate a comprehensive narrative without tracking a specific suspect.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!analysisStarted ? (
                  <div className="space-y-6">                      
                    {/* Videos Preview */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium">Videos to Analyze</h3>
                      {videos.length > 0 ? (
                        <div className="max-h-48 overflow-y-auto space-y-2">
                          {videos.map((video) => (
                            <div key={video.id} className="flex items-center space-x-3 rounded-md border p-2">
                              <div className="h-10 w-10 overflow-hidden rounded bg-muted">
                                {video.thumbnailUrl ? (
                                  <img
                                    src={video.thumbnailUrl}
                                    alt={video.name}
                                    className="h-full w-full object-cover"
                                  />
                                ) : (
                                  <div className="flex h-full items-center justify-center">
                                    <FileVideo className="h-5 w-5 text-muted-foreground" />
                                  </div>
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium truncate">{video.name}</p>
                                <p className="text-xs text-muted-foreground truncate">{video.location}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertTitle>No videos uploaded</AlertTitle>
                          <AlertDescription>
                            Please upload at least one video in the Upload & Prepare tab.
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                    
                    {/* Analysis Options */}
                    <div className="space-y-3">
                      <h3 className="text-sm font-medium">Analysis Options</h3>
                      <div className="grid gap-4 md:grid-cols-2">
                        <div>
                          <Label htmlFor="suspicious-activity">Detect Suspicious Activity</Label>
                          <Select defaultValue="true">
                            <SelectTrigger id="suspicious-activity">
                              <SelectValue placeholder="Select option" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="true">Yes</SelectItem>
                              <SelectItem value="false">No</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="general-narration">Include Narration</Label>
                          <Select defaultValue="en">
                            <SelectTrigger id="general-narration">
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
                      </div>
                    </div>
                    
                    <div className="rounded-md border border-blue-100 bg-blue-50 p-4">
                      <div className="flex">
                        <Info className="h-5 w-5 text-blue-400" />
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-blue-800">About General Analysis</h3>
                          <div className="mt-2 text-sm text-blue-700">
                            <p>
                              General video analysis will process all uploaded videos to:
                            </p>
                            <ul className="list-disc pl-5 mt-2">
                              <li>Detect and track all persons in the videos</li>
                              <li>Identify suspicious activities or behaviors</li>
                              <li>Generate a comprehensive narrative of events</li>
                              <li>Highlight key moments with timestamps</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Analysis Progress */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium">Analysis Progress</h3>
                        <span className="text-sm font-medium">{Math.round(analysisProgress)}%</span>
                      </div>
                      <Progress value={analysisProgress} className="h-2" />
                      
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">
                          {analysisProgress < 25 && "Preparing videos for analysis..."}
                          {analysisProgress >= 25 && analysisProgress < 50 && "Detecting persons in videos..."}
                          {analysisProgress >= 50 && analysisProgress < 75 && "Identifying activities and behaviors..."}
                          {analysisProgress >= 75 && analysisProgress < 100 && "Generating narrative and highlights..."}
                          {analysisProgress >= 100 && "Analysis complete!"}
                        </p>
                      </div>
                    </div>
                    
                    {/* Error Display */}
                    {analysisError && (
                      <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Analysis Failed</AlertTitle>
                        <AlertDescription>{analysisError}</AlertDescription>
                      </Alert>
                    )}
                  </div>
                )}
              </CardContent>
              <CardFooter>
                {!analysisStarted ? (
                  <Button 
                    className="w-full" 
                    disabled={videos.length === 0}
                    onClick={() => {
                      setAnalysisMode("general");
                      startAnalysis();
                    }}
                  >
                    Start General Analysis
                  </Button>
                ) : analysisComplete ? (
                  <Button 
                    className="w-full" 
                    onClick={() => {
                      window.location.href = `/timeline?analysis=${analysisId}`;
                    }}
                  >
                    View Analysis Results
                  </Button>
                ) : (
                  <Button className="w-full" disabled>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </Button>
                )}
              </CardFooter>
            </Card>
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
