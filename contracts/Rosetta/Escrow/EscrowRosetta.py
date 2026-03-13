import smartpy as sp

@sp.module
def main():
    states: type = sp.variant(
        WAIT_DEPOSIT=sp.unit,
        WAIT_RECIPIENT=sp.unit,
        CLOSED=sp.unit)
    
    class EscrowRosetta(sp.Contract):
        def __init__(self, amount: sp.mutez, buyer: sp.address, seller: sp.address):
            self.data.buyer = buyer
            self.data.seller = seller
            self.data.amount = amount
            self.data.state = sp.cast(sp.variant.WAIT_DEPOSIT(), states)
        
        @sp.entrypoint
        def deposit(self):
            assert sp.sender == self.data.buyer, "Only the buyer"
            assert self.data.state == sp.cast(sp.variant.WAIT_DEPOSIT(), states), "Invalid State"
            assert sp.amount == self.data.amount, "Invalid amount"
            self.data.state = sp.cast(sp.variant.WAIT_RECIPIENT(), states)

        @sp.entrypoint
        def pay(self):
            assert sp.sender == self.data.buyer, "Only the buyer"
            assert self.data.state == sp.cast(sp.variant.WAIT_RECIPIENT(), states), "Invalid State"
            self.data.state = sp.cast(sp.variant.CLOSED(), states)
            
            sp.send(self.data.seller, self.data.amount)

        @sp.entrypoint
        def refund(self):
            assert sp.sender == self.data.seller, "Only the seller"
            assert self.data.state == sp.cast(sp.variant.WAIT_RECIPIENT(), states), "Invalid State"
            self.data.state = sp.cast(sp.variant.CLOSED(), states)
            
            sp.send(self.data.buyer, self.data.amount)


@sp.add_test()
def test():
    sc = sp.test_scenario("EscrowRosetta")

    seller = sp.test_account("seller")
    buyer = sp.test_account("buyer")
    outsider = sp.test_account("outsider")
    amount = sp.mutez(1000)

    # Happy path: buyer deposits and then releases the funds to the seller.
    escrow_pay = main.EscrowRosetta(amount, buyer.address, seller.address)
    sc += escrow_pay

    sc.verify(escrow_pay.data.buyer == buyer.address)
    sc.verify(escrow_pay.data.seller == seller.address)
    sc.verify(escrow_pay.data.amount == amount)
    sc.verify(escrow_pay.data.state == sp.variant.WAIT_DEPOSIT(sp.unit))
    sc.verify(escrow_pay.balance == sp.mutez(0))

    escrow_pay.pay(_sender=buyer.address, _valid=False)
    escrow_pay.refund(_sender=seller.address, _valid=False)
    escrow_pay.deposit(_sender=outsider.address, _amount=amount, _valid=False)
    escrow_pay.deposit(_sender=buyer.address, _amount=sp.mutez(999), _valid=False)
    escrow_pay.deposit(_sender=buyer.address, _amount=amount)

    sc.verify(escrow_pay.data.state == sp.variant.WAIT_RECIPIENT(sp.unit))
    sc.verify(escrow_pay.balance == amount)

    escrow_pay.deposit(_sender=buyer.address, _amount=amount, _valid=False)
    escrow_pay.pay(_sender=outsider.address, _valid=False)
    escrow_pay.refund(_sender=buyer.address, _valid=False)
    escrow_pay.pay(_sender=buyer.address)

    sc.verify(escrow_pay.data.state == sp.variant.CLOSED(sp.unit))
    sc.verify(escrow_pay.balance == sp.mutez(0))

    escrow_pay.pay(_sender=buyer.address, _valid=False)
    escrow_pay.refund(_sender=seller.address, _valid=False)

    # Refund path: seller returns the escrowed funds to the buyer.
    escrow_refund = main.EscrowRosetta(amount, buyer.address, seller.address)
    sc += escrow_refund

    escrow_refund.deposit(_sender=buyer.address, _amount=amount)
    sc.verify(escrow_refund.data.state == sp.variant.WAIT_RECIPIENT(sp.unit))
    sc.verify(escrow_refund.balance == amount)

    escrow_refund.refund(_sender=outsider.address, _valid=False)
    escrow_refund.refund(_sender=seller.address)

    sc.verify(escrow_refund.data.state == sp.variant.CLOSED(sp.unit))
    sc.verify(escrow_refund.balance == sp.mutez(0))

    escrow_refund.pay(_sender=buyer.address, _valid=False)
    escrow_refund.refund(_sender=seller.address, _valid=False)
