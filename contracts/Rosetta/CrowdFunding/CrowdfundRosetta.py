import smartpy as sp

@sp.module
def main():
    class CrowdfundRosetta(sp.Contract):
        def __init__(self, receiver, end_donate, goal):
            self.data.end_donate = sp.cast(end_donate, sp.nat)
            self.data.goal = sp.cast(goal, sp.mutez)
            self.data.receiver = sp.cast(receiver, sp.address)
            self.data.donors = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.mutez])

        @sp.entrypoint
        def donate(self):
            assert sp.level < self.data.end_donate
            self.data.donors[sp.sender] += sp.amount
            
        @sp.entrypoint
        def withdraw(self):
            assert sp.level >= self.data.end_donate
            assert sp.balance >= self.data.goal
            
            sp.send(self.data.receiver, sp.balance)

        @sp.entrypoint
        def reclaim(self):
            assert sp.level >= self.data.end_donate
            assert sp.balance < self.data.goal
            assert self.data.donors[sp.sender] > sp.mutez(0)
            amount = self.data.donors[sp.sender]
            self.data.donors[sp.sender] = sp.mutez(0)
            
            sp.send(sp.sender, amount)

@sp.add_test()
def test():
    sc = sp.test_scenario("CrowdfundRosetta")

    recipient = sp.test_account("recipient")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")

    # Successful campaign: the receiver can withdraw after the deadline
    successful = main.CrowdfundRosetta(recipient.address, sp.nat(10), sp.mutez(100))
    successful.data.donors = sp.big_map({
        alice.address: sp.mutez(0),
        bob.address: sp.mutez(0),
    })
    sc += successful

    successful.withdraw(_sender=recipient.address, _level=5, _valid=False)
    successful.donate(_sender=alice.address, _amount=sp.mutez(40), _level=1)
    successful.donate(_sender=bob.address, _amount=sp.mutez(60), _level=2)

    sc.verify(successful.data.donors[alice.address] == sp.mutez(40))
    sc.verify(successful.data.donors[bob.address] == sp.mutez(60))
    sc.verify(successful.balance == sp.mutez(100))

    successful.donate(_sender=alice.address, _amount=sp.mutez(1), _level=10, _valid=False)
    successful.reclaim(_sender=alice.address, _level=11, _valid=False)
    successful.withdraw(_sender=recipient.address, _level=11)

    sc.verify(successful.balance == sp.mutez(0))

    # Failed campaign: donors can reclaim their funds after the deadline
    failed = main.CrowdfundRosetta(recipient.address, sp.nat(20), sp.mutez(200))
    failed.data.donors = sp.big_map({
        alice.address: sp.mutez(0),
        bob.address: sp.mutez(0),
    })
    sc += failed

    failed.donate(_sender=alice.address, _amount=sp.mutez(50), _level=12)
    failed.donate(_sender=bob.address, _amount=sp.mutez(70), _level=13)

    sc.verify(failed.balance == sp.mutez(120))

    failed.withdraw(_sender=recipient.address, _level=21, _valid=False)
    failed.reclaim(_sender=alice.address, _level=19, _valid=False)
    failed.reclaim(_sender=alice.address, _level=21)

    sc.verify(failed.data.donors[alice.address] == sp.mutez(0))
    sc.verify(failed.balance == sp.mutez(70))

    failed.reclaim(_sender=alice.address, _level=22, _valid=False)
    failed.reclaim(_sender=bob.address, _level=22)

    sc.verify(failed.data.donors[bob.address] == sp.mutez(0))
    sc.verify(failed.balance == sp.mutez(0))
