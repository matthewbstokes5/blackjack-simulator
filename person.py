""" An individual involved in the game.

Dealer: Must adhere to casino rules, has no money and places no bets.
Player: Will adhere to a play strategy and betting strategy.
        Has money and places bets.
"""
import hand
import play_strategy
import stats
import strategy
import wallet


class Person(object):
  def __init__(self, name=''):
    self.name = name
    self.stats = stats.WinLossTie()
    self.action_stats = stats.ActionStats()
    self.blackjack_tie = 0

  def Reset(self):
    self.stats.Reset()
    self.action_stats.Reset()
    self.blackjack_tie = 0

  def Win(self, current_hand):
    self.stats.win += 1

    # Record blackjacks.
    if current_hand.IsBlackjack():
      self.stats.win_blackjack += 1

  def Loss(self):
    self.stats.loss += 1

  def Tie(self, current_hand):
    self.stats.tie += 1

    # Record blackjacks.
    if current_hand.IsBlackjack():
      self.blackjack_tie += 1


class Dealer(Person):
  """The dealer at the table."""
  def __init__(self, rules, name=''):
    """Constructor.

    Args:
      rules: table_rules.TableRules, rules at the table.
    """
    super(Dealer, self).__init__(name)
    self.table_rules = rules

  def Play(self, shoe, current_hand):
    """Play the dealer current hand.

    Dealer hits on everything lower than 16, depending on the table rules will
    hit or stand on soft 17, and will stand on everything 18-21.

    Args:
      shoe: Shoe, the table shoe. Used to get cards.
      current_hand: Hand, dealers current hand.
    """
    while True:
      if not current_hand.IsActive():
        self.action_stats.bust += 1
        break

      if current_hand.GetValue() < 17:
        current_hand.AddCard(shoe.GetCard())
        self.action_stats.hit += 1
      elif self.table_rules.hit_on_soft_17 and current_hand.IsSoft(17):
        current_hand.AddCard(shoe.GetCard())
        self.action_stats.hit += 1
      else:
        self.action_stats.stand += 1
        break


class PlayerException(Exception):
  """Base exception."""


