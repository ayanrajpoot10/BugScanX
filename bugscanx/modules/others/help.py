from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

console = Console()


def show_detailed_help():
    help_sections = [
        show_overview(),
        show_host_scanner_help(),
        show_subfinder_help(),
        show_ip_lookup_help(),
        show_file_toolkit_help(),
        show_port_scanner_help(),
        show_dns_records_help(),
        show_host_info_help(),
        show_usage_examples(),
        show_tips_and_tricks()
    ]
    
    for section in help_sections:
        console.print(section)
        console.print()


def show_overview():
    overview_text = """
# 🎯 BugScanX - All-in-One SNI Bug Host Discovery Tool

**BugScanX** is a comprehensive bug host discovery tool designed for finding working SNI/HTTP hosts suitable for tunneling applications. It helps security researchers, penetration testers, and network administrators discover bug hosts that can be used for various tunneling and VPN configurations.

## ✨ Key Features
- Advanced multi-mode host scanning
- Professional subdomain enumeration  
- Comprehensive IP intelligence gathering
- Powerful file management toolkit
- High-performance port scanning
- DNS and SSL analysis capabilities
"""
    return Panel(
        Markdown(overview_text),
        title="[bold blue]Overview[/bold blue]",
        border_style="bold blue",
        expand=True
    )


def show_host_scanner_help():
    scanner_text = """
# 🔍 HOST SCANNER - Advanced Bug Host Discovery

The Host Scanner is BugScanX's most powerful feature for discovering working bug hosts.

## Scanning Modes

### 1. Direct Mode
- Standard HTTP/HTTPS bug host scanning
- **Usage**: Scan hosts with various HTTP methods
- **Best for**: General bug host discovery
- **Example Input**: hosts.txt containing domain/IP list

### 2. DirectNon302 Mode  
- **Special**: Excludes redirect responses (HTTP 302)
- **Critical for**: Clean bug hosts without redirects
- **Use case**: Finding hosts that won't redirect traffic

### 3. SSL/SNI Mode
- SNI hostname verification and TLS analysis
- **Purpose**: Test SSL/TLS configurations
- **Identifies**: Working SNI bug hosts for HTTPS tunneling

### 4. ProxyTest Mode
- Websocket upgrade testing
- **Function**: Validates proxy compatibility
- **Critical for**: Tunneling applications

### 5. ProxyRoute Mode
- Advanced proxy routing validation
- **Tests**: Complex proxy configurations
- **For**: Multi-hop tunneling setups

### 6. Ping Mode
- Basic connectivity testing
- **Quick check**: Host availability
- **Lightweight**: Fast network reachability test

## Input Options
- **File Input**: TXT file with hosts (one per line)
- **CIDR Input**: IP ranges (e.g., 192.168.1.0/24)
- **Manual Input**: Single hosts or comma-separated list

## Configuration Parameters
- **Ports**: 80, 443, 8080, 8443 (common tunneling ports)
- **Threads**: 1-100 (default: 50 for optimal performance)
- **Timeout**: 1-30 seconds (default: 3 seconds)
- **HTTP Methods**: GET, POST, HEAD, PUT, DELETE, OPTIONS, TRACE, PATCH
"""
    return Panel(
        Markdown(scanner_text),
        title="[bold cyan]HOST SCANNER[/bold cyan]",
        border_style="bold cyan",
        expand=True
    )


def show_subfinder_help():
    subfinder_text = """
# 🌐 SUBFINDER - Professional Subdomain Enumeration

Discover subdomains to expand your bug host hunting scope.

## Discovery Methods

### Passive Discovery
- **Certificate Transparency**: Search CT logs for subdomains
- **Search Engines**: Google, Bing, Yahoo dorking
- **DNS Records**: Analyze existing DNS configurations
- **Third-party APIs**: Multiple intelligence sources

## Input Methods
- **Single Domain**: example.com
- **Batch Processing**: domains.txt file
- **Wildcard Domains**: *.example.com patterns

## Output Features
- **Deduplication**: Automatic duplicate removal
- **Validation**: Live subdomain verification
- **Sorting**: Alphabetical and length-based sorting
- **Filtering**: Remove inactive subdomains

## Use Cases
- Expand target scope for bug host discovery
- Reconnaissance for penetration testing
- Asset discovery for organizations
- Bug bounty hunting preparation
"""
    return Panel(
        Markdown(subfinder_text),
        title="[bold magenta]SUBFINDER[/bold magenta]",
        border_style="bold magenta",
        expand=True
    )


