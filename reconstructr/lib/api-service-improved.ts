// Enhanced error handling for API calls

/**
 * Wrapper for fetch that adds better error handling
 */
export async function fetchWithErrorHandling(url: string, options: RequestInit, apiName: string) {
  try {
    console.log(`Calling ${apiName} API:`, url);
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API error (${response.status}) in ${apiName}:`, errorText);
      throw new Error(`Failed to call ${apiName}: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    console.log(`${apiName} API result:`, result);
    return result;
  } catch (error) {
    console.error(`Error in ${apiName}:`, error);
    throw error;
  }
}
