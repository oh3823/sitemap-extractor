#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import requests
import urllib3

# Constants
TIMEOUT_SECONDS = 15
SITEMAP_NS = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
SEPARATOR_LINE = '*' * 50


def get_proxies_from_env() -> dict[str, str] | None:
    """Retrieve proxy settings from environment variables."""
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

    if http_proxy or https_proxy:
        return {"http": http_proxy, "https": https_proxy}
    return None


def _copy_windows(text: str) -> None:
    """Helper to copy text to clipboard on Windows."""
    try:
        # Windows 'clip' command requires UTF-16
        process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
        process.communicate(input=text.encode('utf-16'))
        print("URLs copied to clipboard.")
    except Exception as e:
        print(f"Failed to copy to clipboard: {e}", file=sys.stderr)


def _copy_posix(text: str) -> None:
    """Helper to copy text to clipboard on POSIX systems."""
    commands = [['pbcopy'],  # macOS
        ['xclip', '-selection', 'clipboard'],  # Linux
        ['xsel', '--clipboard', '--input']  # Linux
    ]

    for cmd in commands:
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            process.communicate(input=text.encode('utf-8'))
            if process.returncode == 0:
                print("URLs copied to clipboard.")
                return
        except (FileNotFoundError, OSError):
            continue

    print("Clipboard copy skipped: 'pbcopy', 'xclip', or 'xsel' tools not found.", file=sys.stderr)


def copy_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard in a cross-platform manner."""
    if os.name == 'nt':
        _copy_windows(text)
    else:
        _copy_posix(text)


def wait_for_exit() -> None:
    """Wait for user input before exiting (only in frozen/EXE mode)."""
    if not getattr(sys, 'frozen', False):
        return

    print("\nPress any key to exit...")
    if os.name == 'nt':
        try:
            import msvcrt
            msvcrt.getch()
        except ImportError:
            input()
    else:
        input()


def normalize_url(target: str) -> str:
    """Ensure the URL has the correct scheme and path."""
    url = target.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if not url.endswith('sitemap.xml'):
        url = url.rstrip('/') + '/sitemap.xml'
    return url


def print_urls(target: str, urls: list[str | None]):
    if urls:
        print(SEPARATOR_LINE)
        for item in urls:
            print(item)
        print(SEPARATOR_LINE)
    print(f"Sitemap of '{target}' successfully extracted ({len(urls)} URLs).")


def fetch_and_parse_sitemap(target: str, include_string: str | None = None) -> list[str] | None:
    """Fetch the sitemap, extract URLs, and filter them if needed."""
    # Suppress insecure request warnings locally within the task
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = normalize_url(target)

    try:
        response = requests.get(url, proxies=get_proxies_from_env(), verify=False, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        urls = [loc.text for loc in root.findall('.//ns:loc', SITEMAP_NS) if loc.text]

        if include_string:
            urls = [u for u in urls if include_string in u]

        print_urls(target, urls)

        return urls

    except Exception as e:
        print(f"Sitemap extraction failed. {e}", file=sys.stderr)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract URLs from a sitemap.xml")
    parser.add_argument("target", nargs='?', help="Target URL or domain")
    parser.add_argument("--include-string", help="Only include URLs containing this string")

    args = parser.parse_args()
    target = args.target
    is_frozen = getattr(sys, 'frozen', False)

    try:
        # Interactive mode logic for frozen executable
        if not target:
            # If arguments were provided but target is missing, show help and exit
            if len(sys.argv) > 1:
                parser.print_help()
                sys.exit(1)

            if is_frozen:
                parser.print_help()
                print("\n" + SEPARATOR_LINE + "\n")
                try:
                    target = input("Enter domain or URL: ").strip()
                except EOFError:
                    pass

                if not target:
                    print("No input provided.")
                    wait_for_exit()
                    sys.exit(1)
            else:
                parser.print_help()
                sys.exit(1)

        # Core logic execution
        extracted_urls = fetch_and_parse_sitemap(target, args.include_string)

        if extracted_urls:
            copy_to_clipboard('\n'.join(extracted_urls))

    finally:
        wait_for_exit()


if __name__ == "__main__":
    main()
