import smartpy as sp

@sp.module
def main():
    class AnonymousDataRosetta(sp.Contract):
        def __init__(self):
            self.data.storedData = sp.cast({}, sp.big_map[sp.nat, sp.bytes])
        
        @sp.onchain_view
        def getID(self, nonce):
            return sp.keccak(sp.pack(sp.sender))

        @sp.entrypoint
        def storeData(self, data, id):
            self.data.storedData[id] = sp.cast(data, sp.bytes)
            
        @sp.onchain_view
        def getMyData(self, nonce):
            return self.data.storedData.get(sp.keccak(sp.pack(sp.sender)))
        
sp.add_test()
def test():
    # set scenario
    sc = sp.test_scenario("AnonymousDataRosetta", main)
    c1 = main.AnonymousDataRosetta()
    sc += c1