import smartpy as sp
from smartpy.templates import fa2_lib as fa2

@sp.module
#Type Definition
def types():
    ledger_stored_nft: type = sp.map[sp.nat, sp.record(
        info_ = t.transfer_batch,
        contract_address = sp.address,
        )]

    deposit_params : type = sp.record(
        amount_ = sp.nat, 
        token_id = sp.nat, 
        recipient_ = sp.address, 
        contract_address = sp.address
    )
    
@sp.module
def m():
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
            
    class TokenTransfer(sp.Contract):
        def __init__(self):
            self.data.tokenStored = sp.cast({}, types.ledger_stored_nft)

        @sp.entrypoint
        def deposit(self, batch):
            sp.cast(batch, types.deposit_params)
            tx = sp.record(
                to_ = batch.recipient_,
                token_id = batch.token_id,
                amount = batch.amount_,
            )
            info = sp.record(from_ = sp.sender, txs = [tx])
        
            self.data.tokenStored[batch.token_id] = sp.record(
                    info_ = info,
                    contract_address = batch.contract_address
            )

        @sp.entrypoint
        def withdraw(self, _token_id):
            value = self.data.tokenStored.get_opt(_token_id).unwrap_some()
            for i in value.info_.txs:
                assert sp.sender == i.to_, "You are not the owner"
                contract = sp.contract(t.transfer_params, value.contract_address , entrypoint="transfer")
                sp.transfer([value.info_], sp.tez(0), contract.unwrap_some(error="ContractNotFound"))
            
            
                
        
def make_metadata(symbol, name, decimals, image):
    """Helper function to build metadata JSON bytes values."""
    return sp.map(
        l={
            "decimals": sp.scenario_utils.bytes_of_string("%d" % decimals),
            "name": sp.scenario_utils.bytes_of_string(name),
            "symbol": sp.scenario_utils.bytes_of_string(symbol),
            "image" : sp.scenario_utils.bytes_of_string(image),
        }
    )    


    
@sp.add_test()
def testToken():  
    #Create Scenario
    sc = sp.test_scenario("TokenGenerator", [fa2.t, fa2.main, types, m])
    #Create Users
    owner = sp.test_account("owner")
    bob = sp.test_account("bob")
    #Create token metadata
    tok0_md = make_metadata(name="Token Zero", decimals=1, symbol="Tok0", image = "imagine")
    tok1_md = make_metadata(name="Token Uno", decimals=1, symbol="Tok1", image = "imagine2")
    #create Contract Object
    sc.h1("TokenGenerator Contract Creation")   
    sc.h3("Empty Value")
    c1 = m.TokenGenerator(
        administrator = owner.address,
        metadata = sp.big_map(),
        ledger = {},
        token_metadata = []
    )
    sc += c1

    sc.h1("TokenTransfer Contract Creation")
    c2 = m.TokenTransfer()
    sc += c2
   
   
    sc.h1("Mint a new token")
    c1.mint(
        [
            sp.record(
                to_  = owner.address, # Who will receive the original mint
                metadata = tok0_md
            )
        ],
        _sender=owner)

    
    #Add Operator
    sc.h1("Add Operator")
    c1.update_operators([
        sp.variant("add_operator", sp.record(
            owner = owner.address,
            operator = c2.address,
            token_id = 0))
        ],
        _sender=owner)
    
    
    #Deposit a token to contract
    sc.h1("Deposit")
    c2.deposit(sp.record(
        amount_ = sp.nat(1), 
        token_id = sp.nat(0), 
        recipient_ = bob.address, 
        contract_address = c1.address
    ), _sender = owner)

    #Withdraw a token from contract
    sc.h1("Withdraw")
    c2.withdraw(sp.nat(0), _sender = bob)

    c1.transfer([
        sp.record(
            from_ = bob.address,
            txs = [
                sp.record(to_ = owner.address, amount=1, token_id=0)
            ])], _sender = owner)