import logging
import sys
from mcp.server.fastmcp import FastMCP
import subprocess
import asyncio
import os
import json
import base64
from typing import Optional, Dict, Any, List
from pathlib import Path

# Configure logging with a detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Terminal Server")

# List of dangerous commands that should be blocked
BLOCKED_COMMANDS = [
    "rm -rf /",
    "shutdown",
    "reboot",
    "sudo rm",
    "init 0",
    "halt",
]

# List of protected system paths
PROTECTED_PATHS = [
    "/System",
    "/bin",
    "/sbin",
    "/usr",
    "/etc",
    "/var",
    "/boot",
]

def is_safe_command(command: str) -> bool:
    """
    Check if a command is safe to execute
    
    Args:
        command: The command to check
        
    Returns:
        bool: True if the command is safe, False otherwise
    """
    command = command.lower().strip()
    
    # Check for blocked commands
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            logger.warning(f"Blocked command attempted: {command}")
            return False
            
    # Check for protected paths
    for path in PROTECTED_PATHS:
        if path in command and ("rm" in command or "mv" in command or "rmdir" in command):
            logger.warning(f"Attempted operation on protected path: {path}")
            return False
            
    # Check for sudo/su commands
    if command.startswith("sudo ") or command.startswith("su "):
        logger.warning("Attempted privileged command execution")
        return False
        
    return True

@mcp.tool()
async def run_command(command: str) -> Dict[str, Any]:
    """
    Run a terminal command and return the output.
    
    Args:
        command: The command to execute in the terminal
        
    Returns:
        A dictionary containing stdout, stderr, and return code
    """
    try:
        logger.info(f"Received command request: {command}")
        
        # Check if command is safe
        if not is_safe_command(command):
            logger.error(f"Command blocked for security reasons: {command}")
            return {
                "stdout": "",
                "stderr": "Command blocked for security reasons",
                "return_code": 1,
                "blocked": True
            }
        
        # Log current working directory
        logger.debug(f"Current working directory: {os.getcwd()}")
        
        # Execute the command
        logger.info(f"Executing command: {command}")
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Get output
        stdout, stderr = await process.communicate()
        stdout_str = stdout.decode() if stdout else ""
        stderr_str = stderr.decode() if stderr else ""
        
        # Log command results
        logger.info(f"Command completed with return code: {process.returncode}")
        if stdout_str:
            logger.debug(f"Command stdout: {stdout_str[:200]}...")
        if stderr_str:
            logger.warning(f"Command stderr: {stderr_str}")
        
        # Return results
        return {
            "stdout": stdout_str,
            "stderr": stderr_str,
            "return_code": process.returncode,
            "blocked": False
        }
        
    except asyncio.CancelledError:
        logger.error(f"Command execution cancelled: {command}")
        return {
            "stdout": "",
            "stderr": "Command execution cancelled",
            "return_code": -1,
            "blocked": False
        }
    except Exception as e:
        logger.error(f"Error executing command: {command}", exc_info=True)
        return {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "return_code": -1,
            "blocked": False
        }

if __name__ == "__main__":
    try:
        logger.info("Starting Terminal Server")
        mcp.run("stdio")
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal error occurred", exc_info=True)
        sys.exit(1)