from mcp.server.fastmcp import FastMCP
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import sys
from http import HTTPStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Star Wars Information Server")

# API configuration
BASE_URL = "https://www.swapi.tech/api"
HEADERS = {
    "Content-Type": "application/json"
}

# Resource types configuration
RESOURCE_TYPES = {
    "people": "characters",
    "films": "movies",
    "starships": "starships",
    "vehicles": "vehicles",
    "species": "species",
    "planets": "planets"
}

class StarWarsAPIError(Exception):
    """Custom exception for Star Wars API errors"""
    def __init__(self, message: str, resource_type: str, status_code: Optional[int] = None):
        self.message = message
        self.resource_type = resource_type
        self.status_code = status_code
        super().__init__(self.message)

async def fetch_resource(resource_type: str, resource_id: Optional[str] = None, search_query: Optional[str] = None) -> Dict[str, Any]:
    """
    Helper function to fetch Star Wars data from the API
    
    Args:
        resource_type: Type of resource (people, films, starships, etc.)
        resource_id: Optional ID of specific resource to fetch
        search_query: Optional search query to find resources
        
    Returns:
        Dict containing Star Wars data or error information
    """
    if resource_type not in RESOURCE_TYPES:
        logger.error(f"Invalid resource type requested: {resource_type}")
        return {
            "error": "Invalid resource type",
            "details": f"Type '{resource_type}' is not recognized. Valid types are: {', '.join(RESOURCE_TYPES.keys())}"
        }

    try:
        logger.info(f"Fetching {resource_type} data" + (f" for ID {resource_id}" if resource_id else ""))
        async with httpx.AsyncClient() as client:
            try:
                url = f"{BASE_URL}/{resource_type}"
                if resource_id:
                    url += f"/{resource_id}"
                elif search_query:
                    url += f"?search={search_query}"
                
                response = await client.get(
                    url,
                    headers=HEADERS,
                    timeout=10.0
                )
                response.raise_for_status()
                
            except httpx.TimeoutException:
                logger.error(f"Timeout while fetching {resource_type} data")
                return {
                    "error": "Request timeout",
                    "details": f"The request for {resource_type} data timed out after 10 seconds"
                }
                
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                logger.error(f"HTTP {status_code} error while fetching {resource_type} data: {str(e)}")
                error_msg = {
                    HTTPStatus.NOT_FOUND: "Resource not found",
                    HTTPStatus.BAD_REQUEST: "Invalid request",
                    HTTPStatus.TOO_MANY_REQUESTS: "Rate limit exceeded",
                }.get(status_code, "API request failed")
                
                return {
                    "error": error_msg,
                    "details": f"Failed to fetch {resource_type} data: {str(e)}",
                    "status_code": status_code
                }
                
            except httpx.RequestError as e:
                logger.error(f"Network error while fetching {resource_type} data: {str(e)}")
                return {
                    "error": "Network error",
                    "details": f"Failed to connect to Star Wars API: {str(e)}"
                }

            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Invalid JSON response for {resource_type}: {str(e)}")
                return {
                    "error": "Invalid response",
                    "details": f"Received invalid data for {resource_type}"
                }

            logger.info(f"Successfully fetched {resource_type} data")
            return {
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.exception(f"Unexpected error while fetching {resource_type} data")
        return {
            "error": "Unexpected error",
            "details": f"An unexpected error occurred while fetching {resource_type} data: {str(e)}"
        }

@mcp.tool()
async def get_character(name: str) -> Dict[str, Any]:
    """
    Get information about a Star Wars character
    
    Args:
        name: Name of the character to search for
        
    Returns:
        Dict containing character information
    """
    logger.info(f"Searching for character: {name}")
    return await fetch_resource("people", search_query=name)

@mcp.tool()
async def get_film(title: str) -> Dict[str, Any]:
    """
    Get information about a Star Wars film
    
    Args:
        title: Title of the film to search for
        
    Returns:
        Dict containing film information
    """
    logger.info(f"Searching for film: {title}")
    return await fetch_resource("films", search_query=title)

@mcp.tool()
async def get_starship(name: str) -> Dict[str, Any]:
    """
    Get information about a Star Wars starship
    
    Args:
        name: Name of the starship to search for
        
    Returns:
        Dict containing starship information
    """
    logger.info(f"Searching for starship: {name}")
    return await fetch_resource("starships", search_query=name)

@mcp.tool()
async def get_vehicle(name: str) -> Dict[str, Any]:
    """
    Get information about a Star Wars vehicle
    
    Args:
        name: Name of the vehicle to search for
        
    Returns:
        Dict containing vehicle information
    """
    logger.info(f"Searching for vehicle: {name}")
    return await fetch_resource("vehicles", search_query=name)

@mcp.tool()
async def get_species(name: str) -> Dict[str, Any]:
    """
    Get information about a Star Wars species
    
    Args:
        name: Name of the species to search for
        
    Returns:
        Dict containing species information
    """
    logger.info(f"Searching for species: {name}")
    return await fetch_resource("species", search_query=name)

@mcp.tool()
async def get_planet(name: str) -> Dict[str, Any]:
    """
    Get information about a Star Wars planet
    
    Args:
        name: Name of the planet to search for
        
    Returns:
        Dict containing planet information
    """
    logger.info(f"Searching for planet: {name}")
    return await fetch_resource("planets", search_query=name)

@mcp.tool()
async def search_all(query: str) -> Dict[str, Any]:
    """
    Search across all Star Wars categories for a given query
    
    Args:
        query: Search term to look for across all categories
        
    Returns:
        Dict containing search results from all categories
    """
    logger.info(f"Performing global search for: {query}")
    results = {}
    
    for resource_type in RESOURCE_TYPES.keys():
        result = await fetch_resource(resource_type, search_query=query)
        if "error" not in result:
            results[resource_type] = result["data"]
    
    return {
        "results": results,
        "timestamp": datetime.now().isoformat(),
        "query": query
    }

if __name__ == "__main__":
    logger.info("Starting Star Wars Information Server")
    mcp.run("stdio")
