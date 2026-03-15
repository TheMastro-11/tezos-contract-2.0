import smartpy as sp

@sp.module
def main():
    import smartpy.stdlib.utils as utils
    
    states: type = sp.variant(
        IDLE=sp.unit,
        REQ=sp.unit
    )
    
    class VaultRosetta(sp.Contract):
        def __init__(self, owner: sp.address, recovery: sp.address, wait_time: sp.nat):
            self.data.owner = owner
            self.data.recovery = recovery
            self.data.wait_time = wait_time
            self.data.receiver = sp.cast(None, sp.option[sp.address])
            self.data.request_time = sp.cast(None, sp.option[sp.nat])
            self.data.amount = sp.mutez(0)
            self.data.state = sp.cast(sp.variant.IDLE(), states)

        @sp.entrypoint
        def receive(self):
            assert sp.amount > sp.mutez(0)

        @sp.entrypoint
        def withdraw(self, receiver: sp.address, amount: sp.nat):
            assert self.data.state == sp.cast(sp.variant.IDLE(), states)
            assert utils.nat_to_mutez(amount) <= sp.balance
            assert sp.sender == self.data.owner
            self.data.request_time = sp.Some(sp.level)
            self.data.amount = utils.nat_to_mutez(amount)
            self.data.receiver = sp.Some(receiver)
            self.data.state = sp.cast(sp.variant.REQ(), states)

        @sp.entrypoint
        def finalize(self):
            assert self.data.state == sp.cast(sp.variant.REQ(), states)
            assert sp.level >= self.data.request_time.unwrap_some() + self.data.wait_time
            assert sp.sender == self.data.owner
            self.data.state = sp.cast(sp.variant.IDLE(), states)
            sp.send(self.data.receiver.unwrap_some(), self.data.amount)

        @sp.entrypoint
        def cancel(self):
            assert self.data.state == sp.cast(sp.variant.REQ(), states)
            assert sp.sender == self.data.recovery
            self.data.state = sp.cast(sp.variant.IDLE(), states)
            
@sp.add_test()
def test():
    sc = sp.test_scenario("VaultRosetta", main)

    owner = sp.test_account("owner")
    recovery = sp.test_account("recovery")
    receiver = sp.test_account("receiver")
    outsider = sp.test_account("outsider")
    wait_time = sp.nat(10)

    vault = main.VaultRosetta(owner.address, recovery.address, wait_time)
    sc += vault

    sc.h1("VaultRosetta scenario")

    sc.h2("Initial storage")
    sc.verify(vault.data.owner == owner.address)
    sc.verify(vault.data.recovery == recovery.address)
    sc.verify(vault.data.wait_time == wait_time)
    sc.verify(vault.data.receiver == None)
    sc.verify(vault.data.request_time == None)
    sc.verify(vault.data.amount == sp.mutez(0))
    sc.verify(vault.data.state == sp.variant.IDLE(sp.unit))
    sc.verify(vault.balance == sp.mutez(0))

    sc.h2("Receive funds")
    vault.receive(_sender=outsider.address, _amount=sp.mutez(0), _valid=False)
    vault.receive(_sender=outsider.address, _amount=sp.mutez(5_000_000))
    sc.verify(vault.balance == sp.mutez(5_000_000))

    sc.h2("Withdraw request")
    vault.withdraw(sp.record(amount=sp.nat(1_000_000), receiver=receiver.address), _sender=outsider.address, _valid=False)
    vault.withdraw(sp.record(amount=sp.nat(6_000_000), receiver=receiver.address), _sender=owner.address, _valid=False)
    vault.withdraw(sp.record(amount=sp.nat(1_000_000), receiver=receiver.address), _sender=owner.address, _level=7)

    sc.verify(vault.data.receiver.unwrap_some() == receiver.address)
    sc.verify(vault.data.request_time.unwrap_some() == sp.nat(7))
    sc.verify(vault.data.amount == sp.mutez(1_000_000))
    sc.verify(vault.data.state == sp.variant.REQ(sp.unit))
    sc.verify(vault.balance == sp.mutez(5_000_000))

    sc.h2("Finalize constraints")
    vault.withdraw(sp.record(amount=sp.nat(1), receiver=receiver.address), _sender=owner.address, _valid=False)
    vault.cancel(_sender=outsider.address, _valid=False)
    vault.finalize(_sender=outsider.address, _level=17, _valid=False)
    vault.finalize(_sender=owner.address, _level=16, _valid=False)

    sc.h2("Recovery cancels request")
    vault.cancel(_sender=recovery.address)
    sc.verify(vault.data.state == sp.variant.IDLE(sp.unit))
    sc.verify(vault.balance == sp.mutez(5_000_000))

    sc.h2("Second withdraw cycle")
    vault.finalize(_sender=owner.address, _level=30, _valid=False)
    vault.cancel(_sender=recovery.address, _valid=False)
    vault.withdraw(sp.record(amount=sp.nat(2_500_000), receiver=receiver.address), _sender=owner.address, _level=20)
    vault.finalize(_sender=owner.address, _level=29, _valid=False)
    vault.finalize(_sender=owner.address, _level=30)

    sc.verify(vault.data.state == sp.variant.IDLE(sp.unit))
    sc.verify(vault.balance == sp.mutez(2_500_000))

    sc.h2("Post-finalize state")
    vault.cancel(_sender=recovery.address, _valid=False)
    vault.finalize(_sender=owner.address, _level=31, _valid=False)
