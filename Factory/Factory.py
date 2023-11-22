import smartpy as sp
from utils import utils


@sp.module
def main():
    class MyContract(sp.Contract):
        pass

        
    class Factory(sp.Contract):
        def __init__(self, _owner):
            self.data.owner = _owner
            self.data.created = None
        
        @sp.entrypoint
        def createContract(self):
            self.data.created = sp.Some(
                sp.create_contract(MyContract, None, sp.tez(0), ())
            )


@sp.add_test(name = "Simple Wallet")
def testWallet():
    #set scenario
    sc = sp.test_scenario([utils,main])
    #create admin
    admin = sp.test_account("admin")
    #create object simple wallet
    Factory = main.Factory(admin.address)
    #start scenario
    sc += Factory

    #create users
    pippo = sp.test_account("pippo")
    sofia = sp.test_account("sofia")
    sergio = sp.test_account("sergio")

    sc.h1("Create Contract")
    Factory.createContract()
    
    
    


            
            


    