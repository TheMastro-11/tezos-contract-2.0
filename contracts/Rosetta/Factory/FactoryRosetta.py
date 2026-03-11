import smartpy as sp

@sp.module
def main():
    class ProductRosetta(sp.Contract):
        def __init__(self, factory, creator, tag):
            self.data.factory = sp.cast(factory, sp.address)
            self.data.creator = sp.cast(creator, sp.address)
            self.data.tag = sp.cast(tag, sp.string)

        @sp.offchain_view()
        def getTag(self):
            assert sp.sender == self.data.creator
            return self.data.tag

        @sp.offchain_view()
        def getFactory(self):
            return self.data.factory

    class FactoryRosetta(sp.Contract):
        def __init__(self):
            self.data.products_by_creator = sp.cast({}, sp.map[sp.address, sp.list[sp.address]])

        @sp.entrypoint
        def createProduct(self, tag):
            tag = sp.cast(tag, sp.string)
            address = sp.create_contract(
                ProductRosetta, None, sp.tez(0), sp.record(factory=sp.self_address(), creator=sp.sender, tag=tag))
            current = self.data.products_by_creator[sp.sender]
            self.data.products_by_creator[sp.sender] = sp.cons(address, current)

        @sp.offchain_view()
        def getProducts(self, creator):
            creator = sp.cast(creator, sp.address)
            return self.data.products_by_creator[creator]
        

@sp.add_test()
def testWallet():
    #set scenario
    sc = sp.test_scenario("FactoryRosetta",main)
    #create admin
    admin = sp.test_account("admin")
    #create object simple wallet
    Factory = main.FactoryRosetta()
    #start scenario
    sc += Factory