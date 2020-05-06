from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
req = Request("https://warframe.market/items/asdasd", headers={'User-Agent': 'Mozilla/5.0'})
try:
    response = urlopen(req)
except HTTPError as e:
    print('The server couldn\'t fulfill the request.')
    print('Error code: ', e.code)
except URLError as e:
    print('We failed to reach a server.')
    print('Reason: ', e.reason)
    # everything is fine
print("Over")