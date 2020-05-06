class itemPiece:
    def __init__(self, name):
        self._name = name.lower().replace(' ', '_')
        self._pieces = self._name
    
    def get_name(self):
        return self._name


class itemSet(itemPiece):
    def __init__(self, nameType):
        self._name = f"{nameType[0].lower().replace(' ', '_')}_set"
        self._type = nameType[1]
        self._pieces = [f"{self._name[:-4]}_{item}" for item in self._get_components(self._type)]

    def _get_components(self, itemType):
        componentDict = {
            'warframe'  : ['blueprint1', 'chassis1', 'neuroptics1', 'systems1'],
            # primary
            'rifle'     : ['blueprint1', 'barrel1', 'receiver1', 'stock1'],
            'bow'       : ['blueprint1', 'upper_limb1', 'lower_limb1', 'grip1', 'string1'],
            # secondary
            'pistol'    : ['blueprint1', 'barrel1', 'receiver1'],
            # melee
            'polearm'   : ['blueprint1', 'blade2', 'handle1'],
            'staff'     : ['blueprint1', 'handle1', 'ornament2']}
        return componentDict[itemType]

    def get_pieces(self, flag = False):
        if flag:
            return [i[:-1] for i in self._pieces], [i[-1] for i in self._pieces]
        else:
            return [i[:-1] for i in self._pieces]


if __name__ == "__main__":
    print("main is running")
    a = itemSet(("Ash Prime", 'warframe'))
    print(a.get_name())
    print(a.get_pieces())