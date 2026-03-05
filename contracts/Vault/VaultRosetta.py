import smartpy as sp

@sp.module
def main():
    class VaultRosetta(sp.Contract):
        def __init__(self, owner, recovery_key, wait_delay):
            self.data.owner = sp.cast(owner, sp.address)
            self.data.recovery_key = sp.cast(recovery_key, sp.address)
            self.data.wait_delay = sp.cast(wait_delay, sp.nat)
            self.data.pending = sp.cast(None, sp.option[sp.record(receiver=sp.address, amount=sp.mutez, unlock=sp.nat)])

        @sp.entrypoint
        def receive(self):
            pass

        @sp.entrypoint
        def withdraw(self, params):
            params = sp.cast(params, sp.record(receiver=sp.address, amount=sp.mutez))
            assert sp.sender == self.data.owner
            assert params.amount <= sp.balance
            unlock = sp.level + self.data.wait_delay
            self.data.pending = sp.Some(sp.record(receiver=params.receiver, amount=params.amount, unlock=unlock))

        @sp.entrypoint
        def finalize(self):
            assert sp.sender == self.data.owner
            assert self.data.pending.is_some()
            p = self.data.pending.unwrap_some()
            assert sp.level >= p.unlock
            self.data.pending = sp.cast(None, sp.option[sp.record(receiver=sp.address, amount=sp.mutez, unlock=sp.nat)])
            sp.send(p.receiver, p.amount)

        @sp.entrypoint
        def cancel(self):
            assert sp.sender == self.data.recovery_key
            assert self.data.pending.is_some()
            p = self.data.pending.unwrap_some()
            assert sp.level < p.unlock
            self.data.pending = sp.cast(None, sp.option[sp.record(receiver=sp.address, amount=sp.mutez, unlock=sp.nat)])
            
@sp.add_test()
def test():
    #set scenario
    sc = sp.test_scenario("VaultRosetta",main)
    #CreateUsers
    owner = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    #create object
    Vault = main.VaultRosetta(owner, owner, 10)
    #start scenario
    sc += Vault