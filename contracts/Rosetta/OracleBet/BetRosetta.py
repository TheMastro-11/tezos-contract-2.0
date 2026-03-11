import smartpy as sp

@sp.module
def main():
    class BetRosetta(sp.Contract):
        def __init__(self, oracle, timeout):
            self.data.oracle = sp.cast(oracle, sp.address)
            self.data.deadline = sp.cast(timeout, sp.nat)
            self.data.player1 = sp.cast(None, sp.option[sp.address])
            self.data.player2 = sp.cast(None, sp.option[sp.address])
            self.data.stake = sp.mutez(0)
            self.data.winner = sp.cast(None, sp.option[sp.address])
            self.data.closed = False

        @sp.entrypoint
        def join1(self):
            assert self.data.closed == False
            assert sp.level < self.data.deadline
            assert self.data.player1.is_none()
            assert sp.amount > sp.mutez(0)
            self.data.player1 = sp.Some(sp.sender)
            self.data.stake = sp.amount

        @sp.entrypoint
        def join2(self):
            assert self.data.closed == False
            assert sp.level < self.data.deadline
            assert self.data.player1.is_some()
            assert self.data.player2.is_none()
            assert sp.sender != self.data.player1.unwrap_some()
            assert sp.amount == self.data.stake
            self.data.player2 = sp.Some(sp.sender)

        @sp.entrypoint
        def set_winner(self, winner):
            winner = sp.cast(winner, sp.address)
            assert sp.sender == self.data.oracle
            assert self.data.closed == False
            assert self.data.player1.is_some()
            assert self.data.player2.is_some()
            assert winner == self.data.player1.unwrap_some() or (winner == self.data.player2.unwrap_some())
            self.data.winner = sp.Some(winner)

        @sp.entrypoint
        def claim(self):
            assert self.data.closed == False
            assert self.data.winner.is_some()
            assert sp.sender == self.data.winner.unwrap_some()
            self.data.closed = True
            sp.send(sp.sender, sp.balance)

        @sp.entrypoint
        def timeout(self):
            assert self.data.closed == False
            assert sp.level >= self.data.deadline
            assert self.data.winner.is_none()
            assert self.data.player1.is_some()
            assert self.data.player2.is_some()
            p1 = self.data.player1.unwrap_some()
            p2 = self.data.player2.unwrap_some()
            amount = self.data.stake
            self.data.closed = True
            sp.send(p1, amount)
            sp.send(p2, amount)
            
@sp.add_test()
def test():
    #set scenario
    sc = sp.test_scenario("BetRosetta",main)
    #admin
    oracle = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    timeout = sp.nat(10)
    #create object simple wallet
    OracleBet = main.BetRosetta(oracle, timeout)
    #start scenario
    sc += OracleBet