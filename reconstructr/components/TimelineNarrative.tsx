import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChevronDown, ChevronUp, Clock, MapPin, Activity, Users } from "lucide-react";

interface TimelineNarrativeProps {
  narrative: string;
  activitySummary: string;
  locations: string[];
  duration: number;
  firstSeen: string;
  lastSeen: string;
}

const TimelineNarrative: React.FC<TimelineNarrativeProps> = ({
  narrative,
  activitySummary,
  locations,
  duration,
  firstSeen,
  lastSeen
}) => {
  const [expanded, setExpanded] = useState(false);
  
  // Format the narrative with paragraphs
  const paragraphs = narrative.split('\n\n');
  
  // Format timestamps
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Investigative Narrative</CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {duration} minutes
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {locations.length} locations
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="narrative">
          <TabsList className="mb-4">
            <TabsTrigger value="narrative">Narrative</TabsTrigger>
            <TabsTrigger value="summary">Activity Summary</TabsTrigger>
            <TabsTrigger value="details">Timeline Details</TabsTrigger>
          </TabsList>
          
          <TabsContent value="narrative">
            <ScrollArea className="h-[calc(100vh-400px)] pr-4">
              <div className="space-y-4">
                {expanded ? (
                  // Show full narrative
                  paragraphs.map((paragraph, index) => (
                    <p key={index} className="text-sm leading-relaxed">
                      {paragraph}
                    </p>
                  ))
                ) : (
                  // Show condensed narrative (first paragraph and last paragraph)
                  <>
                    <p className="text-sm leading-relaxed">{paragraphs[0]}</p>
                    {paragraphs.length > 2 && (
                      <p className="text-xs text-muted-foreground italic">
                        [Narrative condensed. Click "Show Full Narrative" to see all details.]
                      </p>
                    )}
                    {paragraphs.length > 1 && (
                      <p className="text-sm leading-relaxed">{paragraphs[paragraphs.length - 1]}</p>
                    )}
                  </>
                )}
                
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={() => setExpanded(!expanded)}
                  className="mt-2 w-full"
                >
                  {expanded ? (
                    <>
                      <ChevronUp className="mr-1 h-4 w-4" />
                      Show Condensed Narrative
                    </>
                  ) : (
                    <>
                      <ChevronDown className="mr-1 h-4 w-4" />
                      Show Full Narrative
                    </>
                  )}
                </Button>
              </div>
            </ScrollArea>
          </TabsContent>
          
          <TabsContent value="summary">
            <div className="rounded-md bg-muted p-4">
              <h3 className="mb-2 flex items-center gap-2 text-sm font-medium">
                <Activity className="h-4 w-4" />
                Activity Summary
              </h3>
              <p className="text-sm text-muted-foreground">{activitySummary}</p>
              
              <h3 className="mb-2 mt-4 flex items-center gap-2 text-sm font-medium">
                <Clock className="h-4 w-4" />
                Time Range
              </h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="rounded-md bg-background p-2">
                  <p className="text-xs text-muted-foreground">First Seen</p>
                  <p className="font-medium">{formatTime(firstSeen)}</p>
                </div>
                <div className="rounded-md bg-background p-2">
                  <p className="text-xs text-muted-foreground">Last Seen</p>
                  <p className="font-medium">{formatTime(lastSeen)}</p>
                </div>
              </div>
              
              <h3 className="mb-2 mt-4 flex items-center gap-2 text-sm font-medium">
                <MapPin className="h-4 w-4" />
                Locations Visited
              </h3>
              <div className="flex flex-wrap gap-2">
                {locations.map((location) => (
                  <Badge key={location} variant="secondary">
                    {location}
                  </Badge>
                ))}
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="details">
            <div className="rounded-md bg-muted p-4">
              <h3 className="mb-2 flex items-center gap-2 text-sm font-medium">
                <Users className="h-4 w-4" />
                Investigation Details
              </h3>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium">Duration of Surveillance:</span>{" "}
                  {duration} minutes
                </p>
                <p>
                  <span className="font-medium">Suspect Movement Pattern:</span>{" "}
                  Tracked across {locations.length} different locations
                </p>
                <p>
                  <span className="font-medium">Surveillance Start:</span>{" "}
                  {new Date(firstSeen).toLocaleString()}
                </p>
                <p>
                  <span className="font-medium">Surveillance End:</span>{" "}
                  {new Date(lastSeen).toLocaleString()}
                </p>
                <p>
                  <span className="font-medium">Movement Path:</span>{" "}
                  {locations.join(" → ")}
                </p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default TimelineNarrative;