def show_ip_lookup_help():
    ip_text = """
# 🔎 IP LOOKUP - Reverse IP Intelligence

Discover all domains hosted on target IP addresses.

## Lookup Types

### Single IP Lookup
- **Input**: Single IP address (e.g., 192.168.1.1)
- **Output**: All domains hosted on that IP
- **Use case**: Find related bug hosts

### CIDR Range Analysis
- **Input**: Network ranges (e.g., 192.168.1.0/24)
- **Process**: Scan entire IP ranges
- **Output**: Complete domain mapping

### Batch IP Processing
- **Input**: IP list file (ips.txt)
- **Processing**: Concurrent lookups
- **Efficiency**: Multi-threaded analysis

## Data Sources
- **Reverse DNS**: PTR record lookups
- **Historical Data**: Past hosting information
- **SSL Certificates**: Certificate transparency logs
- **Web Crawling**: Active web server detection

## Analysis Features
- **Domain Clustering**: Group related domains
- **Hosting Provider**: Identify cloud/hosting services
- **Geographic Location**: IP geolocation data
- **Port Analysis**: Open port correlation

## Strategic Applications
- **Bug Host Clustering**: Find related working hosts
- **Infrastructure Mapping**: Understand target networks
- **Pivot Analysis**: Expand from known good hosts
"""
    return Panel(
        Markdown(ip_text),
        title="[bold cyan]IP LOOKUP[/bold cyan]",
        border_style="bold cyan",
        expand=True
    )


def show_file_toolkit_help():
    """Show detailed help for File Toolkit"""
    toolkit_text = """
# 📁 FILE TOOLKIT - Advanced File Management

Professional file processing for bug host lists and data management.

## Core Operations

### 1. Split Files
- **Purpose**: Divide large host lists into smaller chunks
- **Use case**: Parallel processing or size management
- **Options**: Split by number of parts (equal distribution)

### 2. Merge Files  
- **Function**: Combine multiple discovery results
- **Options**: Merge all TXT files in directory or specific files
- **Smart processing**: Maintains line integrity

### 3. Clean Files
- **Extract**: Clean domain names and IP addresses from mixed content
- **Separate outputs**: Creates separate files for domains and IPs
- **Regex-based**: Uses advanced pattern matching for accuracy

### 4. Deduplicate
- **Algorithm**: Remove duplicate entries and sort results
- **In-place**: Modifies original file
- **Memory efficient**: Handle large files effectively

### 5. Filter by TLD
- **Target**: Specific domain extensions (.com, .org, etc.)
- **Interactive**: Choose from available TLDs in file
- **Separate files**: Creates individual files for each TLD

### 6. Filter by Keywords
- **Include**: Lines containing specific terms
- **Case-insensitive**: Smart pattern matching
- **Multiple keywords**: Comma-separated keyword support

### 7. CIDR to IP Conversion
- **Expand**: Network ranges to individual IP addresses
- **Calculation**: Automatic subnet expansion using Python ipaddress
- **Output**: Complete IP lists ready for scanning

### 8. Domain to IP Resolution
- **Resolve**: Domain names to IP addresses using DNS
- **Multi-threaded**: Concurrent DNS resolution (100 workers)
- **Progress tracking**: Real-time resolution progress
- **Error handling**: Gracefully handles failed resolutions

## File Format Support
- **Input**: TXT files with UTF-8 encoding
- **Output**: TXT format with clean formatting
- **Encoding**: UTF-8 support for international domains
- **Size handling**: Efficiently processes large files
"""
    return Panel(
        Markdown(toolkit_text),
        title="[bold magenta]FILE TOOLKIT[/bold magenta]",
        border_style="bold magenta",
        expand=True
    )


