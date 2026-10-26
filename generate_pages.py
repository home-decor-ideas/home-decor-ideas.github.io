import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

# Default sitemap or argument
sitemap_url = sys.argv[1] if len(sys.argv) > 1 else "https://stylesdays.com/sitemap_index.xml"

print(f"Fetching sitemap from: {sitemap_url}")

def fetch_xml(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_sitemap(url, found_urls=None):
    if found_urls is None:
        found_urls = set()
    
    xml_data = fetch_xml(url)
    if not xml_data:
        return found_urls

    try:
        root = ET.fromstring(xml_data)
        # Handle namespaces in XML sitemaps
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Check if it's a sitemap index (contains other sitemaps)
        sitemaps = root.findall('ns:sitemap', namespace)
        if sitemaps:
            for sm in sitemaps:
                loc = sm.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    print(f"Found sub-sitemap: {loc.text}")
                    parse_sitemap(loc.text, found_urls)
        else:
            # It's a URL set
            urls = root.findall('ns:url', namespace)
            for u in urls:
                loc = u.find('ns:loc', namespace)
                if loc is not None and loc.text:
                    found_urls.add(loc.text.strip())
    except Exception as e:
        print(f"Error parsing XML for {url}: {e}")

    return found_urls

# Gather all article URLs
all_urls = parse_sitemap(sitemap_url)
print(f"Total unique URLs found: {len(all_urls)}")

# HTML Template for generated static pages
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | StylesDays</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical_url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:type" content="article">
  <style>
    :root {{ --primary: #e60023; --bg: #fdfdfd; --text: #111; --gray: #666; --border: #e1e4e8; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 0; }}
    header {{ background: #fff; border-bottom: 1px solid var(--border); padding: 16px 24px; display: flex; justify-content: space-between; align-items: center; }}
    .logo {{ font-weight: 800; font-size: 20px; color: var(--primary); text-decoration: none; }}
    .container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
    .card {{ background: #fff; border: 1px solid var(--border); border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }}
    h1 {{ font-size: 32px; margin-top: 0; letter-spacing: -0.5px; }}
    .meta {{ font-size: 14px; color: var(--gray); margin-bottom: 24px; }}
    .btn {{ display: inline-block; background: var(--primary); color: #fff; padding: 14px 28px; border-radius: 30px; font-weight: 600; text-decoration: none; margin-top: 20px; transition: opacity 0.2s; }}
    .btn:hover {{ opacity: 0.9; }}
    footer {{ text-align: center; margin-top: 60px; font-size: 13px; color: var(--gray); padding-bottom: 40px; }}
  </style>
</head>
<body>
  <header>
    <a href="/" class="logo">StylesDays Curation</a>
    <span style="font-size: 13px; color: var(--gray);">Verified Guide</span>
  </header>
  <div class="container">
    <div class="card">
      <div class="meta">Published on StylesDays &bull; 100% Verified Resource</div>
      <h1>{title}</h1>
      <p>{description}</p>
      <hr style="border:0; border-top:1px solid var(--border); margin:24px 0;">
      <p>Read the complete guide, view high-res imagery, and explore full step-by-step details directly on the official publisher site.</p>
      <a href="{canonical_url}" class="btn" rel="noopener">Continue to Full Article on StylesDays &rarr;</a>
    </div>
  </div>
  <footer>
    &copy; 2026 StylesDays Partnership Hub. All rights reserved.
  </footer>
</body>
</html>
"""

# Generate pages for each URL
for url in all_urls:
    if not url.endswith('/'):
        url += '/'
    
    # Extract slug from URL (e.g. https://stylesdays.com/minimalist-bedroom-ideas/ -> minimalist-bedroom-ideas)
    parts = [p for p in url.split('/') if p]
    if len(parts) <= 1:
        continue
    slug = parts[-1]
    
    # Format title from slug
    title = slug.replace('-', ' ').title()
    description = f"Explore {title}. Discover expert tips, ideas, and complete inspiration guides on StylesDays."
    
    # Create directory structure for clean URLs: /slug/index.html
    os.makedirs(slug, exist_ok=True)
    file_path = os.path.join(slug, 'index.html')
    
    page_content = HTML_TEMPLATE.format(
        title=title,
        description=description,
        canonical_url=url
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(page_content)
    
    print(f"Generated: /{slug}/index.html -> {url}")

print("All pages successfully generated!")
