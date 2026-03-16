import smartpy as sp

@sp.module
def main():
    import smartpy.stdlib.utils as utils
    
    class VestingRosetta(sp.Contract):
        def __init__(self, beneficiaryAddress: sp.address, start_timestamp: sp.nat, duration_seconds: sp.nat):
            assert beneficiaryAddress != sp.address("0"), "Beneficiary is zero address"
            self.data.released = sp.nat(0)
            self.data.beneficiary = beneficiaryAddress
            self.data.start = start_timestamp
            self.data.duration = duration_seconds

        @sp.entrypoint
        def release(self):
            amount = sp.nat(0)
            if (sp.level < self.data.start) :
                amount = sp.nat(0)
            else:
                if (sp.level > self.data.start + self.data.duration):
                    amount =  utils.mutez_to_nat(sp.balance) + self.data.released
                else:
                    amount = ((utils.mutez_to_nat(sp.balance) + self.data.released) * sp.as_nat(sp.level - self.data.start)) / self.data.duration
            amount = sp.as_nat(amount - self.data.released)
            self.data.released = self.data.released + amount
            sp.send(self.data.beneficiary, utils.nat_to_mutez(amount))
            sp.emit(amount)

@sp.add_test()
def test():
    sc = sp.test_scenario("VestingRosetta", main)
    beneficiary = sp.test_account("beneficiary")
    start_level = sp.nat(5)
    duration = sp.nat(10)
    vesting = main.VestingRosetta(beneficiary.address, start_level, duration)
    sc += vesting