def show_port_scanner_help():
    port_text = """
# 🚪 PORT SCANNER - Service Discovery

High-performance port enumeration for bug host analysis.

## Scanning Modes

### Common Ports Scan
- **Ports**: 21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888
- **Speed**: Fast basic discovery
- **Use case**: Initial reconnaissance

### Full Range Scan
- **Ports**: 1-65535 (complete port range)
- **Comprehensive**: Detailed service discovery
- **Time**: Longer but thorough analysis

## Detection Features

### Connection Testing
- **TCP Connect**: Full three-way handshake
- **Timeout**: 1 second per port
- **Multi-threaded**: Concurrent scanning

### Target Resolution
- **Hostname support**: Automatically resolves domain names
- **IP addresses**: Direct IP scanning
- **Error handling**: DNS resolution validation

## Performance Features
- **Threading**: Multi-threaded concurrent connections
- **Progress tracking**: Real-time scanning progress
- **Result display**: Clear open port listing
- **Error handling**: Graceful failure management

## Output Analysis
- **Open Ports**: List of accessible ports
- **Target Info**: Resolved IP and hostname
- **Progress tracking**: Visual progress indicators
- **Summary**: Total ports scanned and found
"""
    return Panel(
        Markdown(port_text),
        title="[bold white]PORT SCANNER[/bold white]",
        border_style="bold white",
        expand=True
    )


def show_dns_records_help():
    dns_text = """
# 🔍 DNS RECORDS - Comprehensive DNS Analysis

Gather complete DNS intelligence for target domains.

## Record Types

### A Records (IPv4)
- **Purpose**: Domain to IPv4 address mapping
- **Critical for**: Host identification and targeting
- **Analysis**: IPv4 address resolution

### AAAA Records (IPv6)
- **Function**: Domain to IPv6 address mapping
- **Modern**: IPv6 infrastructure discovery
- **Dual-stack**: IPv6 address resolution

### CNAME Records
- **Aliases**: Domain name aliases and redirections
- **Infrastructure**: CDN and hosting provider identification
- **Chain resolution**: Alias mapping

### MX Records
- **Mail servers**: Email infrastructure mapping
- **Priority**: Mail server priority information
- **Configuration**: Email routing analysis

### NS Records
- **Name servers**: DNS infrastructure mapping
- **Provider**: DNS hosting provider identification
- **Authority**: DNS zone authority information

### TXT Records
- **Metadata**: Domain verification and configuration
- **Security**: SPF, DKIM, DMARC records
- **Services**: Third-party service verification

## Analysis Features

### DNS Resolution
- **Multiple record types**: A, AAAA, CNAME, MX, NS, TXT
- **Error handling**: Graceful failure for missing records
- **Clear output**: Formatted record display

### Record Information
- **Complete data**: Full record information
- **MX priority**: Mail server priority display
- **Text formatting**: Clean, readable output

## Output Format
- **Structured display**: Clear record type sections
- **Color coding**: Visual distinction for different record types
- **Error reporting**: Clear indication of missing records
- **Comprehensive**: All standard DNS record types
"""
    return Panel(
        Markdown(dns_text),
        title="[bold green]DNS RECORDS[/bold green]",
        border_style="bold green",
        expand=True
    )


def show_host_info_help():
    """Show detailed help for Host Info"""
    info_text = """
# 📊 HOST INFO - Comprehensive Host Analysis

Detailed intelligence gathering for target hosts.

## Information Categories

### Network Information
- **IP Resolution**: Resolve hostname to multiple IP addresses
- **IPv4/IPv6**: Support for both IP versions
- **Multiple IPs**: Display all resolved IP addresses
- **DNS Validation**: Error handling for invalid hostnames

### HTTP Method Analysis
- **Method Testing**: Test multiple HTTP methods (GET, HEAD, POST, PUT, DELETE, OPTIONS, TRACE, PATCH)
- **Status Codes**: HTTP response status analysis
- **Headers**: Complete HTTP header analysis
- **Multi-threaded**: Concurrent method testing (10 workers)

### CDN Detection
- **Provider Detection**: Identify major CDN providers:
  - Cloudflare, Amazon CloudFront, Google, Akamai, Fastly
  - Microsoft Azure, BunnyCDN, Sucuri, Imperva, Cachefly
  - Alibaba, Tencent
- **Header Analysis**: CDN-specific header detection
- **CNAME Analysis**: DNS CNAME record analysis for CDN identification

### SSL/TLS Analysis
- **Certificate Information**: SSL certificate details
- **Protocol Support**: TLS version support
- **Certificate Chain**: Complete certificate validation
- **Security Assessment**: SSL configuration analysis

### Server Analysis
- **Server Headers**: Web server identification
- **Response Analysis**: Detailed HTTP response analysis
- **Error Handling**: Graceful handling of connection failures
- **Timeout Management**: 5-second request timeouts

## Configuration Options
- **Protocol Selection**: Choose HTTP or HTTPS (default: HTTPS)
- **Method Selection**: Select specific HTTP methods to test
- **Multi-select**: Test multiple methods simultaneously
- **Custom Headers**: Support for custom request headers

## Output Features
- **Structured Display**: Clear categorization of information
- **Color Coding**: Visual distinction for different information types
- **Progress Tracking**: Real-time analysis progress
- **Error Reporting**: Clear indication of connection issues
- **Comprehensive**: Complete host intelligence profile

## Use Cases
- **Bug Host Validation**: Verify host suitability for tunneling
- **Infrastructure Analysis**: Understand target environment
- **CDN Detection**: Identify content delivery networks
- **Security Assessment**: Analyze SSL/TLS configurations
- **Method Testing**: Assess supported HTTP methods
"""
    return Panel(
        Markdown(info_text),
        title="[bold blue]HOST INFO[/bold blue]",
        border_style="bold blue",
        expand=True
    )


