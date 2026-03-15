import smartpy as sp

@sp.module
def main():
    class SimpleTransferRosetta(sp.Contract):
        def __init__(self, owner: sp.address, recipient: sp.address):
            self.data.recipient = recipient
            self.data.owner = owner
            
        @sp.entrypoint
        def deposit(self):
            assert sp.sender == self.data.owner
            assert sp.amount > sp.mutez(0)

        @sp.entrypoint
        def withdraw(self, amount: sp.mutez):
            assert sp.sender == self.data.recipient, "only the recipient can withdraw"
            assert amount <= sp.balance, "the contract balance is less then required amount"
            
            sp.send(self.data.recipient, amount)
            
@sp.add_test()
def test():
    sc = sp.test_scenario("SimpleTransferRosetta", main)
    owner = sp.test_account("owner")
    recipient = sp.test_account("recipient")
    outsider = sp.test_account("outsider")

    sc.h1("Main scenario")

    sitr = main.SimpleTransferRosetta(owner.address, recipient.address)
    sc += sitr

    sc.h2("Initial storage")
    sc.verify(sitr.data.owner == owner.address)
    sc.verify(sitr.data.recipient == recipient.address)
    sc.verify(sitr.balance == sp.mutez(0))

    sc.h2("Deposits")
    sitr.deposit(_sender=outsider.address, _amount=sp.mutez(3_000_000), _valid=False)
    sitr.deposit(_sender=owner.address, _amount=sp.mutez(5_000_000))
    sitr.deposit(_sender=owner.address, _amount=sp.mutez(2_000_000))
    sc.verify(sitr.balance == sp.mutez(7_000_000))

    sc.h2("Withdraw access control")
    sitr.withdraw(sp.mutez(1_000_000), _sender=outsider.address, _valid=False)
    sitr.withdraw(sp.mutez(1_000_000), _sender=owner.address, _valid=False)

    sc.h2("Withdraw limits")
    sitr.withdraw(sp.mutez(8_000_000), _sender=recipient.address, _valid=False)
    sc.verify(sitr.balance == sp.mutez(7_000_000))

    sc.h2("Recipient withdrawals")
    sitr.withdraw(sp.mutez(2_000_000), _sender=recipient.address)
    sc.verify(sitr.balance == sp.mutez(5_000_000))

    sitr.withdraw(sp.mutez(5_000_000), _sender=recipient.address)
    sc.verify(sitr.balance == sp.mutez(0))
