

A Python based CLI tool designed to monitor website health across multiple endpoints simultaneously. 

I built this to learn how to handle bulk URL checks efficiently using multi threading, providing real time terminal feedback and automated CSV logging.

## Core Features
* **Multi threaded Polling:** Leverages `ThreadPoolExecutor` for concurrent requests, significantly reducing total execution time.
* **Instantaneous Visuals:** Uses `colorama` for color-coded status reporting (Success/Warning/Critical).
* **Automated Reporting:** Exports every run to a timestamped CSV for historical tracking.
* **Resilient Logic:** Implements specific exception handling for timeouts and DNS failures to ensure the script doesn't hang on dead links.

## Quick Start

### 1. Installation
```bash
# Clone and enter directory
cd health-monitor

# Install requirements
pip install -r requirements.txt

# Run code
python monitor.py