class Player(Person):
  WALLET_TABLE_MIN = 'Table Minimum'
  WALLET_PROGRESSIVE = 'Progressive'
  WALLET_PROGRESSIVE_RESET = 'Progressive with Reset'
  WALLET_COUNT_BASIC = 'Count Basic'
  WALLET_BJ_OPTIMIZED = 'Blackjack Optimized'

  def __init__(self, rules, play_strategy, name=''):
    """Constructor.

    Args:
      rules: table_rules.TableRules, rules of the table.
    """
    super(Player, self).__init__(name)

    # Player needs to know about the rules in order to play and bet.
    self.table_rules = rules

    # How to play hands.
    self.play_strategy = play_strategy

    # Give the player some default wallets to compare betting strategies.
    self.wallets = {}
    self.AddWallet(wallet.Wallet(self.WALLET_TABLE_MIN,
                   strategy.StrategyTableMinimum(self.table_rules.min_money_units)))
    self.AddWallet(wallet.Wallet(self.WALLET_PROGRESSIVE,
                   strategy.StrategyProgressive(self.table_rules.min_money_units,
                                                self.table_rules.max_money_units)))
    self.AddWallet(wallet.Wallet(self.WALLET_PROGRESSIVE_RESET,
                   strategy.StrategyProgressive(self.table_rules.min_money_units,
                                                self.table_rules.max_money_units,
                                                reset_after_max=True)))
    self.AddWallet(wallet.Wallet(self.WALLET_COUNT_BASIC,
                   strategy.StrategyCount(self.table_rules.min_money_units,
                                          self.table_rules.max_money_units)))
    self.AddWallet(wallet.Wallet(self.WALLET_BJ_OPTIMIZED,
                   strategy.StrategyBlackjackOptimized()))

    self.num_split = 0
    self.num_double = 0

  def AddWallet(self, new_wallet):
    """Add wallet to list of wallets.
    
    Args:
      wallet: Wallet, wallet to add.

    Raises:
      PlayerException: Duplicate wallet.
    """
    # Check if wallet already exists
    if new_wallet in self.wallets:
      raise PlayerException('Wallet %s already created' % new_wallet)

    self.wallets[new_wallet.name] = new_wallet

  def PlaceBets(self, current_hand, **kwargs):
    """Bet some money units on the current hand.
    
    Args:
      current_hand: Hand, the current hand to place a bet on.
      kwargs: dict, Useful variables when placing a bet.
    """
    for active_wallet in self.wallets.itervalues():
      active_wallet.PlaceBet(current_hand, **kwargs)

  def _UpdateBetsSplitAction(self, current_hand, split_hand):
    """Add same bet to split hand.

    Args:
      current_hand: Hand, the current hand.
      split_hand: Hand, the hand which has split off.
    """
    for bet in current_hand.bets:
      # Sanity check for wallet to pay.
      if bet.wallet_name not in self.wallets:
        raise PlayerException('Double bet missing wallet named: %s' % bet.wallet_name)

      self.wallets[bet.wallet_name].money_units -= bet.money_units
      split_hand.AddBet(bet)

  def _UpdateBetsDoubleAction(self, current_hand):
    """Double current hand bet.

    Args:
      current_hand: Hand, the current hand.

    Raises:
      PlayerException: Unknown/missing wallet.
    """
    for bet in current_hand.bets:
      # Sanity check for wallet to pay.
      if bet.wallet_name not in self.wallets:
        raise PlayerException('Double bet missing wallet named: %s' % bet.wallet_name)

      self.wallets[bet.wallet_name].money_units -= bet.money_units
      bet.money_units *= 2

  def Reset(self):
    """Reset all wallets and stats."""
    super(Player, self).Reset()
    for active_wallet in self.wallets.itervalues():
      active_wallet.Reset()
    self.num_split = 0
    self.num_double = 0

  def Win(self, current_hand):
    """Hand won in the last round. Process bets and update strategy.

    Args:
      current_hand: Hand, the winning current hand.

    Raises:
      PlayerException: Unknown/missing wallet.
    """
    super(Player, self).Win(current_hand)

    # Is blackjack
    is_blackjack = current_hand.IsBlackjack()

    # Process bets.
    for bet in current_hand.bets:
      # Sanity check for wallet to pay.
      if bet.wallet_name not in self.wallets:
        raise PlayerException('Winning bet. Missing wallet named: %s' % bet.wallet_name)

      # Payment transfer.
      if is_blackjack:
        self.wallets[bet.wallet_name].money_units += (
            bet.money_units * (1 + self.table_rules.blackjack_win_multiplier))
      else:
        self.wallets[bet.wallet_name].money_units += bet.money_units * 2

    # Inform betting strategy of win.
    for active_wallet in self.wallets.itervalues():
      active_wallet.betting_strategy.ProcessWin(blackjack=is_blackjack)

  def Tie(self, current_hand):
    """Hand tied in the last round. Process bets and update strategy.

    Args:
      current_hand: Hand, the hand.

    Raises:
      PlayerException: Unknown/missing wallet.
    """
    super(Player, self).Tie(current_hand)

    # Process bets.
    for bet in current_hand.bets:
      # Sanity check for wallet to pay.
      if bet.wallet_name not in self.wallets:
        raise PlayerException('Winning bet. Missing wallet named: %s' % bet.wallet_name)

      # Payment transfer.
      self.wallets[bet.wallet_name].money_units += bet.money_units

    # Inform betting strategy of tie.
    for active_wallet in self.wallets.itervalues():
      active_wallet.betting_strategy.ProcessTie()

  def Loss(self):
    """Hand lost in the last round. Lick your wounds and update strategy.

    Raises:
      PlayerException: Unknown/missing wallet.
    """
    super(Player, self).Loss()

    # Inform betting strategy of loss.
    for active_wallet in self.wallets.itervalues():
      active_wallet.betting_strategy.ProcessLoss()

  def Play(self, current_shoe, current_hand, dealer_top_card):
    """Play the current hand.

    Args:
      current_shoe: Shoe, current active shoe.
      current_hand: Hand, current hand.
      dealer_top_card: Card, Dealers top card to use for your play strategy.

    Returns:
      [Hands], List of hands.
    """
    hands = [current_hand]
    for my_hand in hands:
      while True:
        # Hand busted.
        if not current_hand.IsActive():
          self.action_stats.bust += 1
          break

        # Get appropriate action from play strategy.
        action = self.play_strategy.GetAction(current_hand, dealer_top_card, len(hands))

        # Act upon action.
        if action == play_strategy.Action.STAND:
          self.action_stats.stand += 1
          break
        elif action == play_strategy.Action.HIT:
          current_hand.AddCard(current_shoe.GetCard())
          self.action_stats.hit += 1
        elif action == play_strategy.Action.DOUBLE:
          self._UpdateBetsDoubleAction(current_hand)
          current_hand.AddCard(current_shoe.GetCard())
          self.action_stats.double += 1
        elif action == play_strategy.Action.SPLIT:
          split_hand = hand.Hand([current_hand.Split()])
          current_hand.AddCard(current_shoe.GetCard())

          self._UpdateBetsSplitAction(current_hand, split_hand)
          split_hand.AddCard(current_shoe.GetCard())
          hands.append(split_hand)

          self.action_stats.split += 1
        else:
          raise PersonException('Unknown action: %s for hand: %s' % (
            action, current_hand))

    return hands
