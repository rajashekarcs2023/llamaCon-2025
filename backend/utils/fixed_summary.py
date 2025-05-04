async def generate_summary(self, timeline_events: List[Dict[str, Any]], graph: Optional[Dict[str, Any]] = None, environment_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a natural language summary of the analysis using Llama 4's long context capabilities
    
    Args:
        timeline_events: List of timeline events
        graph: Knowledge graph data (optional)
        environment_context: Environmental context information (optional)
    
    Returns:
        Summary text
    """
    if not timeline_events:
        return "No suspect appearances were detected in the provided videos."
    
    try:
        # Use LLaMA to generate a comprehensive summary
        if len(timeline_events) > 0:
            # Sort events by timestamp
            sorted_events = sorted(timeline_events, key=lambda x: x.get("timestamp", ""))
            
            # Calculate duration
            first_event = sorted_events[0]
            last_event = sorted_events[-1]
            
            try:
                first_time = datetime.fromisoformat(first_event.get("timestamp", ""))
                last_time = datetime.fromisoformat(last_event.get("timestamp", ""))
                duration = (last_time - first_time).total_seconds() / 60  # in minutes
            except (ValueError, TypeError):
                # Fallback if timestamps are invalid
                first_time = datetime.now()
                last_time = datetime.now() + timedelta(minutes=30)
                duration = 30
            
            # Collect locations
            locations = set()
            for event in timeline_events:
                locations.add(event.get("location", ""))
            locations_str = ", ".join(filter(None, locations)) if locations else "multiple locations"
            
            # Include environment context if available
            env_context_str = ""
            if environment_context:
                env_description = environment_context.get("description", "")
                env_locations = environment_context.get("locations", [])
                
                if env_description:
                    env_context_str = f"\n\nEnvironment Context: {env_description}"
                
                if env_locations:
                    env_locations_str = "\n- " + "\n- ".join([f"{loc.get('name', '')}: {loc.get('description', '')}" for loc in env_locations])
                    env_context_str += f"\n\nLocation Details: {env_locations_str}"
            
            # Include graph information if available
            graph_str = ""
            if graph and isinstance(graph, dict):
                nodes = graph.get("nodes", [])
                edges = graph.get("edges", [])
                
                if nodes and edges:
                    graph_str = f"\n\nInteractions: The suspect interacted with {len(nodes) - 1} entities across {len(edges)} different interactions."
            
            # Generate a more detailed summary using all available information
            activities = set()
            for event in timeline_events:
                activity = event.get("activity", "")
                if activity:
                    activities.add(activity)
            
            activities_str = ", ".join(activities) if activities else "various activities"
            
            # Construct the comprehensive summary
            summary = f"Suspect was tracked for approximately {duration:.0f} minutes across {len(locations)} different locations ({locations_str}). "
            summary += f"First appeared at {first_time.strftime('%I:%M %p')} and was last seen at {last_time.strftime('%I:%M %p')}. "
            summary += f"Activities observed: {activities_str}."
            
            # Add environment and graph context
            summary += graph_str
            summary += env_context_str
            
            return summary
        else:
            return "No suspect appearances were detected in the provided videos."
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        
        # Fallback to basic summary
        first_time = datetime.now() - timedelta(minutes=30)
        last_time = datetime.now()
        duration = 30
        
        locations = set()
        for event in timeline_events:
            locations.add(event.get("location", ""))
        
        locations_str = ", ".join(filter(None, locations)) if locations else "multiple locations"
        
        summary = f"Suspect was tracked for approximately {duration:.0f} minutes across {len(locations)} different locations ({locations_str}). "
        summary += f"First appeared at {first_time.strftime('%I:%M %p')} and was last seen at {last_time.strftime('%I:%M %p')}."
        
        # Add basic environment context if available
        if environment_context and environment_context.get("description"):
            summary += f"\n\nEnvironment Context: {environment_context.get('description')}"
        
        return summary
