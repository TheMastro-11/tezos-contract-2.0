import myFunctions as fn
from pytezos import pytezos, Key
   
#connect to chain
pytezos = pytezos.using(shell='ghostnet')
#key = Key.from_encoded_key("edskS7VWazgioXEcBLhZ48sXmcwNmQ9HCx4q3tWch4MHdYVC7H4qAKtMbNQCZBQbAAL5WaduKA2H4fg8B7f2anEqZhpdXwk1yK")
#pytezos = pytezos.using(key=key)

fn.menu()   