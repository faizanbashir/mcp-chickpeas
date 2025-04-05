# MCP Chickpeas

A collection of Model Context Protocol (MCP) servers providing various functionalities through a standardized interface.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Available Servers](#available-servers)
  - [Gemini AI Server](#gemini-ai-server)
  - [Star Wars Information Server](#star-wars-information-server)
  - [Stars and Constellations Server](#stars-and-constellations-server)
  - [Precious Metals Server](#precious-metals-server)
  - [Shell Command Server](#shell-command-server)

## Overview

This repository contains multiple MCP servers that can be used with Claude for Desktop and other MCP-compatible clients. Each server provides specific functionality through a set of tools and resources.

## Installation

### Prerequisites
- Python 3.10 or higher
- UV package manager

### Installing UV

On MacOS:
```bash
brew install uv
```

On Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows:
```bash
curl -LsSf https://astral.sh/uv/install.ps1 | powershell
```

### Setting up the Project

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-chickpeas
```

2. Create and activate a virtual environment:
```bash
# Create virtual environment
uv venv
# Activate on MacOS/Linux
source .venv/bin/activate
# Activate on Windows
.venv\Scripts\activate
```

3. Install dependencies for a specific server:
```bash
cd <server-directory>
uv pip install -r requirements.txt
```

Or install all servers' dependencies:
```bash
uv pip install "mcp[cli]" httpx google-generativeai
```

## Available Servers

### Gemini AI Server

Located in `/gemini` directory, this server provides access to Google's Gemini AI models.

#### Features
- Multiple model support (gemini-1.5-flash, gemini-2.0-flash, etc.)
- Content generation
- Text analysis
- Chat functionality

#### Available Tools

1. `generate_content`
   ```python
   async def generate_content(prompt: str, model_name: str = "gemini-2.0-flash")
   ```
   - Generates AI content based on the provided prompt
   - Configurable parameters for temperature, top_p, and top_k
   - Built-in safety filters

2. `analyze_text`
   ```python
   async def analyze_text(text: str, analysis_type: str = "sentiment")
   ```
   - Supports sentiment analysis, entity extraction, and classification
   - Returns detailed analysis with confidence scores

3. `chat_stream`
   ```python
   async def chat_stream(messages: List[Dict[str, str]], model_name: str = "gemini-2.0-flash")
   ```
   - Enables interactive chat sessions
   - Supports conversation history

4. `list_models`
   ```python
   async def list_models()
   ```
   - Returns available Gemini models and their descriptions

#### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key

### Star Wars Information Server

Located in `/starwars` directory, provides information about Star Wars universe elements.

#### Available Tools

1. `get_character`
   ```python
   async def get_character(name: str)
   ```
   - Retrieves information about Star Wars characters

2. `get_film`
   ```python
   async def get_film(title: str)
   ```
   - Fetches details about Star Wars films

3. `get_starship`
   ```python
   async def get_starship(name: str)
   ```
   - Gets information about starships

4. `get_vehicle`
   ```python
   async def get_vehicle(name: str)
   ```
   - Retrieves vehicle information

5. `get_species`
   ```python
   async def get_species(name: str)
   ```
   - Fetches species details

6. `get_planet`
   ```python
   async def get_planet(name: str)
   ```
   - Gets information about planets

7. `search_all`
   ```python
   async def search_all(query: str)
   ```
   - Searches across all Star Wars categories

### Stars and Constellations Server

Located in `/stars` directory, provides astronomical data about stars and constellations.

#### Available Tools

1. `get_star`
   ```python
   async def get_star(name: str)
   ```
   - Retrieves information about specific stars

2. `get_constellation`
   ```python
   async def get_constellation(name: str)
   ```
   - Fetches constellation details

3. `get_all_data`
   ```python
   async def get_all_data()
   ```
   - Returns complete database of stars and constellations

4. `search_stars`
   ```python
   async def search_stars(criteria: str, value: str)
   ```
   - Searches stars based on various criteria

### Precious Metals Server

Located in `/precious-metals` directory, provides real-time precious metal prices.

#### Available Tools

1. `get_gold_price`
   ```python
   async def get_gold_price()
   ```
   - Returns current gold price in USD

2. `get_silver_price`
   ```python
   async def get_silver_price()
   ```
   - Returns current silver price in USD

3. `get_palladium_price`
   ```python
   async def get_palladium_price()
   ```
   - Returns current palladium price in USD

4. `get_copper_price`
   ```python
   async def get_copper_price()
   ```
   - Returns current copper price in USD

5. `get_all_metal_prices`
   ```python
   async def get_all_metal_prices()
   ```
   - Returns prices for all available metals

### Shell Command Server

Located in `/shell` directory, provides secure command execution capabilities in the terminal.

#### Features
- Secure command execution with safety checks
- Directory navigation
- File system operations
- Protected system paths
- Command blacklisting

#### Available Tools

1. `run_command`
   ```python
   async def run_command(command: str) -> Dict[str, Any]
   ```
   - Executes shell commands securely
   - Returns command output and status
   - Implements safety checks for dangerous operations

#### Safety Features
- Blocks dangerous system commands (rm -rf /, shutdown, etc.)
- Protects critical system directories
- Prevents execution of sudo commands
- Validates commands before execution
- Blocks force flags with destructive commands

#### Protected Paths
- System directories (/System, /bin, /sbin, /usr, etc.)
- Application directories
- System configuration files
- Critical system files

#### Blocked Commands
- System shutdown/reboot commands
- Dangerous recursive delete commands
- System-level operations requiring sudo
- Network interface modifications
- System service management

#### Usage Examples

Safe commands that are allowed:
```bash
# File operations
ls /Users/myname/
mkdir newfolder
cat myfile.txt

# Navigation
cd /Users/myname/Documents
pwd

# Basic system info
date
whoami
```

Commands that will be blocked:
```bash
rm -rf /
shutdown now
sudo rm -rf /
rm -rf /*
```

## Usage

To use any server:

1. Navigate to the server directory:
```bash
cd <server-directory>
```

2. Install dependencies:
```bash
uv pip install -r requirements.txt
```

3. Set required environment variables (if any). For example:
```bash
# For Gemini AI Server
export GEMINI_API_KEY="your-api-key"
```

4. Run the server:
```bash
python server.py
```

5. Connect to the server using an MCP-compatible client like Claude for Desktop

## Error Handling

All servers implement proper error handling and logging. Check the server logs for detailed information about any issues that occur during operation.

### Common Issues and Solutions

1. **Package Installation Issues**
```bash
# If UV installation fails, try:
pip install uv

# If dependency installation fails, try:
uv pip install --upgrade pip
uv pip install -r requirements.txt --no-cache
```

2. **Permission Issues**
```bash
# For permission denied errors:
chmod +x server.py
```

3. **API Key Issues**
```bash
# Verify environment variables:
echo $GEMINI_API_KEY
# If empty, set it:
export GEMINI_API_KEY="your-api-key"
```

## Contributing

Feel free to contribute by:
1. Opening issues for bugs or feature requests
2. Submitting pull requests with improvements
3. Adding documentation or examples

### Development Setup
```bash
# Create development environment
uv venv
source .venv/bin/activate

# Install development dependencies
uv pip install -r requirements-dev.txt

# Run tests
python -m pytest
```

## License

MIT License - See LICENSE file for details
