from mcp.server.fastmcp import FastMCP
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

# Create an MCP server
mcp = FastMCP("Stars and Constellations Server")

def load_data() -> Dict[str, Any]:
    """Helper function to load the JSON data"""
    current_dir = Path(__file__).parent
    json_path = current_dir / "stars_and_constellations.json"
    with open(json_path, "r") as file:
        return json.load(file)

@mcp.tool()
def get_star(name: str) -> Dict[str, Any]:
    """
    Get details about a specific star
    
    Args:
        name: Name of the star to look up
        
    Returns:
        Dict containing star details or error message
    """
    try:
        data = load_data()
        for star in data["stars"]:
            if star["name"].lower() == name.lower():
                return star
        return {
            "error": "Star not found",
            "details": f"No star named '{name}' found in database"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def get_constellation(name: str) -> Dict[str, Any]:
    """
    Get details about a specific constellation
    
    Args:
        name: Name of the constellation to look up
        
    Returns:
        Dict containing constellation details or error message
    """
    try:
        data = load_data()
        for constellation in data["constellations"]:
            if constellation["name"].lower() == name.lower():
                return constellation
        return {
            "error": "Constellation not found",
            "details": f"No constellation named '{name}' found in database"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def get_all_data() -> Dict[str, Any]:
    """
    Get all stars and constellations data
    
    Returns:
        Dict containing all stars and constellations data
    """
    try:
        return load_data()
    except FileNotFoundError:
        return {
            "error": "Data file not found",
            "details": "stars_and_constellations.json file is missing"
        }
    except json.JSONDecodeError:
        return {
            "error": "Invalid JSON format",
            "details": "The file contains invalid JSON data"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "details": str(e)
        }

@mcp.tool()
def search_stars(criteria: str, value: str) -> List[Dict[str, Any]]:
    """
    Search stars by various criteria
    
    Args:
        criteria: What to search by (constellation, magnitude_less_than, magnitude_greater_than)
        value: The value to search for
        
    Returns:
        List of stars matching the criteria
    """
    try:
        data = load_data()
        results = []
        
        for star in data["stars"]:
            if criteria == "constellation":
                if star["constellation"].lower() == value.lower():
                    results.append(star)
            elif criteria == "magnitude_less_than":
                if star["magnitude"] < float(value):
                    results.append(star)
            elif criteria == "magnitude_greater_than":
                if star["magnitude"] > float(value):
                    results.append(star)
                    
        return results if results else {
            "error": "No matches found",
            "details": f"No stars found matching criteria '{criteria}' with value '{value}'"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "details": str(e)
        }

if __name__ == "__main__":
    mcp.run("stdio")