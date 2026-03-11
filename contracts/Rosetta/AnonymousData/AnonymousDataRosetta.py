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
        
@sp.add_test()
def test():
    sc = sp.test_scenario("AnonymousDataRosetta")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    c1 = main.AnonymousDataRosetta()
    sc += c1

    alice_nonce = sp.nat(1)
    bob_nonce = sp.nat(2)
    alice_data = sp.bytes("0x1234")
    bob_data = sp.bytes("0xabcd")

    alice_id = sp.keccak(sp.pack((alice.address, alice_nonce)))
    bob_id = sp.keccak(sp.pack((bob.address, bob_nonce)))

    sc.verify(alice_id != bob_id)

    c1.store_data(data=alice_data, id=alice_id, _sender=alice.address)
    c1.store_data(data=bob_data, id=bob_id, _sender=bob.address)
    c1.store_data(data=alice_data, id=alice_id, _sender=alice.address, _valid=False)

    sc.verify(c1.data.storedData[alice_id] == alice_data)
    sc.verify(c1.data.storedData[bob_id] == bob_data)
