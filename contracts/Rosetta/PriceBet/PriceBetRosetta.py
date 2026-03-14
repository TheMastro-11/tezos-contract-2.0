import smartpy as sp

@sp.module
def main():
    class PriceBetRosetta(sp.Contract):
        def __init__(self, owner: sp.address, initial_pot: sp.mutez ,oracle: sp.address, deadline: sp.nat, exchange_rate: sp.nat):
            self.data.initial_pot = initial_pot
            self.data.deadline_block = sp.level + deadline
            self.data.exchange_rate = exchange_rate
            self.data.oracle = oracle
            self.data.owner = owner
            self.data.player = sp.cast(None, sp.option[sp.address])

        @sp.entrypoint
        def join(self):
            assert sp.amount == self.data.initial_pot
            assert self.data.player.is_none()
            self.data.player = sp.Some(sp.sender)

        @sp.entrypoint
        def win(self):
            assert sp.level < self.data.deadline_block, "deadline expired"
            assert sp.sender == self.data.player.unwrap_some(), "invalid sender"
            price = sp.view("get_exchange_rate", self.data.oracle, (), sp.nat).unwrap_some()
            assert price >= self.data.exchange_rate, "you lost the bet"
            sp.send(sp.sender, sp.balance)

        @sp.entrypoint
        def timeout(self):
            assert sp.level >= self.data.deadline_block, "deadline not expired"
            sp.send(self.data.owner, sp.balance)
            
    class Oracle(sp.Contract):
        def __init__(self):
            self.data.exchange_rate = sp.nat(10)
            
        @sp.onchain_view
        def get_exchange_rate(self):
            return self.data.exchange_rate 
            
@sp.add_test()
def test():
    sc = sp.test_scenario("PriceBetRosetta", main)

    owner = sp.test_account("owner")
    player = sp.test_account("player")
    outsider = sp.test_account("outsider")
    initial_pot = sp.mutez(1_000_000)
    deadline = sp.nat(5)

    sc.h1("Winning path before the deadline")

    oracle_win = main.Oracle()
    sc += oracle_win

    winning_bet = main.PriceBetRosetta(
        owner=owner.address,
        initial_pot=initial_pot,
        oracle=oracle_win.address,
        deadline=deadline,
        exchange_rate=sp.nat(10),
    )
    winning_bet.set_initial_balance(initial_pot)
    sc += winning_bet

    sc.verify(winning_bet.data.owner == owner.address)
    sc.verify(winning_bet.data.oracle == oracle_win.address)
    sc.verify(winning_bet.data.initial_pot == initial_pot)
    sc.verify(winning_bet.data.exchange_rate == sp.nat(10))
    sc.verify(winning_bet.data.deadline_block == deadline)
    sc.verify(winning_bet.data.player.is_none())
    sc.verify(winning_bet.balance == initial_pot)

    winning_bet.win(_sender=player.address, _level=1, _valid=False)
    winning_bet.join(_sender=player.address, _amount=sp.mutez(500_000), _valid=False)
    winning_bet.join(_sender=player.address, _amount=initial_pot, _level=1)

    sc.verify(winning_bet.data.player.unwrap_some() == player.address)
    sc.verify(winning_bet.balance == sp.mutez(2_000_000))

    winning_bet.join(_sender=outsider.address, _amount=initial_pot, _level=2, _valid=False)
    winning_bet.win(_sender=outsider.address, _level=2, _valid=False)
    winning_bet.win(_sender=player.address, _level=deadline, _valid=False)
    winning_bet.win(_sender=player.address, _level=2)

    sc.verify(winning_bet.balance == sp.mutez(0))

    sc.h1("Losing path when the oracle price is too low")

    oracle_lose = main.Oracle()
    sc += oracle_lose

    losing_bet = main.PriceBetRosetta(
        owner=owner.address,
        initial_pot=initial_pot,
        oracle=oracle_lose.address,
        deadline=deadline,
        exchange_rate=sp.nat(11),
    )
    losing_bet.set_initial_balance(initial_pot)
    sc += losing_bet

    losing_bet.join(_sender=player.address, _amount=initial_pot, _level=1)

    sc.verify(losing_bet.balance == sp.mutez(2_000_000))

    losing_bet.win(_sender=player.address, _level=2, _valid=False)
    sc.verify(losing_bet.balance == sp.mutez(2_000_000))

    sc.h1("Timeout after the deadline")

    oracle_timeout = main.Oracle()
    sc += oracle_timeout

    timeout_bet = main.PriceBetRosetta(
        owner=owner.address,
        initial_pot=initial_pot,
        oracle=oracle_timeout.address,
        deadline=deadline,
        exchange_rate=sp.nat(10),
    )
    timeout_bet.set_initial_balance(initial_pot)
    sc += timeout_bet

    timeout_bet.timeout(_sender=owner.address, _level=1, _valid=False)
    timeout_bet.join(_sender=player.address, _amount=initial_pot, _level=1)

    sc.verify(timeout_bet.balance == sp.mutez(2_000_000))

    timeout_bet.win(_sender=player.address, _level=100, _valid=False)
    timeout_bet.timeout(_sender=owner.address, _level=100)

    sc.verify(timeout_bet.balance == sp.mutez(0))
