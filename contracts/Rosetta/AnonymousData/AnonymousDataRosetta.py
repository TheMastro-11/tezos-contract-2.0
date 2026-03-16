import smartpy as sp

@sp.module
def main():
    class AnonymousDataRosetta(sp.Contract):
        def __init__(self):
            self.data.storedData = sp.cast(sp.big_map(), sp.big_map[sp.bytes, sp.bytes])

        @sp.entrypoint
        def store_data(self, params):
            data = sp.cast(params.data, sp.bytes)
            id = sp.cast(params.id, sp.bytes)
            assert not self.data.storedData.contains(id)
            self.data.storedData[id] = data

        @sp.onchain_view
        def getID(self, nonce):
            nonce = sp.cast(nonce, sp.nat)
            return sp.keccak(sp.pack((sp.sender, nonce)))

        @sp.onchain_view
        def getMyData(self, nonce):
            nonce = sp.cast(nonce, sp.nat)
            id = sp.keccak(sp.pack((sp.sender, nonce)))
            assert self.data.storedData.contains(id)
            return self.data.storedData[id]
