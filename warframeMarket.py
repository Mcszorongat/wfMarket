import re                           # regular expression
import sys                          # system for arguments
from time import time               # for performance monitoring
import urllib.request as request    # for fetching
import multiprocessing as mp        # parallelization


def _init():
    keys = ('platform', 'region', 'status', 'order_type', 'platinum', 'quantity', 'ingame_name')
    n = 7
    return keys, n


def main(argv):

    # call wit 0 arguments --> default is needed
    if len(argv) == 1 and ("warframeMarket.py" in argv[0].split('/') or "warframeMarket.py" in argv[0].split('\\')):
        print("call wit 0 arguments --> default is needed")
        argv = argv + ["bo_prime_handle", "bo_prime_set", "bo_prime_ornament", "ash_prime_set", "ash_prime_systems", "ash_prime_chassis"]
    # call with arguments
    elif len(argv) != 1:
        print("call with 1 argument")

    keys, n = _init()
    t0 = time()
    tables1 = serial_get_prices(argv[1:], keys, n)
    t1 = time()
    tables2 = parallel_get_prices(argv[1:], keys, n)
    t2 = time()

    print(f"========================SERIAL=================  in {t1-t0} seconds\n")
    print(tables1)
    print(f"\n========================PARALLEL=================  in {t2-t1} seconds\n")
    print(tables2)
    print(f"\nThe two tables are the same: {tables1 == tables2} and parallel was {t1-t0-t2+t1} seconds faster")
    return tables1


def get(items, keys = '', n = 0):
    """
    Returns the corresponding sorted 'n' deals in str type
    """
    if n == 0 and keys == '':
        keys, n = _init()
    elif n == 0 and keys != '':
        _, n = _init()
    elif n != 0 and keys == '':
        keys, _ = _init()

    tables = parallel_get_prices(items, keys, n)
    return tables


def find_value(strIn, key):
    """
    Returns a value that stands between 'key": ' and ','
    and strips it from all the '"' vharacters.
    """
    tmp = strIn.partition(key + '": ')[2]
    return tmp[:tmp.find(',')].replace('"', '')


def live_deals(deals, keys):
    """Returns 3 booleans regarding the availablity of the deal"""
    liveDeals = []
    for deal in deals:
        test1 = deal[keys.index('platform')] == 'pc'
        test2 = deal[keys.index('region')] == 'en'
        test3 = deal[keys.index('status')] != 'offline'
        if test1 and test2 and test3:
            deal.remove('pc')
            deal.remove('en')
            if 'ingame' in deal:
                deal.remove('ingame')
            else:
                deal.remove('online')
            liveDeals.append(deal)
    return liveDeals


def fixed_list(listIn, n):
    """Returns a list with a fixed number of elements"""
    if len(listIn) >= n:
        return listIn[:n]
    else:
        return listIn + ['']*(n - len(listIn))


def fixed_sorted_list(liveDeals, n):
    """
    Returns two sorted lists [buys, sells] with length of n
    """
    liveBuys = []
    liveSells = []
    for deal in liveDeals:
        if "buy" in deal:
            liveBuys.append(deal)
        else:
            liveSells.append(deal)

    buyPrices = []
    for deal in liveBuys:
        buyPrices.append([float(x) for x in deal if re.match('^[0-9]{1,3}([.][0]{1})$', x)])
    returnBuys = fixed_list([x for (_, x) in sorted(zip(buyPrices, liveBuys), reverse=True)], n)

    sellPrices = []
    for deal in liveSells:
        sellPrices.append([float(x) for x in deal if re.match('^[0-9]{1,3}([.][0]{1})$', x)])
    returnSells = fixed_list([x for (_, x) in sorted(zip(sellPrices, liveSells))], n)

    return returnBuys, returnSells


def get_prices(item, keys, n):
    """
    Fetches html content regardin 'item' from warframe.market
    
    Args:
        item: ['bo_prime_handle', ...]
        keys: ('platform', 'region', 'status', 'order_type', 'platinum', 'quantity', 'ingame_name', ...
        n:     number of elements to be returned

    Raises:
        ValueError:
            If the given item has no valid URL
    """

    targetURL = f'https://warframe.market/items/{item}'.lower()
    r = request.Request(targetURL, headers={'User-Agent': 'Mozilla/5.0'})
    with request.urlopen(r) as content:
        if content.url.lower() == targetURL:
            htmlContent = str(content.read())                                   # byte to str
        else:
            raise ValueError(f"Invalid url: {targetURL}")

    startBookmark = htmlContent.find(': [{') + 4                            # beginning of deals
    endBookmark = htmlContent.find('}]}, "include":')                       # end of deals
    dealsRaw = htmlContent[startBookmark : endBookmark + 1].split('}, {')   # splitting deals into a list

    table = []
    for deal in dealsRaw:
        table.append([find_value(deal, key) for key in keys])               # getting only the key informations

    liveDeals = live_deals(table, keys)                                     # excludes deals that are offline/other region or platform

    returnBuys, returnSells = fixed_sorted_list(liveDeals, n)

    return  [item, [returnBuys, returnSells]]


def serial_get_prices(items, keys, n):
    if len(items) == 1:
        [_, [buys, sells]] = get_prices(items, keys, n)
        returnTables = [buys, sells]

    elif len(items) >1:
        returnTables = []
        for item in items:
            [_, [buys, sells]] = get_prices(item, keys, n)
            returnTables.append([buys, sells])

    return returnTables


def parallel_get_prices(items, keys, n):
    if len(items) == 1:
        [_, [buys, sells]] = get_prices(items, keys, n)
        returnTables = [buys, sells]
    elif len(items) >1:
        pool = mp.Pool(mp.cpu_count())
        Tables = (pool.starmap(get_prices, [(item, keys, n) for item in items]))
        pool.close()
        tmp = dict()
        for tables in Tables:
            tmp.update({tables[0] : tables[1]})

        returnTables = []
        for key in items:
            returnTables.append(tmp[key])

    return returnTables


if __name__ == "__main__":
    main(sys.argv)

#def save_prices(table, filename, writeMode = 'a'):
#    with open(filename, mode = writeMode + 't', encoding = 'utf8') as f:
#        f.writelines(["  \t".join(str(y)) + '\n' for y in [x for x in table]])