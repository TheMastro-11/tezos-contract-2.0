import myLibrary as lb
   
#connect to chain
pytezos = lb.pytezos.using(shell='ghostnet')
        
lb.fn.menu()   