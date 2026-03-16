import smartpy as sp

@sp.module
def main():
    class CrowdfundRosetta(sp.Contract):
        def __init__(self, receiver, end_donate, goal):
            self.data.end_donate = sp.cast(end_donate, sp.nat)
            self.data.goal = sp.cast(goal, sp.mutez)
            self.data.receiver = sp.cast(receiver, sp.address)
            self.data.donors = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.mutez])

        @sp.entrypoint
        def donate(self):
            assert sp.level < self.data.end_donate
            self.data.donors[sp.sender] += sp.amount
            
        @sp.entrypoint
        def withdraw(self):
            assert sp.level >= self.data.end_donate
            assert sp.balance >= self.data.goal
            
            sp.send(self.data.receiver, sp.balance)

        @sp.entrypoint
        def reclaim(self):
            assert sp.level >= self.data.end_donate
            assert sp.balance < self.data.goal
            assert self.data.donors[sp.sender] > sp.mutez(0)
            amount = self.data.donors[sp.sender]
            self.data.donors[sp.sender] = sp.mutez(0)
            
            sp.send(sp.sender, amount)
            
@sp.add_test()
def test():
    sc = sp.test_scenario("CrowdfundRosetta")
    recipient = sp.test_account("recipient")
    successful = main.CrowdfundRosetta(recipient.address, sp.nat(10), sp.mutez(100))
    sc += successful
