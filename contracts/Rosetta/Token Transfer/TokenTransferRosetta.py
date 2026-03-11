import smartpy as sp
from smartpy.templates import fa2_lib as fa2

@sp.module
def main(): 
    class TokenGenerator(
        main.Admin,
        main.Nft,
        main.ChangeMetadata,
        main.WithdrawMutez,
        main.MintNft,
        main.BurnNft,
        main.OffchainviewTokenMetadata,
        main.OnchainviewBalanceOf
        ,
    ):
        def __init__(self, administrator, metadata, ledger, token_metadata):
            main.OnchainviewBalanceOf.__init__(self)
            main.OffchainviewTokenMetadata.__init__(self)
            main.BurnNft.__init__(self)
            main.MintNft.__init__(self)
            main.WithdrawMutez.__init__(self)
            main.ChangeMetadata.__init__(self)
            main.Nft.__init__(self, metadata, ledger, token_metadata)
            main.Admin.__init__(self, administrator)
            self.data.answer = sp.mutez(0)
            
    class TokenTransferRosetta(sp.Contract):
        def __init__(self, owner, recipient, token_address):
            self.data.owner = sp.cast(owner, sp.address)
            self.data.recipient = sp.cast(recipient, sp.address)
            self.data.token_address = sp.cast(token_address, sp.address)
            self.data.balances = sp.cast({}, sp.map[sp.nat, sp.nat])

        @sp.private
        def fa2_transfer_(self, params):
            sp.cast(
                params,
                sp.record(
                    from_=sp.address,
                    to_=sp.address,
                    token_id=sp.nat,
                    amount=sp.nat,
                ),
            )
            transfer_params = [
                sp.record(
                    from_=params.from_,
                    txs=[sp.record(to_=params.to_, token_id=params.token_id, amount=params.amount)],
                )
            ]
            c = sp.contract(t.transfer_params, self.data.token_address, entrypoint="transfer").unwrap_some()
            sp.transfer(transfer_params, sp.tez(0), c)

        @sp.entrypoint
        def deposit(self, params):
            sp.cast(params, sp.record(token_id=sp.nat, amount=sp.nat))
            assert sp.sender == self.data.owner
            assert params.amount > 0
            self.fa2_transfer_(
                sp.record(
                    from_=self.data.owner,
                    to_=sp.self_address,
                    token_id=params.token_id,
                    amount=params.amount,
                )
            )
            self.data.balances[params.token_id] = self.data.balances[params.token_id] + params.amount

        @sp.entrypoint
        def withdraw(self, params):
            sp.cast(params, sp.record(token_id=sp.nat, amount=sp.nat))
            assert sp.sender == self.data.recipient
            assert self.data.balances[params.token_id] >= params.amount
            self.data.balances[params.token_id] = sp.as_nat(self.data.balances[params.token_id] - params.amount)
            self.fa2_transfer_(
                sp.record(
                    from_=sp.self_address,
                    to_=self.data.recipient,
                    token_id=params.token_id,
                    amount=params.amount,
                )
            )
            
@sp.add_test()
def testToken():  
    #Create Scenario
    sc = sp.test_scenario("TokenTransfer", [fa2.t, fa2.main, main])
    #Create Users
    owner = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa")
    recipient = sp.address("tz1aLPm3WynyHRXFvjjdHZDKEjHZVvQMGxqU")
    
    sc.h1("TokenGenerator Contract Creation")   
    sc.h3("Empty Value")
    c1 = main.TokenGenerator(
        administrator = owner.address,
        metadata = sp.big_map(),
        ledger = {},
        token_metadata = []
    )
    sc += c1
    
    #create Contract Object
    sc.h1("TokenTransfer Contract Creation")
    c2 = main.TokenTransferRosetta(owner, recipient, c1.address)
    sc += c2
