""" Table rules.

Collection of attributes which influence strategy that vary table to table.

"""
import collections


class TableRules(collections.namedtuple(
    'TableRules', ['min_money_units', 'max_money_units',
                   'blackjack_win_multiplier', 'hit_on_soft_17',
                   'num_decks', 'double_limited_to', 
                   'max_num_split_hands',
                   'max_num_seats'])):
  """Table rules."""

DEFAULT_TABLE_RULES = TableRules(
    min_money_units=1,
    max_money_units=20,
    blackjack_win_multiplier=1.5,
    hit_on_soft_17=True,
    num_decks=4,
    double_limited_to=[10, 11],
    max_num_split_hands=4,
    max_num_seats=8)
