#calling update operators from another contract
@sp.entrypoint
def transfer(self, token_id_, contract_address):
    contract = sp.contract(t.update_operators_params, contract_address, entrypoint="update_operators")
    sp.transfer([sp.variant.add_operator(sp.record(
            owner = sp.sender,
            operator = sp.self_address(),
            token_id = token_id_))], 
        sp.tez(0), contract.unwrap_some(error="ContractNotFound"))