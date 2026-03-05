import smartpy as sp

@sp.module
def main():
    class CrowdfundRosetta(sp.Contract):
        def __init__(self, recipient, goal, deadline_level):
            self.data.recipient = sp.cast(recipient, sp.address)
            self.data.goal = sp.cast(goal, sp.mutez)
            self.data.deadline = sp.cast(deadline_level, sp.nat)
            self.data.closed = False
            self.data.contributions = sp.cast({}, sp.map[sp.address, sp.mutez])

        @sp.entrypoint
        def donate(self):
            assert self.data.closed == False
            assert sp.level < self.data.deadline
            self.data.contributions = sp.update_map(sp.sender, sp.Some(sp.amount), self.data.contributions)
            
        @sp.entrypoint
        def withdraw(self):
            assert self.data.closed == False
            assert sp.sender == self.data.recipient
            assert sp.level >= self.data.deadline
            assert sp.balance >= self.data.goal
            self.data.closed = True
            sp.send(self.data.recipient, sp.balance)

        @sp.entrypoint
        def reclaim(self):
            assert self.data.closed == False
            assert sp.level >= self.data.deadline
            assert sp.balance < self.data.goal
            assert self.data.contributions.contains(sp.sender)
            amount = self.data.contributions[sp.sender]
            assert amount > sp.mutez(0)
            self.data.contributions[sp.sender] = sp.mutez(0)
            sp.send(sp.sender, amount)

@sp.add_test()
def test():
    #set scenario
    sc = sp.test_scenario("CrowdfundRosetta",main)
    #create recipient
    recipient = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    #create object crowdfunding
    crowdFunding = main.CrowdfundRosetta(recipient, sp.mutez(1000), 100)
    #start scenario
    sc += crowdFunding