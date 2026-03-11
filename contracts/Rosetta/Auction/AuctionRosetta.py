import smartpy as sp

@sp.module
def main():
    states: type = sp.variant(
        WAIT_START=sp.unit,
        WAIT_CLOSING=sp.unit,
        CLOSED=sp.unit)
    
    class AuctionRosetta(sp.Contract):
        def __init__(self, seller: sp.address, object: sp.string, starting_bid: sp.mutez):
            self.data.state = sp.cast(sp.variant.WAIT_START(), states)
            self.data.object = object
            self.data.seller = seller
            self.data.end_time = sp.cast(None, sp.option[sp.timestamp])
            self.data.highest_bidder = sp.cast(None, sp.option[sp.address])
            self.data.highest_bid = starting_bid
            self.data.bids = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.mutez])
            
        @sp.entrypoint
        def start(self, duration):
            assert self.data.state == sp.cast(sp.variant.WAIT_START(), states), "Auction already started"
            assert sp.sender == self.data.seller, "Only the seller"
            self.data.state = sp.cast(sp.variant.WAIT_CLOSING(), states)
            self.data.end_time = sp.Some(sp.add_seconds(sp.now,duration))

        @sp.entrypoint
        def bid(self):
            assert self.data.state == sp.cast(sp.variant.WAIT_CLOSING(), states), "Auction not started or already closed"
            assert sp.now < self.data.end_time.unwrap_some(), "Bidding time expired"
            
            assert sp.amount > self.data.highest_bid, "value must be greater than highest"

            if (self.data.highest_bidder != sp.Some(sp.sender)):
                self.data.bids[self.data.highest_bidder.unwrap_some()] = self.data.highest_bid

            if (self.data.bids[sp.sender] != sp.mutez(0)):
                sp.transfer((), sp.mutez(0), sp.self_entrypoint("withdraw"))

            self.data.highest_bidder = sp.Some(sp.sender)
            self.data.highest_bid = sp.amount

        @sp.entrypoint
        def withdraw(self):
            assert self.data.state != sp.cast(sp.variant.WAIT_CLOSING(), states), "Auction not started"
            bal = self.data.bids[sp.sender]
            self.data.bids[sp.sender] = sp.mutez(0)
            sp.send(sp.sender, bal)

        @sp.entrypoint
        def end(self):
            assert sp.sender == self.data.seller, "Only the seller"
            assert self.data.state == sp.cast(sp.variant.WAIT_CLOSING(), states), "Auction not started"
            assert sp.now >= self.data.end_time.unwrap_some(), "Auction not ended"
            self.data.state = sp.cast(sp.variant.CLOSED(), states)
            sp.send(self.data.seller, self.data.highest_bid)


@sp.add_test()
def test():
    sc = sp.test_scenario("AuctionRosetta", main)

    seller = sp.test_account("seller")
    alice = sp.test_account("alice")
    bob = sp.test_account("bob")

    auction = main.AuctionRosetta(seller.address, "reason", sp.mutez(5))
    auction.set_initial_balance(sp.mutez(5))
    sc += auction

    sc.verify(auction.data.state == sp.variant.WAIT_START(sp.unit))
    sc.verify(auction.data.highest_bid == sp.mutez(5))
    sc.verify(~auction.data.highest_bidder.is_some())

    auction.start(100, _sender=alice.address, _now=sp.timestamp(0), _valid=False)
    auction.start(100, _sender=seller.address, _now=sp.timestamp(0))
    auction.start(100, _sender=seller.address, _now=sp.timestamp(1), _valid=False)

    sc.verify(auction.data.state == sp.variant.WAIT_CLOSING(sp.unit))
    sc.verify(auction.data.end_time.unwrap_some() == sp.timestamp(100))

    auction.bid(_sender=alice.address, _amount=sp.mutez(5), _now=sp.timestamp(10), _valid=False)
    auction.bid(_sender=alice.address, _amount=sp.mutez(10), _now=sp.timestamp(10), _valid=False)
    auction.withdraw(_sender=alice.address, _now=sp.timestamp(20), _valid=False)

    auction.end(_sender=seller.address, _now=sp.timestamp(50), _valid=False)
    auction.end(_sender=bob.address, _now=sp.timestamp(101), _valid=False)
    auction.end(_sender=seller.address, _now=sp.timestamp(101))

    sc.verify(auction.data.state == sp.variant.CLOSED(sp.unit))
    auction.bid(_sender=bob.address, _amount=sp.mutez(25), _now=sp.timestamp(102), _valid=False)
    auction.withdraw(_sender=bob.address, _now=sp.timestamp(103), _valid=False)
