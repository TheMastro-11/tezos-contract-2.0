import smartpy as sp

@sp.module
def t():
    tx: type = sp.record(
        recipient=sp.address,
        value=sp.mutez,
        data=sp.bytes
    )

@sp.module
def main():
    class SimpleWalletRosetta(sp.Contract):
        def __init__(self, owner):
            self.data.owner = sp.cast(owner, sp.address)
            self.data.current_id = sp.nat(0)
            self.data.txs = sp.cast()
            sp.big_map({}, tkey=sp.nat, tvalue=sp.record(tx=t.tx, executed=sp.bool))

        @sp.entrypoint
        def deposit(self):
            assert sp.sender == self.data.owner

        @sp.entrypoint
        def createTransaction(self, batch):
            sp.cast(batch, t.tx)
            assert sp.sender == self.data.owner
            self.data.current_id += 1
            tx_id = self.data.current_id
            self.data.txs[tx_id] = sp.record(tx=batch, executed=False)
            sp.emit(tx_id)

        @sp.entrypoint
        def executeTransaction(self, tx_id):
            sp.cast(tx_id, sp.nat)
            assert sp.sender == self.data.owner
            assert self.data.txs.contains(tx_id)
            item = self.data.txs[tx_id]
            assert item.executed == False
            assert item.tx.value <= sp.balance
            self.data.txs[tx_id] = sp.record(tx=item.tx, executed=True)
            sp.send(item.tx.recipient, item.tx.value)

        @sp.entrypoint
        def withdraw(self):
            assert sp.sender == self.data.owner
            sp.send(self.data.owner, sp.balance)
            
@sp.add_test()
def test():
    # set scenario
    sc = sp.test_scenario("SimpleWalletRosetta", [t,main])
    # create admin
    admin = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    # create object simple wallet
    simpleWallet = main.SimpleWalletRosetta(admin.address)
    # start scenario
    sc += simpleWallet
