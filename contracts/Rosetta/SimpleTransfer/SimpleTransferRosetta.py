import smartpy as sp

@sp.module
def main():
    class SimpleTransferRosetta(sp.Contract):
        def __init__(self, owner, recipient):
            self.data.owner = owner
            self.data.recipient = recipient

        @sp.entrypoint
        def deposit(self):
            assert sp.sender == self.data.owner

        @sp.entrypoint
        def withdraw(self, amount):
            sp.cast(amount, sp.mutez)
            assert sp.sender == self.data.recipient
            assert amount <= sp.balance
            sp.send(self.data.recipient, amount)
            
@sp.add_test()
def test():
    # set scenario
    sc = sp.test_scenario("SimpleTransferRosetta", main)
    owner = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    recipient = sp.address("tz1aLPm3WynyHRXFvjjdHZDKEjHZVvQMGxqU")
    # create object SimpleTransfer
    sitr = main.SimpleTransferRosetta(owner, recipient)
    # start scenario
    sc += sitr
