import smartpy as sp

@sp.module
def main():
    class CrowdFunding(sp.Contract):
        def __init__(self, admin, deadline):
            self.data.admin = admin
            self.data.startDate = sp.timestamp(0) 
            self.data.endDate = deadline
            self.data.contributors = (None, None )
            self.data.ceiling = sp.mutez(100000)
    
        @sp.entry_point
        def checkResult(self, time):
            assert sp.sender == self.data.admin, "You are not the Admin"
            assert time >= self.data.startDate.add_minutes(self.data.endDate),"The time is not over"
            assert sp.balance >= self.data.ceiling, "Crowdfund failed"
            #send all money to Admin
            sp.send(self.data.admin, sp.balance)

        @sp.private(with_storage="read-write")
        def getSeconds(self):
            return self.data.endDate * 60
        
        @sp.entry_point
        def contribute(self):
            #add on list
            if (self.data.contributors.contains(sp.sender)): 
                #check if it will reach the max amount with other donation
                prvDons = sp.mutez(0)
                prvDons = self.checkTotal(self.data.contributors[sp.sender])
                self.data.contributors[sp.sender].push(sp.amount) #if already exist
            else:
                self.data.contributors[sp.sender] =  [sp.amount] #insert donator address

        @sp.private(with_storage="read-write")
        def checkTotal(self, list_):
            total = sp.mutez(0)
            for j in list_:
                with list as x1:
                    total += x1.head
                    list_ = x1.tail
            return total
    
        @sp.entry_point
        def refund(self):
            #check if sender is a contributor
            assert self.data.contributors.contains(sp.sender), "You are not a contributor"
    
            #refund
            sp.send(sp.sender, self.checkTotal(self.data.contributors[sp.sender]))


@sp.add_test(name = "Crowdfunding")
def testCrowd():
    #set scenario
    sc = sp.test_scenario(main)
    #create admin
    admin = sp.test_account("admin")
    #create object crowdfunding
    crowdFunding = main.CrowdFunding(admin.address , 1)
    #start scenario
    sc += mcrowdFunding

    #create users
    pippo = sp.test_account("pippo")
    sofia = sp.test_account("sofia")
    sergio = sp.test_account("sergio")

    time = sp.timestamp_from_utc_now() #calculate execution time
    time = time.add_minutes(2)
    sc.h1("Check Time")
    crowdFunding.checkResult(time).run(sender = admin).run(valid = False)
    sc.h1("Pippo Contribute")
    crowdFunding.contribute().run(sender = pippo, amount = sp.mutez(10))
    sc.h1("Sofia Contribute")
    crowdFunding.contribute().run(sender = sofia, amount = sp.mutez(100))
    sc.h1("Pippo Contribute Again")
    crowdFunding.contribute().run(sender = pippo, amount = sp.mutez(1000000))
    sc.h1("Sergio Contribute")
    crowdFunding.contribute().run(sender = sergio, amount = sp.mutez(1000))
    sc.h1("Attempt to Contribute")
    crowdFunding.contribute().run(sender = sofia, amount = sp.mutez(10000))
    sc.h1("Check Result")
    crowdFunding.checkResult(time).run(sender = admin)
    
