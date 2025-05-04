import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileVideo, User, TimerIcon as Timeline, Network, MessageSquare, ArrowRight } from "lucide-react"
import Link from "next/link"

export default function Dashboard() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Investigation Dashboard</h1>
        <p className="text-muted-foreground">Track suspects across multiple CCTV feeds using AI</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Video Upload</CardTitle>
            <FileVideo className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Upload CCTV Footage</div>
            <p className="text-xs text-muted-foreground">Upload and manage your video feeds</p>
            <Button asChild className="mt-4 w-full">
              <Link href="/videos">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Suspect Identification</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Track Suspects</div>
            <p className="text-xs text-muted-foreground">Upload suspect images and run analysis</p>
            <Button asChild className="mt-4 w-full">
              <Link href="/suspect">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Timeline View</CardTitle>
            <Timeline className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Analyze Timeline</div>
            <p className="text-xs text-muted-foreground">View suspect movements across time</p>
            <Button asChild className="mt-4 w-full">
              <Link href="/timeline">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Graph View</CardTitle>
            <Network className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Knowledge Graph</div>
            <p className="text-xs text-muted-foreground">Visualize connections and movements</p>
            <Button asChild className="mt-4 w-full">
              <Link href="/graph">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Query Panel</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Ask Questions</div>
            <p className="text-xs text-muted-foreground">Get natural language answers about your case</p>
            <Button asChild className="mt-4 w-full">
              <Link href="/query">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-detective-primary to-detective-secondary text-white">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">New Investigation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Start Fresh</div>
            <p className="text-xs opacity-90">Begin a new investigation with ReConstructR</p>
            <Button variant="secondary" asChild className="mt-4 w-full">
              <Link href="/videos">
                New Case <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest investigation activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="mr-4 rounded-full bg-muted p-2">
                  <FileVideo className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-medium">Video Uploaded</p>
                  <p className="text-xs text-muted-foreground">North Entrance CCTV - 2 hours ago</p>
                </div>
              </div>
              <div className="flex items-center">
                <div className="mr-4 rounded-full bg-muted p-2">
                  <User className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-medium">Suspect Identified</p>
                  <p className="text-xs text-muted-foreground">Suspect #1024 - 3 hours ago</p>
                </div>
              </div>
              <div className="flex items-center">
                <div className="mr-4 rounded-full bg-muted p-2">
                  <Timeline className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-medium">Timeline Generated</p>
                  <p className="text-xs text-muted-foreground">Case #4872 - 5 hours ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
