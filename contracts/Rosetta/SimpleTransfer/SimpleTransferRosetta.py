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
