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

@sp.add_test()
def test():
    sc = sp.test_scenario("HTLCRosetta", main)

    owner = sp.test_account("owner")
    verifier = sp.test_account("verifier")
    outsider = sp.test_account("outsider")
    secret = "Test"
    wrong_secret = "Wrong"
    secret_hash = sp.keccak(sp.pack(secret))
    delay = sp.nat(10)

    # The contract requires an existing balance before reveal can succeed.
    empty_htlc = main.HTLCRosetta(owner.address, verifier.address, secret_hash, delay)
    sc += empty_htlc

    sc.verify(empty_htlc.data.owner == owner.address)
    sc.verify(empty_htlc.data.verifier == verifier.address)
    sc.verify(empty_htlc.data.hash == secret_hash)
    sc.verify(empty_htlc.data.reveal_timeout == sp.nat(10))
    sc.verify(empty_htlc.balance == sp.mutez(0))

    empty_htlc.reveal(secret, _sender=owner.address, _valid=False)

    funded_htlc = main.HTLCRosetta(owner.address, verifier.address, secret_hash, delay)
    funded_htlc.set_initial_balance(sp.mutez(1_000_000))
    sc += funded_htlc

    sc.verify(funded_htlc.data.owner == owner.address)
    sc.verify(funded_htlc.data.verifier == verifier.address)
    sc.verify(funded_htlc.data.hash == secret_hash)
    sc.verify(funded_htlc.data.reveal_timeout == sp.nat(10))
    sc.verify(funded_htlc.balance == sp.mutez(1_000_000))

    funded_htlc.reveal(secret, _sender=outsider.address, _valid=False)
    funded_htlc.reveal(wrong_secret, _sender=owner.address, _valid=False)
    funded_htlc.reveal(secret, _sender=owner.address)

    sc.verify(funded_htlc.balance == sp.mutez(0))