def show_usage_examples():
    examples_text = """
# 💡 Practical Usage Examples

## Bug Host Discovery Workflow

### Step 1: Initial Discovery
```bash
# Launch BugScanX
bugscanx

# Select [2] SUBFINDER
# Input: target.com
# Output: subdomains.txt (500+ subdomains)
```

### Step 2: Host Validation
```bash  
# Select [1] HOST SCANNER
# Mode: DirectNon302 (excludes redirects)
# Input: subdomains.txt
# Ports: 80,443
# Output: working_hosts.txt (clean bug hosts)
```

### Step 3: Infrastructure Expansion
```bash
# Select [3] IP LOOKUP
# Input: working_hosts.txt
# Output: related_domains.txt (expanded scope)
```

### Step 4: Port Analysis
```bash
# Select [5] PORT SCANNER  
# Input: working_hosts.txt
# Scan: Common tunneling ports
# Output: open_ports.txt
```

## Advanced Techniques

### CIDR Range Hunting
```bash
# Identify target IP ranges
# Select [3] IP LOOKUP with CIDR input
# Input: 192.168.1.0/24
# Discover all hosted domains in range
```

### SSL/SNI Testing
```bash
# Select [1] HOST SCANNER
# Mode: SSL
# Test SNI configurations
# Identify TLS-compatible hosts
```

### Bulk Processing  
```bash
# Use [4] FILE TOOLKIT
# Split large lists for parallel processing
# Merge results from multiple scans
# Deduplicate and clean final output
```

## File Management Examples

### Clean and Organize Results
```bash
# [4] FILE TOOLKIT → [3] Clean File
# Remove invalid entries and duplicates
# Extract only valid domain names
```

### Filter by Criteria
```bash
# [4] FILE TOOLKIT → [5] Filter by TLD
# Keep only .com domains
# Or filter by keywords (cdn, api, etc.)
```
"""
    return Panel(
        Markdown(examples_text),
        title="[bold yellow]Usage Examples[/bold yellow]",
        border_style="bold yellow",
        expand=True
    )


