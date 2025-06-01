<div align="center">
    <img src="https://raw.githubusercontent.com/Ayanrajpoot10/bugscanx/refs/heads/main/assets/logo.png" width="128" height="128"/>
    <h1>BugScanX</h1>
    <p><b>All-in-One Tool for Finding SNI Bug Hosts</b></p>
    <p>🔍 Bug Host Discovery • 🌐 SNI Host Scanning • 🛡️ HTTP Analysis • 📊 Host Intelligence</p>
</div>

<p align="center">
    <img src="https://img.shields.io/github/stars/Ayanrajpoot10/bugscanx?color=e57474&labelColor=1e2528&style=for-the-badge"/>
    <img src="https://img.shields.io/pypi/dm/bugscan-x?color=67b0e8&labelColor=1e2528&style=for-the-badge"/>
    <img src="https://img.shields.io/pypi/v/bugscan-x?color=8ccf7e&labelColor=1e2528&style=for-the-badge"/>
    <img src="https://img.shields.io/github/license/Ayanrajpoot10/bugscanx?color=f39c12&labelColor=1e2528&style=for-the-badge"/>
    <img src="https://img.shields.io/github/last-commit/Ayanrajpoot10/bugscanx?color=9b59b6&labelColor=1e2528&style=for-the-badge"/>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Python-3.7+-3776ab?style=for-the-badge&logo=python&logoColor=white"/>
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-lightgrey?style=for-the-badge"/>
</p>


## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [⚡ Quick Start](#-quick-start)
- [🔧 Installation](#-installation)
- [🛠️ Tools Documentation](#️-tools-documentation)
- [🏗️ Architecture](#️-architecture)
- [🤝 Contributing](#-contributing)
- [⚠️ Disclaimer](#️-disclaimer)
- [📞 Support](#-support)


## 🎯 Overview

**BugScanX** is a specialized bug host discovery tool designed for finding working SNI/HTTP hosts that are suitable for tunneling applications. This tool helps users discover bug hosts that can be used to create configurations for various tunneling and VPN applications to enable unrestricted internet access.

## ✨ Features

### 🎯 Host Scanner Pro
Advanced multi-mode bug host scanning with specialized capabilities:
- **Direct Scanning**: HTTP/HTTPS bug host discovery with custom methods
- **DirectNon302**: Specialized scanning that excludes redirect responses (essential for bug hosts)
- **SSL/SNI Analysis**: TLS/SSL configuration analysis for SNI bug hosts
- **Proxy Testing**: Comprehensive proxy validation for tunneling compatibility
- **Ping Scanning**: Connectivity testing for discovered hosts
- Support for all HTTP methods and custom payload injection
- Multi-threaded concurrent processing

### 🔍 Subdomain Enumeration
Professional subdomain discovery for expanding bug host lists:
- **Passive Discovery**: Leverages multiple API providers and search engines
- **Active Enumeration**: DNS brute-force for comprehensive coverage
- **Batch Processing**: Mass domain enumeration from target lists

### 🌐 IP Lookup & Reverse DNS
Comprehensive IP intelligence for bug host clustering:
- **Reverse IP Lookup**: Discover all domains hosted on target IPs
- **CIDR Range Processing**: Bulk analysis of IP ranges
- **Multi-Source Aggregation**: Combines data from multiple sources

### 📡 CIDR Scanner
Efficient IP range analysis for bug host discovery with port enumeration and custom HTTP methods.

### 🚪 Port Scanner
Advanced port scanning for service discovery with common tunneling ports (80, 443, 8080, 8443).

### 🔎 DNS & SSL Analysis
Comprehensive analysis for SNI bug hosts including DNS records and SSL certificate validation.

### 📁 File Management & Processing
Professional-grade file processing with smart splitting, merging, deduplication, and filtering tools.


## ⚡ Quick Start

### 🚀 Installation

```bash
# Install from PyPI
pip install bugscan-x
```

### 🎮 Launch BugScanX

```bash
# Primary command
bugscanx

# Alternative commands
bugscan-x
bx
```

### 🎯 Interactive Menu

```
    ╔╗ ╦ ╦╔═╗╔═╗╔═╗╔═╗╔╗╔═╗ ╦
    ╠╩╗║ ║║ ╦╚═╗║  ╠═╣║║║╔╩╦╝
    ╚═╝╚═╝╚═╝╚═╝╚═╝╩ ╩╝╚╝╩ ╚═

[1]  HOST SCANNER PRO     # Advanced bug host scanner with multiple modes
[2]  HOST SCANNER         # Simplified bug host scanner 
[3]  CIDR SCANNER         # CIDR/IP scanner for bug host
[4]  SUBFINDER            # Subdomain enumeration with active and passive modes
[5]  IP LOOKUP            # Reverse IP lookup
[6]  FILE TOOLKIT         # Bug host list management
[7]  PORT SCANNER         # Port scanner to discover open ports
[8]  DNS RECORD           # DNS record gathering
[9]  HOST INFO            # Detailed bug host analysis
[10] HELP                 # Documentation and usage examples
[11] UPDATE               # Self-update tool
[12] EXIT                 # Quit application
```

### 📱 Using Discovered Bug Hosts

Once you discover working bug hosts using BugScanX, you can use them to create configurations for various tunneling and VPN applications to bypass network restrictions.


## 🔧 Installation

### 📋 System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, Linux, macOS, Android (Termux)
- **Network**: Internet connection

### 🔨 Installation Methods

#### PyPI Installation (Recommended)

```bash
# Install latest stable version
pip install bugscan-x

# Install beta version
pip install --pre bugscan-x
```

#### Development Installation

```bash
# Clone repository
git clone https://github.com/Ayanrajpoot10/bugscanx.git
cd bugscanx

# Install in development mode
pip install -e .
```

### 🔗 Dependencies

BugScanX automatically installs the following dependencies:

```text
beautifulsoup4   # HTML parsing and web scraping
dnspython        # DNS resolution and analysis
InquirerPy       # Interactive CLI prompts
packaging        # Version management
pyfiglet         # ASCII art generation
requests         # HTTP client library
rich             # Rich console output
tqdm             # Progress bars
```

## 🛠️ Tools Documentation

### 1️⃣ Host Scanner Pro

Advanced bug host discovery with multiple scanning modes:

- **Direct Mode**: Standard HTTP/HTTPS bug host scanning
- **DirectNon302 Mode**: Excludes redirect responses (essential for clean bug hosts)
- **SSL/SNI Mode**: SNI hostname verification and TLS analysis
- **Proxy Mode**: Websocket upgrade testing and proxy validation

### 2️⃣ Subfinder

Professional subdomain enumeration using multiple sources:
- Certificate Transparency logs
- Search engines and APIs
- DNS records analysis
- Batch processing for multiple domains

### 3️⃣ IP Lookup

Reverse IP analysis for related bug host discovery:
- Multi-source domain lookup
- CIDR range processing
- Historical hosting data

### 4️⃣ File Toolkit

Advanced file processing operations:
```bash
[1] SPLIT FILE      # Divide large bug host lists
[2] MERGE FILES     # Combine multiple discoveries
[3] CLEAN FILE      # Extract clean domains
[4] DEDUPLICATE     # Remove duplicates
[5] FILTER BY TLD   # Filter by domain extension
[6] FILTER BY KEYWORD # Filter by criteria
[7] CIDR TO IP      # Expand network ranges
[8] DOMAIN TO IP    # Resolve to IP addresses
```

### 5️⃣ Port Scanner

High-performance port enumeration:
- Common tunneling ports (80, 443, 8080, 8443, 8888)
- Full range scanning
- Service detection and connection testing

### 6️⃣ DNS Record Analyzer

Comprehensive DNS intelligence:
- A, AAAA, CNAME, MX, NS, TXT records
- IPv4/IPv6 address resolution
- Name server analysis


## ⚙️ Configuration

### 🛠️ Scanning Parameters
- **Thread Count**: Adjust concurrent threads (default: 50)
- **Timeout Settings**: Configure connection timeouts
- **Port Lists**: Customize target ports
- **HTTP Methods**: Select specific methods for discovery

### 📂 Output Configuration
- **File Formats**: TXT, JSON, CSV output options
- **Result Filtering**: Filter by response codes and content types
- **Logging Levels**: Adjust verbosity for debugging

### 🌐 Network Settings
- **Proxy Configuration**: Use proxy servers for scanning
- **DNS Settings**: Configure custom DNS servers
- **User Agent**: Customize HTTP user agent strings

### 🎯 Advanced Settings
- **DirectNon302 Mode**: Exclude redirect responses for clean bug hosts
- **SSL/SNI Configuration**: TLS version preferences and certificate validation
- **Timeout Settings**: SSL handshake and connection timeouts


## 🏗️ Architecture

BugScanX is built with a modular architecture for extensibility and performance:

### 🔧 Core Components

- **Module Handler**: Dynamic module loading and execution
- **Concurrency Engine**: Multi-threaded processing with ThreadPoolExecutor
- **Rich Console Interface**: Advanced console output with progress tracking
- **File Management**: Smart file operations and processing
- **Network Layer**: HTTP/HTTPS requests with proxy support


## 🤝 Contributing

We welcome contributions from the security community!

### 🐛 Bug Reports

Create an issue with:
- Clear description of the issue
- Steps to reproduce
- Environment details (OS, Python version, BugScanX version)
- Expected vs actual behavior

### 💡 Feature Requests

Include:
- Feature description and use case
- Implementation ideas


## ⚠️ Disclaimer

### 🚨 Important Notice

BugScanX is designed for **educational purposes** and **legitimate testing** only:

- ✅ **Learning**: Understanding tunneling and bypass techniques
- ✅ **Personal Use**: Testing your own networks and systems
- ✅ **Research**: Academic and educational research
- ✅ **Legal Testing**: Authorized penetration testing

### ⚠️ Responsible Usage

- **🔒 Legal Compliance**: Always comply with local laws
- **📋 Permission Required**: Only test systems you own or have permission to test
- **🤝 Respect Networks**: Avoid overwhelming target servers
- **🛡️ Ethical Use**: Use discovered bug hosts responsibly
- **❌ No Unauthorized Testing**: Never scan without proper authorization

### 📝 Usage Agreement

By using BugScanX, you agree to use the tool only for legitimate purposes and take full responsibility for your actions.

### 🚨 Legal Warning

**The developers are not responsible for any misuse of this tool. Users must ensure compliance with all applicable laws.**


## 📞 Support

### 💬 Community Support

- **Telegram**: [@BugScanX](https://t.me/BugScanX) - Community discussions
- **GitHub Issues**: [Report bugs and request features](https://github.com/Ayanrajpoot10/bugscanx/issues)
- **GitHub Discussions**: [Community Q&A](https://github.com/Ayanrajpoot10/bugscanx/discussions)

### 📚 Documentation

- **Built-in Help**: Use option `[10] HELP` in the application
- **Wiki**: [Comprehensive documentation](https://github.com/Ayanrajpoot10/bugscanx/wiki)


---


<div align="center">
    <h3>Built with ❤️ for the Free Internet Community</h3>
    <p>
        <a href="https://github.com/Ayanrajpoot10">👨‍💻 Developer</a> •
        <a href="https://t.me/BugScanX">💬 Telegram</a> •
        <a href="https://github.com/Ayanrajpoot10/bugscanx/issues">🐛 Issues</a> •
        <a href="https://pypi.org/project/bugscan-x/">📦 PyPI</a>
    </p>
    <p><sub>⚠️ This tool is intended for educational and authorized testing purposes only. Use responsibly and legally.</sub></p>
</div>
