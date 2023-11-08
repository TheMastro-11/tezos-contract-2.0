import smartpy as sp

@sp.module
def main():
    class CrowdFunding(sp.Contract):
        def __init__(self, admin, deadline, goal): 
            self.data.receiver = admin
            self.data.startDate = sp.timestamp(0) 
            self.data.endDate = deadline 
            self.data.contributors = {None : None}
            self.data.goal = sp.mutez(10)
    
        @sp.entry_point
        def withdraw(self, time): 
            assert sp.sender == self.data.receiver, "You are not the Admin"
            assert time >= sp.add_seconds(self.data.startDate, self.data.endDate*60 ) ,"The time is not over"
            assert sp.balance >= self.data.goal, "Crowdfund failed"
            #send all money to Admin
            sp.send(self.data.receiver, sp.balance)

        @sp.private(with_storage="read-write")
        def getSeconds(self):
            return self.data.endDate * 60
        
        @sp.entry_point
        def donate(self):
            tmp = sp.update_map(sp.Some(sp.sender), sp.Some(sp.Some(sp.amount)), self.data.contributors)

    
        @sp.entry_point
        def refund(self):
            #check if sender is a contributor
            assert self.data.contributors.contains(sp.Some(sp.sender)), "You are not a contributor"
            assert time >= sp.add_seconds(self.data.startDate, self.data.endDate*60 ) ,"The time is not over"
            assert sp.balance >= self.data.goal, "Crowdfund failed"
            
            #refund
            sp.send(sp.sender, self.data.contributors[sp.Some(sp.sender)].unwrap_some())


@sp.add_test(name = "Crowdfunding")
def testCrowd():
    #set scenario
    sc = sp.test_scenario(main)
    #create admin
    admin = sp.test_account("admin")
    #create object crowdfunding
    crowdFunding = main.CrowdFunding(admin.address , 1, 10000)
    #start scenario
    sc += crowdFunding

    #create users
    pippo = sp.test_account("pippo")
    sofia = sp.test_account("sofia")
    sergio = sp.test_account("sergio")

    time = sp.timestamp_from_utc_now() #calculate execution time
    time = time.add_minutes(2)
    sc.h1("Check Time")
    crowdFunding.withdraw(time).run(sender = admin, valid = False)
    sc.h1("Pippo donate")
    crowdFunding.donate().run(sender = pippo, amount = sp.mutez(10))
    sc.h1("Sofia donate")
    crowdFunding.donate().run(sender = sofia, amount = sp.mutez(100))
    sc.h1("Pippo donate Again")
    crowdFunding.donate().run(sender = pippo, amount = sp.mutez(1000000))
    sc.h1("Sergio donate")
    crowdFunding.donate().run(sender = sergio, amount = sp.mutez(1000))
    sc.h1("Attempt to donate")
    crowdFunding.donate().run(sender = sofia, amount = sp.mutez(10000))
    sc.h1("Check Result")
    crowdFunding.withdraw(time).run(sender = admin)
    