def show_tips_and_tricks():
    tips_text = """
# 🎯 Tips & Best Practices

## Performance Optimization

### Threading Configuration
- **Start small**: Begin with 10-20 threads
- **Scale up**: Increase based on network capacity
- **Monitor**: Watch for timeout increases
- **Balance**: More threads ≠ always faster

### Input File Preparation
- **Clean format**: One host per line
- **Remove duplicates**: Use FILE TOOLKIT deduplication
- **Validate entries**: Remove invalid domains/IPs
- **Sort alphabetically**: Easier progress tracking

## Bug Host Quality Assessment

### DirectNon302 Mode Priority
- **Use first**: Always start with DirectNon302
- **Clean results**: Excludes problematic redirects
- **Tunnel compatibility**: Better for VPN configs
- **Higher success**: More reliable connections

### Port Selection Strategy
- **Start with 80,443**: Most common working ports
- **Test 8080,8443**: Alternative HTTP/HTTPS ports  
- **Try 8888**: Common proxy/tunnel port
- **Custom ports**: Based on target analysis

## Data Management

### Result Organization
```
project/
├── raw_subdomains.txt      # Initial discovery
├── cleaned_hosts.txt       # After DirectNon302 scan
├── working_ports.txt       # Port scan results
├── ssl_hosts.txt          # SSL-compatible hosts
└── final_bughosts.txt     # Curated final list
```

### Regular Maintenance
- **Update lists**: Re-scan periodically
- **Remove dead hosts**: Clean non-responsive entries
- **Validate configurations**: Test tunnel compatibility
- **Backup results**: Save working configurations

## Ethical Usage Guidelines

### Responsible Scanning
- **Permission**: Only scan authorized targets
- **Rate limiting**: Don't overwhelm target servers
- **Respect robots.txt**: Follow website policies
- **Legal compliance**: Adhere to local laws

### Professional Usage
- **Documentation**: Record methodology and findings
- **Reporting**: Provide clear, actionable reports
- **Disclosure**: Responsible vulnerability disclosure
- **Education**: Share knowledge responsibly

## Troubleshooting Common Issues

### No Results Found
- **Check connectivity**: Verify internet connection
- **Increase timeout**: Some hosts respond slowly
- **Try different ports**: Expand port range
- **Verify input format**: Ensure correct file format

### High False Positives
- **Use DirectNon302**: Reduces redirect noise
- **Increase timeout**: Allow more response time
- **Validate manually**: Spot-check random results
- **Cross-reference**: Compare with other tools
"""
    return Panel(
        Markdown(tips_text),
        title="[bold green]Tips & Best Practices[/bold green]",
        border_style="bold green",
        expand=True
    )


def main():
    choice = console.input("""
[1]  Complete Documentation (All sections)
[2]  Quick Overview Only  
[3]  Host Scanner Details
[4]  Subfinder Guide
[5]  Usage Examples & Tips

[bold cyan] your choice (1-5): [/bold cyan]""")

    console.print()
    
    if choice == "1":
        show_detailed_help()
    elif choice == "2":
        console.print(show_overview())
    elif choice == "3":
        console.print(show_host_scanner_help())
    elif choice == "4":
        console.print(show_subfinder_help())
    elif choice == "5":
        console.print(show_usage_examples())
        console.print()
        console.print(show_tips_and_tricks())
    else:
        console.print(show_overview())

    table = Table(title="[bold]Quick Feature Reference[/bold]", border_style="bright_blue")
    table.add_column("Option", style="bold cyan", width=8)
    table.add_column("Feature", style="bold white", width=20)
    table.add_column("Best For", style="green", width=30)
    table.add_column("Input Type", style="yellow", width=15)

    features = [
        ("1", "HOST SCANNER", "Bug host discovery & validation", "Files/CIDR"),
        ("2", "SUBFINDER", "Subdomain enumeration", "Domains/Files"),
        ("3", "IP LOOKUP", "Reverse IP intelligence", "IPs/CIDR"),
        ("4", "FILE TOOLKIT", "Data processing & management", "Text files"),
        ("5", "PORT SCANNER", "Service discovery", "Hosts/IPs"),
        ("6", "DNS RECORDS", "DNS intelligence gathering", "Domains"),
        ("7", "HOST INFO", "Detailed host analysis", "Hosts/URLs"),
        ("8", "HELP", "Documentation & guides", "N/A"),
        ("9", "UPDATE", "Keep tool current", "N/A"),
        ("0", "EXIT", "Quit application", "N/A")
    ]

    for option, feature, best_for, input_type in features:
        table.add_row(option, feature, best_for, input_type)

    console.print()
    console.print(table)
    console.print()
    console.print(
        Panel(
            Text(
                "Thank you for choosing BugScanX! 🚀\n\n"
                "📱 Stay updated with our latest releases and features:\n"
                "🔗 Telegram: https://t.me/BugScanX\n"
                "⭐ GitHub: https://github.com/Ayanrajpoot10/bugscanx\n"
                "📦 PyPI: https://pypi.org/project/bugscan-x/\n\n"
                "💡 Questions? Issues? Contributions welcome!\n"
                "🎯 Happy Bug Hunting!"
            ),
            border_style="bold blue",
            expand=True,
            title="[bold blue]Connect & Support[/bold blue]"
        )
    )
