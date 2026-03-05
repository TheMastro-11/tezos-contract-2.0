import smartpy as sp

@sp.module
def main():
    class PriceBetRosetta(sp.Contract):
        def __init__(self, owner, oracle, deadline, bet_rate):
            self.data.owner = sp.cast(owner, sp.address)
            self.data.oracle = sp.cast(oracle, sp.address)
            self.data.deadline = sp.level + sp.cast(deadline, sp.nat)
            self.data.bet_rate = sp.cast(bet_rate, sp.nat)
            self.data.bettor = sp.cast(None, sp.option[sp.address])
            self.data.oracle_rate = sp.cast(None, sp.option[sp.nat])
            self.data.closed = False

        @sp.entrypoint
        def join(self):
            assert self.data.closed == False
            assert sp.level < self.data.deadline
            assert self.data.bettor.is_none()
            assert sp.amount == sp.balance - sp.amount
            self.data.bettor = sp.Some(sp.sender)

        @sp.entrypoint
        def set_rate(self, rate):
            rate = sp.cast(rate, sp.nat)
            assert sp.sender == self.data.oracle
            assert self.data.closed == False
            self.data.oracle_rate = sp.Some(rate)

        @sp.entrypoint
        def win(self):
            assert self.data.closed == False
            assert sp.level < self.data.deadline
            assert self.data.bettor.is_some()
            assert sp.sender == self.data.bettor.unwrap_some()
            assert self.data.oracle_rate.is_some()
            assert self.data.oracle_rate.unwrap_some() > self.data.bet_rate
            self.data.closed = True
            sp.send(sp.sender, sp.balance)

        @sp.entrypoint
        def timeout(self):
            assert self.data.closed == False
            assert sp.level >= self.data.deadline
            assert sp.sender == self.data.owner
            self.data.closed = True
            sp.send(self.data.owner, sp.balance)
            
    class Oracle(sp.Contract):
        def __init__(self):
            self.data.exchangeRate = sp.mutez(10)
            
        @sp.entrypoint
        def getPrice(self, callBack):
            #callBack
            contract = sp.contract(sp.mutez, callBack , "setter").unwrap_some(error="ContractNotFound")
            sp.transfer(self.data.exchangeRate, sp.tez(0),contract) 
            
@sp.add_test()
def test():
    # set scenario
    sc = sp.test_scenario("PriceBetRosetta", main)
    admin = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    # create object
    oracle = main.Oracle()
    priceBet = main.PriceBetRosetta(admin, oracle.address, sp.nat(10), sp.nat(10))
    # start scenario
    sc += priceBet