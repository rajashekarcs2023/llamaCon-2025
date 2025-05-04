import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Clock, MapPin, Video, ArrowRight, Filter } from "lucide-react";

interface TimelineEvent {
  id: string;
  time: string;
  location: string;
  activity: string;
  thumbnailUrl: string;
  confidence: number;
  isLocationChange: boolean;
  description: string;
}

interface VisualTimelineProps {
  events: TimelineEvent[];
  locations: string[];
  onEventSelect: (eventId: string) => void;
  selectedEventId?: string;
}

const VisualTimeline: React.FC<VisualTimelineProps> = ({
  events,
  locations,
  onEventSelect,
  selectedEventId
}) => {
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null);
  const [view, setView] = useState<'timeline' | 'locations'>('timeline');
  
  // Filter events by location if selected
  const filteredEvents = selectedLocation 
    ? events.filter(event => event.location === selectedLocation)
    : events;
  
  // Group events by location
  const eventsByLocation = events.reduce((acc, event) => {
    if (!acc[event.location]) {
      acc[event.location] = [];
    }
    acc[event.location].push(event);
    return acc;
  }, {} as Record<string, TimelineEvent[]>);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Visual Timeline</CardTitle>
          <Tabs value={view} onValueChange={(v) => setView(v as 'timeline' | 'locations')}>
            <TabsList>
              <TabsTrigger value="timeline">Chronological</TabsTrigger>
              <TabsTrigger value="locations">By Location</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        
        {view === 'timeline' && (
          <div className="mt-2 flex flex-wrap gap-2">
            <Button 
              variant={selectedLocation === null ? "default" : "outline"} 
              size="sm"
              onClick={() => setSelectedLocation(null)}
              className="flex items-center gap-1"
            >
              <Filter className="h-3 w-3" />
              All Locations
            </Button>
            {locations.map(location => (
              <Button
                key={location}
                variant={selectedLocation === location ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedLocation(location)}
                className="flex items-center gap-1"
              >
                <MapPin className="h-3 w-3" />
                {location}
              </Button>
            ))}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[calc(100vh-300px)] pr-4">
          {view === 'timeline' ? (
            <div className="relative space-y-4 pl-6">
              {/* Timeline line */}
              <div className="absolute inset-y-0 left-2 w-px bg-muted" />
              
              {filteredEvents.map((event, index) => (
                <div
                  key={event.id}
                  className={`relative cursor-pointer rounded-md border p-3 transition-colors ${
                    selectedEventId === event.id ? "border-primary bg-primary/10" : "hover:bg-muted/50"
                  }`}
                  onClick={() => onEventSelect(event.id)}
                >
                  {/* Timeline dot */}
                  <div
                    className={`absolute -left-6 top-1/2 h-4 w-4 -translate-y-1/2 rounded-full border-2 ${
                      selectedEventId === event.id
                        ? "border-primary bg-background"
                        : "border-muted-foreground bg-background"
                    }`}
                  />
                  
                  {/* Location change indicator */}
                  {event.isLocationChange && (
                    <Badge 
                      variant="secondary" 
                      className="absolute -left-24 top-1/2 -translate-y-1/2"
                    >
                      Location Change
                    </Badge>
                  )}
                  
                  <div className="flex gap-3">
                    <div className="h-16 w-24 flex-shrink-0 overflow-hidden rounded">
                      <img
                        src={event.thumbnailUrl || "/placeholder.svg"}
                        alt={`Event at ${event.time}`}
                        className="h-full w-full object-cover"
                      />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium">{event.time}</p>
                        <Badge variant="outline" className="text-xs">
                          {event.confidence}%
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{event.location}</p>
                      <p className="text-xs">{event.activity}</p>
                      <div className="mt-1 flex items-center gap-1">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-6 px-2 text-xs"
                          onClick={(e) => {
                            e.stopPropagation();
                            onEventSelect(event.id);
                          }}
                        >
                          <Video className="mr-1 h-3 w-3" />
                          View Video
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-6">
              {Object.entries(eventsByLocation).map(([location, locationEvents]) => (
                <div key={location} className="rounded-md border p-3">
                  <h3 className="mb-2 flex items-center gap-2 text-sm font-medium">
                    <MapPin className="h-4 w-4" />
                    {location}
                    <Badge variant="outline" className="ml-2">
                      {locationEvents.length} events
                    </Badge>
                  </h3>
                  
                  <div className="relative ml-4 space-y-3 pl-6">
                    {/* Timeline line */}
                    <div className="absolute inset-y-0 left-2 w-px bg-muted" />
                    
                    {locationEvents.map((event, index) => (
                      <div
                        key={event.id}
                        className={`relative cursor-pointer rounded-md border p-2 transition-colors ${
                          selectedEventId === event.id ? "border-primary bg-primary/10" : "hover:bg-muted/50"
                        }`}
                        onClick={() => onEventSelect(event.id)}
                      >
                        {/* Timeline dot */}
                        <div
                          className={`absolute -left-6 top-1/2 h-3 w-3 -translate-y-1/2 rounded-full border ${
                            selectedEventId === event.id
                              ? "border-primary bg-primary"
                              : "border-muted-foreground bg-muted"
                          }`}
                        />
                        
                        <div className="flex items-center gap-2">
                          <div className="h-12 w-16 flex-shrink-0 overflow-hidden rounded">
                            <img
                              src={event.thumbnailUrl || "/placeholder.svg"}
                              alt={`Event at ${event.time}`}
                              className="h-full w-full object-cover"
                            />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <p className="text-xs font-medium">{event.time}</p>
                              <Badge variant="outline" className="text-xs">
                                {event.confidence}%
                              </Badge>
                            </div>
                            <p className="text-xs">{event.activity}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* Show next location if not the last one */}
                  {Object.keys(eventsByLocation).indexOf(location) < Object.keys(eventsByLocation).length - 1 && (
                    <div className="mt-3 flex items-center justify-center">
                      <ArrowRight className="h-5 w-5 text-muted-foreground" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default VisualTimeline;
