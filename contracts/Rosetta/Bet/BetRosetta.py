import smartpy as sp

@sp.module
def main():
    class BetRosetta(sp.Contract):
        def __init__(self, player1, oracle, timeout, wager):
            self.data.player1 = sp.cast(player1, sp.address)
            self.data.player2 = sp.cast(None, sp.option[sp.address])
            self.data.deadline = sp.level + timeout
            self.data.oracle = sp.cast(oracle, sp.address)
            self.data.wager = sp.cast(wager, sp.mutez)

        @sp.entrypoint
        def join(self):
            assert sp.amount == self.data.wager, "Invalid Value"
            assert self.data.player2.is_none(), "Player2 already joined"
            assert sp.level < self.data.deadline, "Timeout"
        
            self.data.player2 = sp.Some(sp.sender)

        @sp.entrypoint
        def win(self, winner: sp.nat):
            assert sp.sender == self.data.oracle, "Only the oracle"
            assert self.data.player2.is_some(), "Player2 has not joined"
            assert winner <= 1, "Invalid winner"

            addressWinner = sp.cast(None, sp.option[sp.address])

            if (winner == 0):
                addressWinner = sp.Some(self.data.player1)
            else:
                addressWinner = self.data.player2
                
            sp.send(addressWinner.unwrap_some(), sp.balance)

        @sp.entrypoint
        def timeout(self):
            assert sp.level >= self.data.deadline, "The timeout has not passed"
            sp.send(self.data.player1, self.data.wager)

            if (self.data.player2.is_some()):
                sp.send(self.data.player2.unwrap_some(), self.data.wager)
            
@sp.add_test()
def test():
    sc = sp.test_scenario("BetRosetta")

    player1 = sp.test_account("player1")
    player2 = sp.test_account("player2")
    player3 = sp.test_account("player3")
    oracle = sp.test_account("oracle")
    outsider = sp.test_account("outsider")
    timeout = sp.nat(10)
    wager = sp.mutez(500)

    #player2 joins and oracle pays player1.
    bet_player1 = main.BetRosetta(player1.address, oracle.address, timeout, wager)
    bet_player1.set_initial_balance(wager)
    sc += bet_player1

    sc.verify(bet_player1.data.player1 == player1.address)
    sc.verify(~bet_player1.data.player2.is_some())
    sc.verify(bet_player1.data.oracle == oracle.address)
    sc.verify(bet_player1.data.wager == wager)
    sc.verify(bet_player1.data.deadline == sp.nat(10))

    bet_player1.win(sp.nat(0), _sender=oracle.address, _valid=False)
    bet_player1.join(_sender=player2.address, _amount=sp.mutez(400), _level=1, _valid=False)
    bet_player1.join(_sender=player2.address, _amount=wager, _level=1)
    
    sc.verify(bet_player1.data.player2.unwrap_some() == player2.address)
    sc.verify(bet_player1.balance == sp.mutez(1000))

    bet_player1.join(_sender=player3.address, _amount=wager, _level=2, _valid=False)
    bet_player1.win(sp.nat(0), _sender=outsider.address, _valid=False)
    bet_player1.win(sp.nat(2), _sender=oracle.address, _valid=False)
    bet_player1.win(sp.nat(0), _sender=oracle.address)

    sc.verify(bet_player1.balance == sp.mutez(0))

    #oracle pays player2.
    bet_player2 = main.BetRosetta(player1.address, oracle.address, timeout, wager)
    bet_player2.set_initial_balance(wager)
    sc += bet_player2

    bet_player2.join(_sender=player2.address, _amount=wager, _level=3)
    bet_player2.win(sp.nat(1), _sender=oracle.address)

    sc.verify(bet_player2.balance == sp.mutez(0))

    # Timeout path with no second player.
    timeout_no_join = main.BetRosetta(player1.address, oracle.address, timeout, wager)
    timeout_no_join.set_initial_balance(wager)
    sc += timeout_no_join

    timeout_no_join.join(_sender=player2.address, _amount=wager, _level=10)
    timeout_no_join.timeout(_sender=player1.address, _level=9, _valid=False)
    timeout_no_join.timeout(_sender=player1.address, _level=14)

    sc.verify(timeout_no_join.balance == sp.mutez(0))

    # Timeout path after player2 joined; both wagers are refunded.
    timeout_with_join = main.BetRosetta(player1.address, oracle.address, timeout, wager)
    timeout_with_join.set_initial_balance(wager)
    sc += timeout_with_join

    timeout_with_join.join(_sender=player2.address, _amount=wager, _level=4)
    timeout_with_join.timeout(_sender=player2.address, _level=9, _valid=False)
    timeout_with_join.timeout(_sender=player2.address, _level=25)

    sc.verify(timeout_with_join.balance == sp.mutez(0))