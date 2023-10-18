import smartpy as sp
from utils import utils

@sp.module
def main():
    class Auction(sp.Contract):
        def __init__ (self):
            self.data.bidders = {None : None}
            self.data.top = sp.record(winning = [],amount = sp.mutez(0))
            self.data.amount = sp.mutez(0)
            self.data.minBid = sp.mutez(0)
    
        
        @sp.entry_point
        def bid(self):
            #check if a bidder has already partecipated
            assert self.data.bidders.contains(sp.Some(sp.sender)) == False, "This address is already registered"
            
            #add to bidder
            self.data.bidders[sp.Some(sp.sender)] = sp.Some(sp.amount)
    
            #check if is top bid
            if sp.amount >= self.data.top.amount:
                if sp.amount > self.data.top.amount:
                    self.data.top = sp.record(winning = [sp.sender], amount = sp.amount)
                else:
                    newList = sp.cons(sp.sender, self.data.top.winning)
                    self.data.top = sp.record(winning = newList, amount = sp.amount)
            
        @sp.entry_point
        def getWinner(self):
            #check how many winners
            listTemp = self.data.top.winning
            #remove temporarily winners from map
            for i in listTemp:
                    adTemp = listTemp
                    listTemp = listTemp.tail
                    #delete winner from map
                    del self.data.bidders[adTemp]
            
            #rimborso 
            addressList = self.data.bidders.keys()
            for i in addressList:
                    address = addressList.head
                    addressList.value = addressList.tail
                    sp.send(address, self.data.bidders[address])
                    del self.data.bidders[address]
                    
            #re-list
            listTemp.value = self.data.top.winning
            for j in listTemp:
                    address = listTemp.head
                    listTemp.value = listTemp.tail
                    self.data.bidders[address] = self.data.top.amount
    
            #case: more then 1 winners
            if sp.len(self.data.bidders) > 1:
                self.data.minBid = self.data.top.amount
                self.data.top = sp.record(winning = [], amount = sp.mutez(0))
                adList = self.data.bidders.keys()
                for k in adList.value:
                        address = listTemp.head
                        adList.value = listTemp.tail
                        sp.send(address, self.data.minBid)


@sp.add_test(name = "auctionTest")
def auctionTest():
    #set scenario
    sc = sp.test_scenario(main)
    #new object Auction
    auction = main.Auction()
    #start scenario
    sc += auction

    #users
    sofia = sp.test_account("sofia")
    piero = sp.test_account("piero")
    carla = sp.test_account("carla")
    maria = sp.test_account("maria")

    #first bid
    sc.h1("First Bid")
    auction.bid().run(sender = sofia, amount = sp.mutez(100))
    auction.bid().run(sender = sofia, amount = sp.mutez(100)).run(valid = False)
    #second bid
    sc.h1("Second Bid")
    auction.bid().run(sender = piero, amount = sp.mutez(10))
    #third bid
    sc.h1("Third Bid")
    auction.bid().run(sender = carla, amount = sp.mutez(1000))
    sc.h1("Fourth Bid")
    auction.bid().run(sender = maria, amount = sp.mutez(100))
    #ending
    sc.h1("ending")
    auction.getWinner()
    
