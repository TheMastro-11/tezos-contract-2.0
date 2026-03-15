import smartpy as sp

@sp.module
def main():
    class StorageRosetta(sp.Contract):
        def __init__(self):
            self.data.byte_sequence = sp.cast(None, sp.option[sp.bytes])
            self.data.text_string = sp.cast(None, sp.option[sp.string])

        @sp.entrypoint
        def storeBytes(self, byte_sequence: sp.bytes):
            self.data.byte_sequence = sp.Some(byte_sequence)

        @sp.entrypoint
        def storeString(self, text_string: sp.string):
            self.data.text_string = sp.Some(text_string)

@sp.add_test()
def test():
    sc = sp.test_scenario("StorageRosetta", main)

    storage = main.StorageRosetta()
    sc += storage

    sc.h1("Main scenario")

    sc.h2("Initial storage")
    sc.verify(~storage.data.byte_sequence.is_some())
    sc.verify(~storage.data.text_string.is_some())

    sc.h2("Store bytes")
    first_bytes = sp.bytes("0x1234")
    second_bytes = sp.bytes("0xaabbccdd")

    storage.storeBytes(first_bytes)
    sc.verify(storage.data.byte_sequence.is_some())
    sc.verify(storage.data.byte_sequence.unwrap_some() == first_bytes)
    sc.verify(~storage.data.text_string.is_some())

    storage.storeBytes(second_bytes)
    sc.verify(storage.data.byte_sequence.unwrap_some() == second_bytes)

    sc.h2("Store strings")
    first_text = "Hello Rosetta"
    second_text = "Storage updated"

    storage.storeString(first_text)
    sc.verify(storage.data.text_string.is_some())
    sc.verify(storage.data.text_string.unwrap_some() == first_text)
    sc.verify(storage.data.byte_sequence.unwrap_some() == second_bytes)

    storage.storeString(second_text)
    sc.verify(storage.data.text_string.unwrap_some() == second_text)
