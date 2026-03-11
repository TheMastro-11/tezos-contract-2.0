import smartpy as sp

@sp.module
def main():
    class EscrowRosetta(sp.Contract):
        def __init__(self, seller, buyer, amount):
            self.data.seller = sp.cast(seller, sp.address)
            self.data.buyer = sp.cast(buyer, sp.address)
            self.data.amount = sp.cast(amount, sp.mutez)
            self.data.funded = False
            self.data.closed = False

        @sp.entrypoint
        def deposit(self):
            assert self.data.closed == False
            assert self.data.funded == False
            assert sp.sender == self.data.buyer
            assert sp.amount == self.data.amount
            self.data.funded = True

        @sp.entrypoint
        def pay(self):
            assert self.data.closed == False
            assert self.data.funded == True
            assert sp.sender == self.data.buyer
            assert sp.balance == self.data.amount
            self.data.closed = True
            sp.send(self.data.seller, self.data.amount)

        @sp.entrypoint
        def refund(self):
            assert self.data.closed == False
            assert self.data.funded == True
            assert sp.sender == self.data.seller
            assert sp.balance == self.data.amount
            self.data.closed = True
            sp.send(self.data.buyer, self.data.amount)


@sp.add_test()
def test():
    #set scenario
    sc = sp.test_scenario("EscrowRosetta",main)
    #create admin
    seller = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    #create users
    buyer = sp.address("tz1aLPm3WynyHRXFvjjdHZDKEjHZVvQMGxqU")
    #create object
    Escrow = main.EscrowRosetta(seller,buyer, sp.mutez(1000))
    #start scenario
    sc += Escrow