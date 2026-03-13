import smartpy as sp

@sp.module
def main():
    class ProductRosetta(sp.Contract):
        def __init__(self, owner: sp.address, factory: sp.address, tag: sp.string):
            self.data.tag = tag
            self.data.owner = owner
            self.data.factory = factory
            
        @sp.offchain_view()
        def getTag(self):
            assert sp.sender == self.data.owner, "only the owner"
            return self.data.tag

        @sp.offchain_view()
        def getFactory(self):
            return self.data.factory

    class FactoryRosetta(sp.Contract):
        def __init__(self):
            self.data.product_list = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.list[sp.address]])

        @sp.entrypoint
        def createProduct(self, tag: sp.string):
            address = sp.create_contract(
                ProductRosetta, None, sp.tez(0), sp.record(factory=sp.self_address, owner=sp.sender, tag=tag))
            if self.data.product_list.contains(sp.sender):
                self.data.product_list[sp.sender] = sp.cons(address, self.data.product_list[sp.sender])
            else:
                self.data.product_list[sp.sender] = [address]
            
            sp.emit(address)

        @sp.offchain_view()
        def getProducts(self, owner: sp.address) -> sp.list[sp.address]:
            assert self.data.product_list.contains(owner), "Address not avaiable"

            return self.data.product_list[owner]
        

@sp.add_test()
def testWallet():
    sc = sp.test_scenario("FactoryRosetta", main)

    alice = sp.test_account("alice")
    bob = sp.test_account("bob")
    charlie = sp.test_account("charlie")

    factory = main.FactoryRosetta()
    sc += factory

    sc.verify(sp.catch_exception(factory.getProducts(alice.address)) == sp.Some("Address not avaiable"))
    sc.verify(sp.catch_exception(factory.getProducts(bob.address)) == sp.Some("Address not avaiable"))
    sc.verify(sp.catch_exception(factory.getProducts(charlie.address)) == sp.Some("Address not avaiable"))

    factory.createProduct("alice-first", _sender=alice.address)
    factory.createProduct("alice-second", _sender=alice.address)
    factory.createProduct("bob-only", _sender=bob.address)

    first_product = sc.dynamic_contract(main.ProductRosetta, offset=-3)
    second_product = sc.dynamic_contract(main.ProductRosetta, offset=-2)
    third_product = sc.dynamic_contract(main.ProductRosetta, offset=-1)

    sc.verify(sp.len(factory.data.product_list[alice.address]) == 2)
    sc.verify(sp.len(factory.data.product_list[bob.address]) == 1)
    sc.verify(sp.catch_exception(factory.getProducts(charlie.address)) == sp.Some("Address not avaiable"))

    alice_products = sc.compute(factory.getProducts(alice.address))
    bob_products = sc.compute(factory.getProducts(bob.address))

    sc.verify(sp.len(alice_products) == 2)
    sc.verify(sp.len(bob_products) == 1)
    sc.verify_equal(alice_products, [second_product.address, first_product.address])
    sc.verify_equal(bob_products, [third_product.address])

    sc.verify_equal(first_product.data.owner, alice.address)
    sc.verify_equal(first_product.data.factory, factory.address)
    sc.verify_equal(first_product.data.tag, "alice-first")

    sc.verify_equal(second_product.data.owner, alice.address)
    sc.verify_equal(second_product.data.factory, factory.address)
    sc.verify_equal(second_product.data.tag, "alice-second")

    sc.verify_equal(third_product.data.owner, bob.address)
    sc.verify_equal(third_product.data.factory, factory.address)
    sc.verify_equal(third_product.data.tag, "bob-only")

    sc.verify_equal(sc.compute(first_product.getFactory()), factory.address)
    sc.verify_equal(sc.compute(second_product.getFactory()), factory.address)
    sc.verify_equal(sc.compute(third_product.getFactory()), factory.address)

    sc.verify_equal(first_product.data.tag, "alice-first")
    sc.verify_equal(second_product.data.tag, "alice-second")
    sc.verify_equal(third_product.data.tag, "bob-only")

    sc.verify(sp.catch_exception(first_product.getTag()) == sp.Some("only the owner"))
    sc.verify(sp.catch_exception(second_product.getTag()) == sp.Some("only the owner"))
    sc.verify(sp.catch_exception(third_product.getTag()) == sp.Some("only the owner"))
