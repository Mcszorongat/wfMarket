import multiprocessing as mp
import numpy.random as np
import sys
from numpy.random import RandomState
from time import time, sleep

#print("Number of processors: ", mp.cpu_count())
    #>12
# perf
#import time
#start = time.time()
#print("hello")
#end = time.time()
#print(end - start)

def main(argv):
    
    data = get_data()

    print("serial:\t\t\t", end =" ")
    ts1 = time()
    s1results = []
    for row in data:
        s1results.append(howmany_within_range(row, minimum=4, maximum=8))
    print(sum(s1results), "in", time()-ts1, "s")


    # Parallelizing using Pool.apply()
#    tp1 = time()
#    pool1 = mp.Pool(mp.cpu_count())
#    p1results = [pool1.apply(howmany_within_range, args=(row, 4, 8)) for row in data]
#    pool1.close()
#    print(len(p1results), "in", time()-tp1, "s")


    # Parallelizing using Pool.map()
    print("pool.map():\t\t", end =" ")
    tp2 = time()
    pool2 = mp.Pool(mp.cpu_count())
    p2results = pool2.map(howmany_within_range, [row for row in data])
    pool2.close()
    print(sum(p2results), "in", time()-tp2, "s")

    # Parallelizing with Pool.starmap()
    print("pool.starmap():\t\t", end =" ")
    tp3 = time()
    pool3 = mp.Pool(mp.cpu_count())
    p3results = pool3.starmap(howmany_within_range, [(row, 4, 8) for row in data])
    pool3.close()
    print(sum(p3results), "in", time()-tp3, "s")

    # pool.map_async()
    print("pool.map_async():\t", end =" ")
    tp4 = time()
    pool4 = mp.Pool(mp.cpu_count())
    p4results = pool4.map_async(howmany_within_range, [row for row in data])
    pool4.close()
    print(sum(p4results.get()), "in", time()-tp4, "s")

    # pool.starmap_async()
    print("pool.starmap_async()\t", end =" ")
    tp5 = time()
    pool5 = mp.Pool(mp.cpu_count())
    p4results = pool5.starmap_async(howmany_within_range, [(row, 4, 8) for row in data])
    pool5.close()
    print(sum(p4results.get()), "in", time()-tp5, "s")

# Prepare data
def get_data():
    RandomState(100)
    arr = np.randint(0, 10, size=[1000, 5])
    data = arr.tolist()
    print("Data generated")
    return data

def howmany_within_range(row, minimum=4, maximum=8):
    """Returns how many numbers lie within `maximum` and `minimum` in a given `row`"""
    if sum(row) > 35:
        sleep(0.5)
    count = 0
    for n in row:
        if minimum <= n <= maximum:
            count = count + 1
    return count

if __name__ == "__main__":
    main(sys.argv)