""" The fund location supporting a betting strategy.

A player will own multiple wallets, which will have different
betting strategies.
"""
import strategy


class Bet(object):
  def __init__(self, wallet_name, money_units=0):
    """Constructor.

    Args:
      wallet_name: str, Name of wallet placing the bet.
      money_units: int, Number of money units.
    """
    self.wallet_name = wallet_name
    self.money_units = money_units

  def IncreaseBet(self, money_units):
    """Add money units to the current bet.

    Args:
      money_units: int, Number of money units to add.
    """
    self.money_units += money_units


class Wallet(object):
  """A collection of money associated with a betting strategy."""
  def __init__(self, name, betting_strategy, starting_money_units=0):
    """Constructor.

    Args:
      name: str, Wallet name.
      betting_strategy: BettingStrategy, strategy.
      starting_money_units: int, starting money units.
    """
    self.name = name
    self.betting_strategy = betting_strategy
    self.starting_money_units = starting_money_units
    self.money_units = self.starting_money_units

  def Reset(self, zero_reset=False):
    """Reset money units.

    Args:
      zero_reset: bool, reset money units to 0 instead of starting money units.
    """
    if zero_reset:
      self.money_units = 0
    else:
      self.money_units = self.starting_money_units

    self.betting_strategy.Reset()

  def PlaceBet(self, next_hand, **kwargs):
    """Determine how much to bet on the next hand.

    Bet amount will depend on the betting strategy and various other factors
    which are passed as kwargs.

    Money units are transfered from the wallet to the hand.

    Args:
      next_hand: Hand, hand to place bet onto.
      kwargs: dict, relevent parameters which influence betting strategy.
    """
    amount = self.betting_strategy.GetBetAmount(**kwargs)

    # Sanity check the bet.
    if not amount or amount < 0:
      raise WalletException('Invalid bet amount')

    # Transfer money units to the hand- No funny business if you leave before
    # hand is finished.
    self.money_units -= amount
    next_hand.bets.append(Bet(self.name, amount))

  # TODO(self): Revist who calculates stats.
  def PrintStats(self, game_stats):
    self.betting_strategy.PrintStats(self.name, game_stats, self.money_units)
