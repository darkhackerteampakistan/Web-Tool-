import socket
import json
import requests
import dns.resolver
from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print
from pyfiglet import Figlet
import os
import time

console = Console()

# =======================
# Banner
# =======================
def banner():
    os.system("clear")
    f = Figlet(font='slant')
    title = f.renderText("WEB TOOL")
    console.print(f"[cyan]{title}[/cyan]")

    console.print(Panel.fit(
        "[bold green]Developer : Md Rifat Islam[/bold green]\n"
        "[yellow]Tool Name : Website Info Tool[/yellow]\n"
        "[cyan]Version : v2.0[/cyan]\n"
        "[magenta]Features : IP | DNS | CDN | STATUS[/magenta]",
        title="[bold red]WELCOME[/bold red]"
    ))

# =======================
# Extract Domain
# =======================
def extract_domain(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    return parsed.netloc

# =======================
# Get Multiple IPs
# =======================
def get_ips(domain):
    try:
        results = socket.getaddrinfo(domain, None)
        ips = list(set([x[4][0] for x in results]))
        return ips
    except Exception as e:
        return [f"Error: {e}"]

# =======================
# Reverse DNS
# =======================
def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Not Found"

# =======================
# DNS Records
# =======================
def dns_records(domain):
    data = {}

    record_types = ["A", "AAAA", "MX", "NS"]

    for record in record_types:
        try:
            answers = dns.resolver.resolve(domain, record)
            data[record] = [str(r) for r in answers]
        except:
            data[record] = ["Not Found"]

    return data

# =======================
# Website Status
# =======================
def website_status(url):
    try:
        r = requests.get(url, timeout=10)
        return f"{r.status_code} ({r.reason})"
    except:
        return "Offline / Unreachable"

# =======================
# CDN Detect
# =======================
def detect_cdn(headers):
    server = headers.get("server", "").lower()

    if "cloudflare" in server:
        return "Cloudflare"
    elif "akamai" in server:
        return "Akamai"
    elif "nginx" in server:
        return "Nginx"
    elif "apache" in server:
        return "Apache"

    return "Unknown"

# =======================
# Save Result
# =======================
def save_result(data):
    filename = "result.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    console.print(f"[green]Saved Successfully:[/green] {filename}")

# =======================
# Scan Website
# =======================
def scan():
    website = Prompt.ask("[bold yellow]Enter Website URL")

    domain = extract_domain(website)

    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    console.print("\n[cyan]Scanning Website...[/cyan]")
    time.sleep(1)

    ips = get_ips(domain)
    dns_data = dns_records(domain)
    status = website_status(website)

    headers = {}
    try:
        headers = requests.get(website, timeout=10).headers
    except:
        pass

    cdn = detect_cdn(headers)

    table = Table(title="Website Information")

    table.add_column("Type", style="cyan")
    table.add_column("Result", style="green")

    table.add_row("Domain", domain)
    table.add_row("Website Status", status)
    table.add_row("CDN", cdn)
    table.add_row("IP Addresses", "\n".join(ips))

    for ip in ips:
        if "Error" not in ip:
            table.add_row(f"Reverse DNS ({ip})", reverse_dns(ip))

    for key, value in dns_data.items():
        table.add_row(f"DNS {key}", "\n".join(value))

    console.print(table)

    save = Prompt.ask("\nSave Result? (y/n)").lower()

    if save == "y":
        result = {
            "domain": domain,
            "status": status,
            "cdn": cdn,
            "ips": ips,
            "dns": dns_data
        }
        save_result(result)

# =======================
# Menu
# =======================
def menu():
    while True:
        banner()

        console.print("""
[1] Scan Website
[2] Exit
        """)

        choice = Prompt.ask("Select Option")

        if choice == "1":
            scan()
            input("\nPress Enter To Continue...")
        elif choice == "2":
            console.print("[red]Goodbye![/red]")
            break
        else:
            console.print("[red]Invalid Option[/red]")
            time.sleep(1)

if __name__ == "__main__":
    menu()
