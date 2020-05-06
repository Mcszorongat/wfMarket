import sys
from warframeItems import itemPiece, itemSet
from wfMarket import parallel_get_deals
from wfMarket import main as mn

def main(argv):
    fNames = ['Ash', 'Atlas', 'Banshee', 'Chroma', 'Ember', 'Equinox']
    warframes = [(f"{item}_Prime", 'warframe') for item in fNames]

    frameSets = [itemSet(wf) for wf in warframes]
    
    wfPieces = [piece for iSet in frameSets for piece in iSet.get_pieces()]

    dealsDict = parallel_get_deals(wfPieces)
    
    for key in dealsDict:
        print(key)
        print('buy')
        print(dealsDict[key][0])
        print('sell')
        print(dealsDict[key][1])
        print(' ')


if __name__ == "__main__":
    main(sys.argv)