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
