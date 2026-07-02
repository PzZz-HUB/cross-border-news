import requests, re
r = requests.get('https://newsroom.tiktok.com/en-us/', headers={'User-Agent': 'Mozilla/5.0'})
matches = re.findall(r'"title":"([^"]+)","url":"([^"]+)"', r.text)
print(len(matches))
