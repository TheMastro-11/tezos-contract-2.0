import smartpy as sp


@sp.module
def main():
    import smartpy.stdlib.utils as utils
    
    class PaymentSplitterRosetta(sp.Contract):
        def __init__(self, shares: sp.list[sp.nat], payees: sp.list[sp.address]):
            payees_len = sp.len(payees)
            assert payees_len == sp.len(shares), "PaymentSplitter: payees and shares length mismatch"
            assert payees_len > 0, "PaymentSplitter: no payees"
            
            self.data.total_shares = sp.nat(0)
            self.data.total_released = sp.mutez(0)
            self.data.shares = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.nat])
            self.data.released = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.mutez])
            self.data.payees = payees

            counter_p = 0
            counter_s= 0
            done = False
            for payee in payees:
                done = False
                counter_s = 0
                for share in shares:
                    if not done:
                        for i in range(payees_len):
                            if i == counter_s and i == counter_p:
                                assert payee != sp.address("0"), "PaymentSplitter: account is the zero address"
                                assert share > 0, "PaymentSplitter: shares are 0"
                                assert not self.data.shares.contains(payee), "PaymentSplitter: account already has shares"
                                
                                self.data.shares[payee] = share
                                self.data.total_shares += share

                                done = True

                        counter_s += 1
                counter_p += 1
            
        @sp.entrypoint
        def receive(self):
            assert sp.amount > sp.mutez(0)
        
        @sp.offchain_view()
        def total_shares(self):
            return self.data.total_shares
        
        @sp.offchain_view()
        def total_released(self):
            return self.data.total_released
        
        @sp.offchain_view()
        def shares(self, account: sp.address):
            return self.data.shares[account]
        
        @sp.offchain_view()
        def released(self, account: sp.address):
            return self.data.released[account]
        
        @sp.offchain_view()
        def payee(self, index: sp.nat):
            response = sp.cast(None, sp.option[sp.address])
            counter = 0
            for payee in self.data.payees:
                if counter == index:
                    response = sp.Some(payee)
                counter += 1
            return response.unwrap_some()

        @sp.offchain_view()
        def releasable(self, account: sp.address):
            total_received = sp.balance + self.data.total_released
            return (utils.mutez_to_nat(total_received) * self.data.shares[account]) / self.data.total_shares - utils.mutez_to_nat(self.data.total_released)
        
        @sp.entrypoint
        def release(self, account: sp.address):
            assert self.data.shares[account] > sp.nat(0), "PaymentSplitter: account has no shares"
            total_received = utils.mutez_to_nat(sp.balance + self.data.total_released)
            num = total_received * self.data.shares[account]
            div = self.data.total_shares - utils.mutez_to_nat(self.data.total_released)
            payment = sp.fst(sp.ediv(num, sp.as_nat(div)).unwrap_some())
            assert payment != 0, "PaymentSplitter: account is not due payment"
            
            self.data.total_released += utils.nat_to_mutez(payment)
            
            sp.send(account, utils.nat_to_mutez(payment))
        
            
            
@sp.add_test()
def test():
    sc = sp.test_scenario("PaymentSplitterRosetta", main)

    admin = sp.test_account("admin")
    mario = sp.test_account("mario")
    luca = sp.test_account("luca")
    outsider = sp.test_account("outsider")

    payees = [
        admin.address,
        mario.address,
        luca.address,
    ]
    shares = [
        sp.nat(50),
        sp.nat(30),
        sp.nat(20),
    ]

    sc.h1("Main scenario")

    
    payment_splitter = main.PaymentSplitterRosetta(shares, payees)
    sc += payment_splitter

    sc.h2("Initial storage")
    sc.verify(payment_splitter.data.total_shares == sp.nat(100))
    sc.verify(payment_splitter.data.total_released == sp.mutez(0))
    sc.verify(payment_splitter.payee(sp.nat(0)) == admin.address)
    sc.verify(payment_splitter.payee(sp.nat(1)) == mario.address)
    sc.verify(payment_splitter.payee(sp.nat(2)) == luca.address)
    sc.verify(payment_splitter.data.shares[admin.address] == sp.nat(50))
    sc.verify(payment_splitter.data.shares[mario.address] == sp.nat(30))
    sc.verify(payment_splitter.data.shares[luca.address] == sp.nat(20))

    sc.h2("Receiving funds")
    payment_splitter.receive(_sender=outsider.address, _amount=sp.mutez(10))
    sc.verify(payment_splitter.balance == sp.mutez(10))

    sc.h2("Release flow")
    payment_splitter.release(admin.address, _sender=admin.address)
    payment_splitter.release(mario.address, _sender=mario.address)
    payment_splitter.release(luca.address, _sender=luca.address)

    sc.h2("No payment for non-payee")
    payment_splitter.release(outsider.address, _sender=outsider.address, _valid=False)
    
