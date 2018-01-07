""" Playing strategy.

Rules to STAND, HIT, DOUBLE, or SPLIT based on your hand.

"""
import os
import card
import hand
import yaml
from enum import Enum


class Action(Enum):
  STAND = 0
  HIT = 1
  DOUBLE = 2
  SPLIT = 3


class PlayStrategyException(Exception):
  """Base exception."""


# TODO(self): Make unit testable by passing stream instead of filename.
class PlayStrategy(object):
  # Available strategies.
  YAML_FOUR_DECK_HIT_SOFT_17 = os.path.join(
      '/', 'home', 'matthewbstokes','Blackjack',
      'play_strat_four_deck_hit_soft_17.yaml')

  def __init__(self, table_rules, yaml_file=YAML_FOUR_DECK_HIT_SOFT_17):
    """Constructor.

    Args:
      yaml_file: str, YAML filepath.
      table_rules: CasinoRules, Rules in the Casino.

    Raises:
      IOError: YAML file does not exist.
      PlayStrategyException: Strategy does not match casino rules.
    """
    self.table_rules = table_rules
    self.LoadStrategy(yaml_file)

  def LoadStrategy(self, yaml_file):
    """Load strategy from YAML file.

    Args:
      yaml_file: YAML filepath.

    Raises:
      IOError: YAML file does not exist
      PlayStrategyException: Strategy does not match casino rules.
    """
    strategy = yaml.load(open(yaml_file))

    if self.table_rules is not None:
      if (strategy['hit_on_soft_17'] != self.table_rules.hit_on_soft_17 or
          strategy['decks'] != self.table_rules.num_decks):
        raise PlayStrategyException('Strategy does not match casino rules.')

    # TODO(self): Add validation file contains necessary strategy.

    self.strategy = strategy

  def FindAndLoadStrategy(self, table_rules):
    """Find then load strategy that matches the table rules.

    Suggest multiple strategies for matching attribute counts.

    Args:
      table_rules: TableRules, Rules which define the table.
    """
    # TODO(self): Add logic to find then load strategy.
    pass

  def GetAction(self, current_hand, dealer_top_card, num_split_hands=1):
    """Get player action based on strategy.

    Args:
      current_hand: Hand, Players hand.
      dealer_top_card: Card, Dealers face up card.
      num_split_hands: int, Number of currently active split hands.

    Returns:
      Action, action to take.
    """
    if not current_hand.IsActive():
      return Action.STAND

    if (current_hand.IsSplitable() and
        num_split_hands <= self.table_rules.max_num_split_hands):
      strategy = self.strategy['split']
    elif current_hand.IsSoft():
      strategy = self.strategy['soft']
    else:
      strategy = self.strategy['hard']

    value = current_hand.GetValue()
    return strategy[value][dealer_top_card.value]
