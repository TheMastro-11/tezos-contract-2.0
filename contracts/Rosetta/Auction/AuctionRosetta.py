import smartpy as sp

@sp.module
def main():
    class AuctionRosetta(sp.Contract):
        def __init__(self, admin, starting_bid, bidding_period, object_description):
            self.data.admin = admin
            self.data.starting_bid = sp.cast(starting_bid, sp.mutez)
            self.data.bidding_period = sp.cast(bidding_period, sp.nat)
            self.data.object_description = sp.cast(object_description, sp.string)
            self.data.started = False
            self.data.ended = False
            self.data.end_level = sp.nat(0)
            self.data.top_bidder = sp.cast(None, sp.option[sp.address])
            self.data.top_bid = sp.mutez(0)
            self.data.refunds = sp.cast({}, sp.map[sp.address, sp.mutez])

        @sp.entrypoint
        def start(self):
            assert sp.sender == self.data.admin
            assert self.data.started == False
            self.data.started = True
            self.data.end_level = sp.level + self.data.bidding_period
            self.data.top_bid = self.data.starting_bid

        @sp.entrypoint
        def bid(self):
            assert self.data.started == True
            assert self.data.ended == False
            assert sp.level < self.data.end_level

            if sp.amount <= self.data.top_bid:
                sp.send(sp.sender, sp.amount)
            else:
                if self.data.top_bidder.is_some():
                    prev = self.data.top_bidder.unwrap_some()
                    self.data.refunds = sp.update_map(prev, sp.Some(self.data.top_bid), self.data.refunds)
                self.data.top_bidder = sp.Some(sp.sender)
                self.data.top_bid = sp.amount

        @sp.entrypoint
        def withdraw(self):
            assert self.data.refunds.contains(sp.sender)
            amount = self.data.refunds[sp.sender]
            assert amount > sp.mutez(0)
            self.data.refunds[sp.sender] = sp.mutez(0)
            sp.send(sp.sender, amount)

        @sp.entrypoint
        def end(self):
            assert sp.sender == self.data.admin
            assert self.data.started == True
            assert self.data.ended == False
            assert sp.level >= self.data.end_level
            self.data.ended = True
            sp.send(self.data.admin, sp.balance)


@sp.add_test()
def test():
    # set scenario
    sc = sp.test_scenario("AuctionRosetta", main)
    # create admin
    admin = sp.address("tz1SL2xBdmLSD2W3Hs84SfH912xDpYtAjsaa") 
    # new object Auction
    auction = main.AuctionRosetta(admin, sp.mutez(5), 10, "reason")
    # start scenario
    sc += auction