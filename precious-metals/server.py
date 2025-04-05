from mcp.server.fastmcp import FastMCP
import httpx
from typing import Dict, Any, List
from datetime import datetime
import logging
import sys
from http import HTTPStatus

# Configure logging with a detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Precious Metals Price Server")

# API configuration
BASE_URL = "https://api.gold-api.com"
HEADERS = {
    "Content-Type": "application/json"
}

# Metal configuration
METAL_SYMBOLS = {
    "XAU": "Gold",
    "XAG": "Silver",
    "XPD": "Palladium",
    "HG": "Copper"
}

class MetalPriceError(Exception):
    """Custom exception for metal price fetching errors"""
    def __init__(self, message: str, symbol: str, status_code: int = None):
        self.message = message
        self.symbol = symbol
        self.status_code = status_code
        super().__init__(self.message)

async def fetch_metal_price(symbol: str) -> Dict[str, Any]:
    """
    Helper function to fetch metal price from the API
    
    Args:
        symbol: The metal symbol to fetch price for (XAU, XAG, XPD, HG)
        
    Returns:
        Dict containing metal price details or error information
        
    Raises:
        MetalPriceError: If there's an error fetching the price
    """
    if symbol not in METAL_SYMBOLS:
        logger.error(f"Invalid metal symbol requested: {symbol}")
        return {
            "error": "Invalid metal symbol",
            "details": f"Symbol '{symbol}' is not recognized. Valid symbols are: {', '.join(METAL_SYMBOLS.keys())}"
        }

    try:
        logger.info(f"Fetching price for {METAL_SYMBOLS[symbol]} ({symbol})")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{BASE_URL}/price/{symbol}",
                    headers=HEADERS,
                    timeout=10.0  # 10 second timeout
                )
                response.raise_for_status()
                
            except httpx.TimeoutException:
                logger.error(f"Timeout while fetching {symbol} price")
                return {
                    "error": "Request timeout",
                    "details": f"The request for {METAL_SYMBOLS[symbol]} price timed out after 10 seconds"
                }
                
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                logger.error(f"HTTP {status_code} error while fetching {symbol} price: {str(e)}")
                error_msg = {
                    HTTPStatus.NOT_FOUND: "Metal price data not found",
                    HTTPStatus.UNAUTHORIZED: "API authentication failed",
                    HTTPStatus.TOO_MANY_REQUESTS: "Rate limit exceeded",
                }.get(status_code, "API request failed")
                
                return {
                    "error": error_msg,
                    "details": f"Failed to fetch {METAL_SYMBOLS[symbol]} price: {str(e)}",
                    "status_code": status_code
                }
                
            except httpx.RequestError as e:
                logger.error(f"Network error while fetching {symbol} price: {str(e)}")
                return {
                    "error": "Network error",
                    "details": f"Failed to connect to price API: {str(e)}"
                }

            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Invalid JSON response for {symbol}: {str(e)}")
                return {
                    "error": "Invalid response",
                    "details": f"Received invalid data for {METAL_SYMBOLS[symbol]}"
                }

            if not data.get("price"):
                logger.warning(f"No price data found for {symbol}")
                return {
                    "error": "Missing price data",
                    "details": f"No price information available for {METAL_SYMBOLS[symbol]}"
                }

            logger.info(f"Successfully fetched price for {symbol}")
            return {
                "metal": METAL_SYMBOLS[symbol],
                "symbol": symbol,
                "price": data.get("price"),
                "currency": "USD",
                "last_updated": data.get("updatedAtReadable", "Unknown"),
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.exception(f"Unexpected error while fetching {symbol} price")
        return {
            "error": "Unexpected error",
            "details": f"An unexpected error occurred while fetching {METAL_SYMBOLS[symbol]} price: {str(e)}"
        }

@mcp.tool()
async def get_gold_price() -> Dict[str, Any]:
    """
    Get the current gold price in USD
    
    Returns:
        Dict containing gold price details
    """
    logger.info("Getting gold price")
    return await fetch_metal_price("XAU")

@mcp.tool()
async def get_silver_price() -> Dict[str, Any]:
    """
    Get the current silver price in USD
    
    Returns:
        Dict containing silver price details
    """
    logger.info("Getting silver price")
    return await fetch_metal_price("XAG")

@mcp.tool()
async def get_palladium_price() -> Dict[str, Any]:
    """
    Get the current palladium price in USD
    
    Returns:
        Dict containing palladium price details
    """
    logger.info("Getting palladium price")
    return await fetch_metal_price("XPD")

@mcp.tool()
async def get_copper_price() -> Dict[str, Any]:
    """
    Get the current copper price in USD
    
    Returns:
        Dict containing copper price details
    """
    logger.info("Getting copper price")
    return await fetch_metal_price("HG")

@mcp.tool()
async def get_all_metal_prices() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get prices for all available metals (Gold, Silver, Palladium, Copper)
    
    Returns:
        Dict containing a list of all metal prices
    """
    logger.info("Getting prices for all metals")
    metals = ["XAU", "XAG", "XPD", "HG"]
    results = []
    
    for symbol in metals:
        result = await fetch_metal_price(symbol)
        results.append(result)
    
    response = {
        "prices": results,
        "timestamp": datetime.now().isoformat(),
        "currency": "USD"
    }
    
    # Log any errors that occurred
    errors = [r for r in results if "error" in r]
    if errors:
        logger.warning(f"Errors occurred while fetching some metal prices: {len(errors)} errors")
        for error in errors:
            logger.error(f"Metal price error: {error.get('error')} - {error.get('details')}")
    else:
        logger.info("Successfully fetched all metal prices")
    
    return response

if __name__ == "__main__":
    logger.info("Starting Precious Metals Price Server")
    mcp.run("stdio")
