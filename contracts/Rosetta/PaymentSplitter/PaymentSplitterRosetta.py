import smartpy as sp

@sp.module
def main():
    class PaymentSplitterRosetta(sp.Contract):
        def __init__(self, shares):
            self.data.shares = sp.cast(shares, sp.map[sp.address, sp.nat])
            total = sp.nat(0)
            for k in self.data.shares.keys():
                total += self.data.shares[k]
            self.data.total_shares = total
            self.data.released = sp.cast({}, sp.map[sp.address, sp.mutez])
            self.data.total_released = sp.mutez(0)

        @sp.entrypoint
        def receive(self):
            pass

        @sp.entrypoint
        def release(self, payee):
            payee = sp.cast(payee, sp.address)
            assert sp.sender == payee
            assert self.data.shares.contains(payee)
            assert self.data.total_shares > 0

            already = self.data.released[payee]
            total_received = sp.balance + self.data.total_released
            entitlement = sp.split_tokens(total_received, self.data.shares[payee], self.data.total_shares)
            amount = entitlement - already
            assert amount > sp.mutez(0)

            self.data.released[payee] = already + amount
            self.data.total_released += amount
            sp.send(payee, amount)
            
@sp.add_test()
def test():
    # set scenario
    sc = sp.test_scenario("PaymentSplitterRosetta", main)
    admin = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    mario = sp.address("tz1aLPm3WynyHRXFvjjdHZDKEjHZVvQMGxqU")
    shares = { admin : sp.nat(80), mario : sp.nat(20)}
    # create object
    paymentSplitter = main.PaymentSplitterRosetta(shares)
    # start scenario
    sc += paymentSplitter