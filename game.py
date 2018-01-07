""" A game of blackjack.

Select number of players and number of decks then PlayRounds or PlayShoes.
"""

import hand
import shoe
import strategy
import table_rules
import stats
import person
import play_strategy


class Seat(object):
  """A binding of player and a hand to a physical interface on the table."""
  def __init__(self, player=None):
    self.player = player
    self.hand = None

  def IsAvailable(self):
    return self.player is None

  def Leave(self):
    self.player = None
    self.hand = None

  def ClearHand(self):
    self.hand = None

  def AddPlayer(self, player):
    self.player = player


# TODO(self): Integrate into game.
class Table(object):
  """The blackjack table, including seats, table rules, and a dealer."""
  def __init_(self, table_rules, dealer):
    self.table_rules = table_rules
    self.dealer = dealer
    self.seats = []

    # Initialize seat with nobody there.
    for _ in self.table_rules.max_num_seats:
      self.seats[Seat()]

  def AddPlayer(self, seat_num, player):
    if not self.seats[seat_num].IsAvailable():
      raise GameException('Seat %d is not available' % seat_num)

    self.seats[seat_num].AddPlayer(player)


class GameException(Exception):
  """Base game exception."""

# TODO(self): Add additional players
# TODO(self): Add seating position
# TODO(self): Add no active hands dealer doesn't need to draw cards.
class Game(object):
  """Blackjack."""

  def __init__(self, num_players=5,
               rules=table_rules.DEFAULT_TABLE_RULES):
    """Constructor.

    Args:
      num_players: int, total number of players at the table. Excludes Dealer.
      rules: table_rules.TableRules, table rules.
    """
    # Rules and strategy
    self.table_rules = rules

    # Sanity check number of players.
    if 1 < num_players > self.table_rules.max_num_seats:
      raise GameException(
          'Must be between 1-%d players total.' % self.table_rules.max_num_seats)
    self.num_players = num_players

    # TODO(self): Support multiple play strategies.
    self.play_strategy = play_strategy.PlayStrategy(self.table_rules)

    # Initialize people.
    self.dealer = person.Dealer(self.table_rules)
    self.player = person.Player(self.table_rules, self.play_strategy)

    # Initializing game parameters.
    self.game_stats = stats.GameStats()
    self.shoe = shoe.Shoe(self.table_rules.num_decks)

  def AddPlayerWallet(self, new_wallet):
    """Add wallet to player.

    Args:
      new_wallet: Wallet, wallet to add.

    Raises:
      PlayerException: Duplicate wallet.
    """
    self.player.AddWallet(new_wallet)

  def Reset(self):
    """Reset everything."""
    self.player.Reset()
    self.dealer.Reset()
    self.game_stats.Reset()
    self.shoe.Reset()

  def StatsForNerds(self):
    """Print all the stats."""
    if self.game_stats.num_hands == 0:
      print 'No games played. No stats for you.'
      return

    # Game stats.
    print '== Game Stats ============'
    print 'Players: %d' % self.num_players
    print 'Decks:   %d' % self.table_rules.num_decks
    # TODO(self): Separate into rounds, and keep tractk of number of hands
    # in split condition.
    print 'Hands:   %d' % self.game_stats.num_hands
    print 'Shoes:   %d' % self.game_stats.num_shoes
    print 'Rate:    %0.1f [hands/shoe]' % (
        float(self.game_stats.num_hands) / self.game_stats.num_shoes)
    print '=========================='
    print ''

    # Dealer stats.
    print '== Dealer Stats =========='
    print 'Blackjack Win: %02.2f [%%]' % (
        (float(self.dealer.stats.win_blackjack) / self.game_stats.num_hands) * 100)
    print 'Blackjack Tie: %02.2f [%%]' % (
        (float(self.dealer.blackjack_tie) / self.game_stats.num_hands) * 100)
    print 'Bust: %.2f [%%]' % (
        (float(self.dealer.action_stats.bust) / self.game_stats.num_hands) * 100)
    print ''
    print 'Stand: %.2f [%%]' % (
        (float(self.dealer.action_stats.stand) / self.game_stats.num_hands) * 100)
    print 'Hit: %.2f [%%]' % (
        (float(self.dealer.action_stats.hit) / self.game_stats.num_hands) * 100)
    print '=========================='
    print ''
    

    # Player stats.
    print '== Player Stats =========='
    print 'Win:  %02.2f [%%]' % (
        (float(self.player.stats.win) / self.game_stats.num_hands) * 100)
    print 'Loss: %02.2f [%%]' % (
        (float(self.player.stats.loss) / self.game_stats.num_hands) * 100)
    print 'Tie:   {:2.2f} [%]'.format(
        (float(self.player.stats.tie) / self.game_stats.num_hands) * 100)
    print ''
    print 'Blackjack Win: %02.2f [%%]' % (
        (float(self.player.stats.win_blackjack) / self.game_stats.num_hands) * 100)
    print 'Blackjack Tie: %02.2f [%%]' % (
        (float(self.player.blackjack_tie) / self.game_stats.num_hands) * 100)
    print 'Bust: %.2f [%%]' % (
        (float(self.player.action_stats.bust) / self.game_stats.num_hands) * 100)
    print ''
    print 'Stand: %.2f [%%]' % (
        (float(self.player.action_stats.stand) / self.game_stats.num_hands) * 100)
    print 'Hit: %.2f [%%]' % (
        (float(self.player.action_stats.hit) / self.game_stats.num_hands) * 100)
    print 'Double: %.2f [%%]' % (
        (float(self.player.action_stats.double) / self.game_stats.num_hands) * 100)
    print 'Split: %.2f [%%]' % (
        (float(self.player.action_stats.split) / self.game_stats.num_hands) * 100)
    print '=========================='
    print ''

    # Money unit stats.
    print '== Performance Stats ====='
    for wallet_name in sorted(self.player.wallets.iterkeys()):
      self.player.wallets[wallet_name].PrintStats(self.game_stats)
    print '=========================='

  def PlayRounds(self, num_hands, reset=False):
    """Play some rounds.

    In a round a player may play more than one hand. Such an example is
    when a split occurs a player will have multiple active hands.

    Args:
      num_hands: int, number of hands to play
      reset: bool, reset the shoe after playing the hands.
    """
    start_num_hands = self.game_stats.num_hands
    finished = False
    while not finished:
      while not self.shoe.IsFinished():
        self.PlayRound()
        if self.game_stats.num_hands == (start_num_hands + num_hands):
          finished = True
          break
      self.game_stats.num_shoes += 1
      if not finished:
        self.shoe.Reset()
      elif reset:
        self.shoe.Reset()

  def PlayShoes(self, num_shoes):
    """Play multiple shoes.
    
    Args:
      num_shoes: int, number of shoes to play.
    """
    for _ in xrange(num_shoes):
      self.PlayShoe()

  def PlayShoe(self):
    """Play entire shoe."""
    while not self.shoe.IsFinished():
      self.PlayRound()
    self.game_stats.num_shoes += 1
    self.shoe.Reset()

  def PlayRound(self):
    """Play a round."""
    # Shoe is finished. Round over.
    if self.shoe.IsFinished():
      raise GameException('Unable to play round- shoe is finished.')

    # Burn cards representing other players for now.
    # TODO(self): Could keep track of everyone
    # and run experiments in parrallel.
    self.shoe.BurnCards(2 * (self.num_players - 1))

    # Place bet on the empty hand.
    player_hand = hand.Hand()

    # Pack parameters for betting strategies.
    kwargs = {}
    kwargs['shoe'] = self.shoe
    kwargs['num_hands'] = self.game_stats.num_hands
    self.player.PlaceBets(player_hand, **kwargs)

    # Get player hand
    player_hand.AddCards(self.shoe.GetCards(2))

    # Get dealer top card. This dictates how the player will play their hand.
    dealer_top_card = self.shoe.GetCard()
    dealer_hand = hand.Hand([dealer_top_card, self.shoe.GetCard()])

    # Increase stats.
    self.game_stats.num_hands += 1

    # Check for auto-loss dealer blackjack. Insurance is for suckers.
    if dealer_hand.IsBlackjack():
      if player_hand.IsBlackjack():
        self.player.Tie(player_hand)
        self.dealer.Tie(dealer_hand)
      else:
        self.player.Loss()
        self.dealer.Win(dealer_hand)
      return

    # Burn cards representing average num cards in blackjack hand.
    # TODO(self): Could keep track of everyone.
    self.shoe.BurnCards(1 * (self.num_players - 1))

    # Player blackjack. Pay me.
    if player_hand.IsBlackjack():
      self.player.Win(player_hand)
      return

    # Play player hand(s). Player may end up having multiple hands as a result
    # of split(s).
    player_hands = self.player.Play(self.shoe, player_hand, dealer_top_card)
    # TODO(self): Dealer may not need to depending on what players have.
    self.dealer.Play(self.shoe, dealer_hand)

    for player_hand in player_hands:
      self._ProcessOutcome(player_hand, dealer_hand)

  def _ProcessOutcome(self, player_hand, dealer_hand):
    """Process outcome of hand and update players.
    
    Args:
      player_hand: Hand, players hand.
      dealer_hand: Hand, dealer hand.
    """
    # If this is one of your split hands and you got blackjack.
    if player_hand.IsBlackjack():
      self.player.Win(player_hand)

    # If you bust you lose.
    elif not player_hand.IsActive():
      self.player.Loss()
      self.dealer.Win(dealer_hand)

    # If we good and dealer busts.
    elif not dealer_hand.IsActive():
      self.player.Win(player_hand)
      self.dealer.Loss()

    # We are both active, let's compare cards.
    elif player_hand.GetValue() == dealer_hand.GetValue():
      self.player.Tie(player_hand)
      self.dealer.Tie(dealer_hand)
    elif player_hand.GetValue() > dealer_hand.GetValue():
      self.player.Win(player_hand)
      self.dealer.Loss()
    else:
      self.player.Loss()
      self.dealer.Win(dealer_hand)
