import smartpy as sp

@sp.module
def main():
    class VestingRosetta(sp.Contract):
        def __init__(self, beneficiary, start_level, duration, total_amount):
            self.data.beneficiary = sp.cast(beneficiary, sp.address)
            self.data.start_level = sp.cast(start_level, sp.nat)
            self.data.duration = sp.cast(duration, sp.nat)
            self.data.total_amount = sp.cast(total_amount, sp.mutez)
            self.data.released = sp.mutez(0)

        @sp.entrypoint
        def release(self):
            assert sp.sender == self.data.beneficiary
            assert sp.level >= self.data.start_level
            assert self.data.duration > 0

            elapsed = sp.as_nat(sp.level - self.data.start_level)
            vested = sp.mutez(0)
            if elapsed >= self.data.duration:
                vested = self.data.total_amount
            else:
                vested = sp.split_tokens(self.data.total_amount, elapsed, self.data.duration)

            amount = vested - self.data.released
            assert amount > sp.mutez(0)
            self.data.released += amount
            sp.send(self.data.beneficiary, amount)
            
@sp.add_test()
def test():
    #set scenario
    sc = sp.test_scenario("VestingRosetta", main)
    #create users
    beneficiary = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    #create object
    c1 = main.VestingRosetta(beneficiary, 5, 10, sp.mutez(10))
    #start scenario
    sc += c1
