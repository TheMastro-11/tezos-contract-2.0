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
    oracle_win = main.Oracle()
    sc += oracle_win