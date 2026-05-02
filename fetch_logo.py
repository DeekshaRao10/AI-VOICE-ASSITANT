import urllib.request
import re

try:
    req = urllib.request.Request('https://msrmh.com/', headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    urls = re.findall(r'src="([^"]+logo[^"]*\.png)"', html, re.IGNORECASE)
    print("Found URLs:", urls)
    if urls:
        logo_url = urls[0]
        if logo_url.startswith('/'):
            logo_url = 'https://msrmh.com' + logo_url
        print("Downloading from:", logo_url)
        urllib.request.urlretrieve(logo_url, 'logo.png')
        print("Downloaded successfully!")
except Exception as e:
    print(e)
