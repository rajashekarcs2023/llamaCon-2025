/**
 * API Helper functions for better error handling and logging
 */

/**
 * Enhanced fetch function with better error handling
 */
export async function fetchWithErrorHandling<T>(url: string, options: RequestInit): Promise<T> {
  try {
    console.log(`API call to: ${url}`, options.body ? JSON.parse(options.body as string) : {});
    
    const response = await fetch(url, options);
    
    // Try to parse the response as JSON
    let data;
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      const text = await response.text();
      console.error(`Non-JSON response: ${text}`);
      throw new Error(`Unexpected response format: ${text}`);
    }
    
    // Check if the response contains an error message
    if (data && data.error) {
      console.error("API returned error:", data.error);
      throw new Error(data.error);
    }
    
    // If the response is not OK and we don't have an error message in the data
    if (!response.ok && !data.error) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    console.log("API response:", data);
    return data as T;
  } catch (error) {
    console.error("API call failed:", error);
    throw error;
  }
}
