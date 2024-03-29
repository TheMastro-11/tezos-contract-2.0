## Specification

The OracleBet contract involves two players and an oracle. Upon stipulation, the first player deposits 1 token unit in the contract, and specifies the opponent and an oracle. A deadline is set to the current block height plus 1000.
After the stipulation, the second player must join the contract: this requires depositing 1 token unit.
At this point, the oracle is expected to determine the winner between the two players. The winner can redeem the whole pot of 2 token units.
If the oracle does not choose the winner by the deadline, then both players can redeem their bets, withdrawing 1 token units each.