import smartpy as sp

@sp.module
def main():
    class StorageRosetta(sp.Contract):
        def __init__(self):
            self.data.stored_bytes = sp.bytes("0x")
            self.data.stored_string = ""

        @sp.entrypoint
        def storeBytes(self, value):
            sp.cast(value, sp.bytes)
            self.data.stored_bytes = value

        @sp.entrypoint
        def storeString(self, value):
            sp.cast(value, sp.string)
            self.data.stored_string = value

@sp.add_test()
def test():
    #set scenario
    sc = sp.test_scenario("StorageRosetta",main)
    #create object
    Storage = main.StorageRosetta()
    #start scenario
    sc += Storage