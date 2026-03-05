import smartpy as sp

@sp.module
def main():
    class LogicRosetta(sp.Contract):
        def __init__(self):
            pass

        @sp.entrypoint
        def check(self, balance):
            sp.cast(balance, sp.mutez)
            assert balance < sp.tez(100)

    class ProxyRosetta(sp.Contract):
        def __init__(self, admin, logic_address):
            self.data.admin = sp.cast(admin, sp.address)
            self.data.logic_address = sp.cast(logic_address, sp.address)

        @sp.entrypoint
        def upgradeTo(self, new_logic):
            sp.cast(new_logic, sp.address)
            assert sp.sender == self.data.admin
            self.data.logic_address = new_logic

        @sp.entrypoint
        def check(self, balance):
            sp.cast(balance, sp.mutez)
            c = sp.contract(sp.mutez, self.data.logic_address, entrypoint="check").unwrap_some()
            sp.transfer(balance, sp.tez(0), c)

    class CallerRosetta(sp.Contract):
        def __init__(self):
            pass

        @sp.entrypoint
        def callProxy(self, proxy, balance):
            sp.cast(proxy, sp.address)
            sp.cast(balance, sp.mutez)
            c = sp.contract(sp.mutez, proxy, entrypoint="check").unwrap_some()
            sp.transfer(balance, sp.tez(0), c)

sp.add_test()
def testProxy():
    #Create Scenario
    sc = sp.test_scenario("UpgradableProxy", main)
    #Create Users
    admin = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    #Create Contract Object
    c1 = main.LogicRosetta()
    sc += c1
    c2 = main.ProxyRosetta(admin, c1.address)
    sc += c2
