import os
import sys
import xml.etree.ElementTree as ET

import requests
import urllib3


def get_proxies_from_env():
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')

    if http_proxy or https_proxy:
        return {"http": http_proxy, "https": https_proxy}
    return None


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extract_urls_with_proxy(input_target):
    url = input_target
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if not url.endswith('sitemap.xml'):
        url = url.rstrip('/') + '/sitemap.xml'

    try:
        response = requests.get(url, proxies=get_proxies_from_env(), verify=False, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = [loc.text for loc in root.findall('.//ns:loc', ns)]

        print('*' * 50)
        for item in urls:
            print(item)

        print('*' * 50)
        print(f"sitemap of {input_target} successfully extracted.")

    except Exception as e:
        print(f"sitemap extraction failed. {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: sitemap_extractor <url or domain>")
        print("  ex > sitemap_extractor https://www.example.com")
        print("  ex > sitemap_extractor example.com")
        sys.exit(1)

    extract_urls_with_proxy(sys.argv[1])
