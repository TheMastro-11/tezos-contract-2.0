import smartpy as sp

@sp.module
def main():
    class ProxyRosetta(sp.Contract):
        def __init__(self, admin: sp.address, logic_address: sp.address):
            self.data.admin = admin
            self.data.logic_address = logic_address

        @sp.entrypoint
        def upgradeTo(self, new_logic: sp.address):
            assert sp.sender == self.data.admin
            self.data.logic_address = new_logic

        @sp.entrypoint
        def check(self, balance: sp.mutez):
            c = sp.contract(sp.mutez, self.data.logic_address, entrypoint="check").unwrap_some()
            sp.transfer(balance, sp.tez(0), c)

    class CallerRosetta(sp.Contract):
        def __init__(self):
            pass

        @sp.entrypoint
        def callLogicByProxy(self, proxy: sp.address, balance: sp.mutez):
            c = sp.contract(sp.mutez, proxy, entrypoint="check").unwrap_some()
            sp.transfer(balance, sp.tez(0), c)
    
    class LogicRosetta(sp.Contract):
        def __init__(self):
            pass

        @sp.entrypoint
        def check(self, to_check: sp.mutez):
            assert to_check >= sp.mutez(100)

@sp.module
def scenario_helpers():
    class AcceptBelowThreshold(sp.Contract):
        def __init__(self, threshold: sp.mutez):
            self.data.threshold = threshold

        @sp.entrypoint
        def check(self, to_check: sp.mutez):
            assert to_check < self.data.threshold

    class AcceptFromThreshold(sp.Contract):
        def __init__(self, threshold: sp.mutez):
            self.data.threshold = threshold

        @sp.entrypoint
        def check(self, to_check: sp.mutez):
            assert to_check >= self.data.threshold

@sp.add_test()
def testProxy():
    sc = sp.test_scenario("UpgradableProxy", [main, scenario_helpers])

    admin = sp.test_account("admin")
    outsider = sp.test_account("outsider")

    threshold = sp.mutez(100)
    below_threshold_logic = scenario_helpers.AcceptBelowThreshold(threshold)
    from_threshold_logic = scenario_helpers.AcceptFromThreshold(threshold)
    proxy = main.ProxyRosetta(admin.address, below_threshold_logic.address)
    caller = main.CallerRosetta()

    sc.h1("Main scenario")

    sc += below_threshold_logic
    sc += from_threshold_logic
    sc += proxy
    sc += caller

    sc.h2("Initial storage")
    sc.verify(proxy.data.admin == admin.address)
    sc.verify(proxy.data.logic_address == below_threshold_logic.address)

    sc.h2("Current implementation routing")
    proxy.check(sp.mutez(99), _sender=outsider.address)
    proxy.check(sp.mutez(100), _sender=outsider.address, _valid=False)
    caller.callLogicByProxy(proxy=proxy.address, balance=sp.mutez(99), _sender=outsider.address)
    caller.callLogicByProxy(proxy=proxy.address, balance=sp.mutez(100), _sender=outsider.address, _valid=False)

    sc.h2("Upgrade access control")
    proxy.upgradeTo(from_threshold_logic.address, _sender=outsider.address, _valid=False)
    sc.verify(proxy.data.logic_address == below_threshold_logic.address)

    sc.h2("Admin upgrade")
    proxy.upgradeTo(from_threshold_logic.address, _sender=admin.address)
    sc.verify(proxy.data.logic_address == from_threshold_logic.address)

    sc.h2("Updated implementation routing")
    proxy.check(sp.mutez(99), _sender=outsider.address, _valid=False)
    proxy.check(sp.mutez(100), _sender=outsider.address)
    caller.callLogicByProxy(proxy=proxy.address, balance=sp.mutez(99), _sender=outsider.address, _valid=False)
    caller.callLogicByProxy(proxy=proxy.address, balance=sp.mutez(100), _sender=outsider.address)
