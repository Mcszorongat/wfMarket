import re                                                                   # regular expression
import sys                                                                  # system for arguments
from time import time                                                       # for performance monitoring
import urllib.request as request                                            # for fetching
import multiprocessing as mp                                                # parallelization


def main(argv):
    # call wit 0 arguments --> default is needed
    if len(argv) == 1 and ("wfMarket.py" in argv[0].split('/') or "wfMarket.py" in argv[0].split('\\')):
        print("call wit 0 arguments --> default is needed")
        argv = argv + ["bo_prime_handle", "bo_prime_set", "bo_prime_ornament", "ash_prime_set", "ash_prime_systems", "ash_prime_chassis"]
    # call with arguments
    elif len(argv) != 1:
        print("call with more argument")

    t0 = time()
    dealsDict1 = serial_get_deals(argv[1:])
    t1 = time()
    dealsDict2 = parallel_get_deals(argv[1:])
    t2 = time()
    
    print(f"========================SERIAL=================  in {t1-t0} seconds\n")
    #print(dealsDict1)
    print(f"\n========================PARALLEL=================  in {t2-t1} seconds\n")
    #print(dealsDict2)
    print(f"\nThe two dicts are the same: {dealsDict1 == dealsDict2} and parallel was {t1-t0-t2+t1} seconds faster")
    return dealsDict2

def _def(keys, m):
    if keys == '':
        keys = ('platform', 'region', 'status', 'order_type', 'platinum', 'ingame_name')
    if m == 0:
        m = 4
    return keys, m


def _crop_content(content, startSTR = ': [{', stopSTR = '}]}, "', splitAt = '}, {'):
    """
    Returns the text between 'startSTR' and 'stopSTR'
    split into a list at 'splitAT'
    """
    startIndex = content.find(startSTR) + len(startSTR)                     # beginning of deals
    stopIndex  = content.find(stopSTR)                                      # end of deals
    return content[startIndex : stopIndex + 1].split(splitAt)               # splitting deals into a list


def _find_value(strIn, key, sep = '": '):
    """
    Returns a value that stands between 'key": ' and ','
    and strips it from all the '"' vharacters.
    eg.:    "platform": "pc" --> pc
    """
    tmp = strIn.partition(key + sep)[2]                                     # takes the text after the 'key' + 'sep'
    return tmp[:tmp.find(',')].replace('"', '')                             # searches for the next ',' and replaces '"'


def _live_deals(deals, keys):
    """
    Returns the deals where:
    platform = pc
    region = en
    status != offline
    without theese tags
    """
    liveDeals = []
    for deal in deals:
        test1 = deal[keys.index('platform')] == 'pc'
        test2 = deal[keys.index('region')] == 'en'
        test3 = deal[keys.index('status')] != 'offline'
        if test1 and test2 and test3:
            liveDeals.append(deal)

    return liveDeals


def sep_sort_m_deals(deals, keys, m):
    """
    Returns two sorted lists [buys, sells] with length of n
    """
    buys = []
    sells = []
    for deal in deals:
        if 'buy' in deal:
            buys.append(deal)
        elif 'sell' in deal:
            sells.append(deal)
        else:
            raise RuntimeError(f"Wrong keys: missing order_type: {deal}")
    
    index = keys.index('platinum')
    returnBuys  = sorted(buys, key=lambda x: float(x[index]), reverse=True)
    returnSells = sorted(sells, key=lambda x: float(x[index]))

    return (returnBuys[:m] if m<len(returnBuys) else returnBuys,
        returnSells[:m] if m<len(returnSells) else returnSells)


def _get_deals(item, keys, m):
    """
    Fetches html content regardin 'item' from warframe.market
    
    Args:
        item: ['bo_prime_handle', ...]
        keys: ('platform', 'region', 'status', ...
        m:     maximum number of elements to be returned per 'order_type'

    Raises:
        ValueError:
            If the given item has no valid URL
    """
    targetURL = f'https://warframe.market/items/{item}'.lower()
    headers_ = {'User-Agent': 'Mozilla/5.0'}
    r = request.Request(targetURL, headers = headers_)
    with request.urlopen(r) as content:
        if content.url.lower() == targetURL:
            pageContent = str(content.read())                               # byte to str
        else:
            raise ValueError(f"Invalid url: {targetURL}")
    
    rawDeals = _crop_content(pageContent, ': [{', '}]}, "', '}, {')         # crop garbage and split the rest

    deals = []
    for deal in rawDeals:
        deals.append([_find_value(deal, key) for key in keys])              # concatenating the key values

    liveDeals = _live_deals(deals, keys)                                    # excluding offline deals

    liveBuys, liveSells = sep_sort_m_deals(liveDeals, keys, m)
    
    return {item : (liveBuys, liveSells)}


def serial_get_deals(items, keys = '', m = 0):
    keys, m = _def(keys, m)                                                 # loads default values if no input
    dealsDict = dict()
    for item in items:
        dealsDict.update(_get_deals(item, keys, m))                         # list of dictionaries with item names as keys

    return dealsDict


def parallel_get_deals(items, keys = '', m = 0):
    keys, m = _def(keys, m)                                                 # loads default values if no input
    if type(items) == 'str':
        dealsDict = _get_deals(items, keys, m)
    elif len(items) == 1:
        dealsDict = _get_deals(items[0], keys, m)
    else:
        pool = mp.Pool(mp.cpu_count())
        dicts = (pool.starmap(_get_deals, [(item, keys, m) for item in items]))
        pool.close()
        dealsDict = dict()
        [dealsDict.update(dct) for dct in dicts]
    return dealsDict

if __name__ == "__main__":
    main(sys.argv)


def _separated_sorted_list(deals, keys):
    """
    Returns two sorted lists [buys, sells] with length of n
    """
    buys = []
    sells = []
    for deal in deals:
        if 'buy' in deal:
            buys.append(deal)
        elif 'sell' in deal:
            sells.append(deal)
        else:
            raise RuntimeError(f"Wrong key set: missing order_type: {deal}")

    buyPrices = []
    for deal in buys:
        buyPrices.append([float(x) for x in deal if re.match('^[0-9]{1,3}([.][0]{1})$', x)])
    returnBuys = [x for (_, x) in sorted(zip(buyPrices, buys), reverse=True)]
    
    sellPrices = []
    for deal in sells:
        sellPrices.append([float(x) for x in deal if re.match('^[0-9]{1,3}([.][0]{1})$', x)])
    returnSells = [x for (_, x) in sorted(zip(sellPrices, sells))]

    return returnBuys, returnSells