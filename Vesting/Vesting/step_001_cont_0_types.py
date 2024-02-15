import smartpy as sp

tstorage = sp.record(amount = sp.mutez, beneficiary = sp.address, duration = sp.int, released = sp.mutez, start = sp.timestamp).layout(("amount", ("beneficiary", ("duration", ("released", "start")))))
tparameter = sp.variant(release = sp.unit).layout("release")
tprivates = { }
tviews = { }
