import smartpy as sp

@sp.module
def main():
    class HTLCRosetta(sp.Contract):
        def __init__(self, owner: sp.address, v: sp.address, h: sp.bytes, delay: sp.nat):
            self.data.owner = owner
            self.data.verifier = v
            self.data.hash = h
            self.data.reveal_timeout = sp.level + delay

        @sp.entrypoint
        def reveal(self, s: sp.string):
            assert sp.balance - sp.amount >= sp.mutez(1) #check solidity constructor
            
            assert sp.sender == self.data.owner
            assert sp.keccak(sp.pack(s)) == self.data.hash
        
            sp.send(self.data.owner, sp.balance)

        @sp.entrypoint
        def timeout(self):
            assert sp.level >= self.data.reveal_timeout
            sp.send(self.data.owner, sp.balance)
