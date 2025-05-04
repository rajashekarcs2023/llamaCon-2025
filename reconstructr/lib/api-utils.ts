// API utilities for better error handling

/**
 * Enhanced fetch function with better error handling
 * @param url API endpoint URL
 * @param options Fetch options
 * @param apiName Name of the API for logging
 * @returns Promise with the API response
 */
export async function fetchWithErrorHandling<T>(url: string, options: RequestInit, apiName: string): Promise<T> {
  try {
    console.log(`Calling ${apiName} API:`, url);
    const response = await fetch(url, options);

    if (!response.ok) {
      let errorText: string;
      try {
        const errorData = await response.json();
        errorText = JSON.stringify(errorData);
      } catch {
        errorText = await response.text();
      }
      
      console.error(`API error (${response.status}) in ${apiName}:`, errorText);
      throw new Error(`Failed to call ${apiName}: ${response.status} - ${errorText}`);
    }

    const result = await response.json() as T;
    console.log(`${apiName} API result:`, result);
    return result;
  } catch (error) {
    console.error(`Error in ${apiName}:`, error);
    throw error;
  }
}
