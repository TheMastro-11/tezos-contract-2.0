import smartpy as sp

@sp.module
def main():
    class HTLCRosetta(sp.Contract):
        def __init__(self, committer, receiver, hash, delay):
            self.data.committer = sp.cast(committer, sp.address)
            self.data.receiver = sp.cast(receiver, sp.address)
            self.data.hash = sp.cast(hash, sp.bytes)
            self.data.deadline = sp.level + sp.cast(delay, sp.nat)
            self.data.completed = False

        @sp.entrypoint
        def reveal(self, word):
            word = sp.cast(word, sp.string)
            assert self.data.completed == False
            computed = sp.keccak(sp.pack(word))
            assert computed == self.data.hash
            self.data.completed = True
            sp.send(self.data.committer, sp.balance)

        @sp.entrypoint
        def timeout(self):
            assert self.data.completed == False
            assert sp.level >= self.data.deadline
            assert sp.sender == self.data.receiver
            self.data.completed = True
            sp.send(self.data.receiver, sp.balance)

@sp.add_test()
def test():
    # set scenario
    sc = sp.test_scenario("HTLCRosetta", main)
    committer = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    receiver = sp.address("tz1aLPm3WynyHRXFvjjdHZDKEjHZVvQMGxqU")
    bytes = sp.pack("Test")
    hash = sp.keccak(bytes)
    delay = sp.nat(10)
    # create object HashTimedLockedContract
    htlc = main.HTLCRosetta(committer, receiver, hash, delay)
    # start scenario
    sc += htlc