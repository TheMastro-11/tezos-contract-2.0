import smartpy as sp

@sp.module
#types definition
def t():
    tickets : type = sp.map[sp.nat, sp.ticket[sp.string]]
@sp.module
def m():
    class TokenGenerator(sp.Contract):
        def __init__(self, _admin):
            self.data.admin  = _admin
            #self.data.tickets = sp.cast({}, t.tickets)
            self.data.token_id = 0

        '''
        @sp.entrypoint
        def createToken(self):
            with sp.modify_record(self.data) as data:
                data.tickets[data.token_id] = sp.ticket("Primo", data.token_id)
                data.token_id += 1

        @sp.entrypoint
        def transferToken(self, _token_id):
            c = sp.contract(sp.ticket[sp.string], sp.sender).unwrap_some()
            with sp.modify_record(self.data) as data:
                sp.transfer(data.tickets.get_opt(_token_id).unwrap_some(), sp.tez(0), c)
        '''
        @sp.entrypoint
        def createToken(self):
            c = sp.contract(sp.ticket[sp.string], self.data.admin).unwrap_some()
            sp.transfer(sp.ticket("Primo", 1), sp.tez(0), c)
            self.data.token_id += 1
        

@sp.add_test()
def test():
    sc = sp.test_scenario("TicketGenerator", [t, m])
    owner = sp.test_account("owner")
    c1 = m.TokenGenerator(owner.address)
    sc += c1

    sc.h1("ciao")
    c1.createToken()





    
    