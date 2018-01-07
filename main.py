import argparse
import game
import table_rules

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--table-rules', type=str,
                      default=table_rules.DEFAULT_TABLE_RULES,
                      help='Table rules yaml.')
  parser.add_argument('--players', type=int, default=4,
                      help='Number of players at the table.')
  parser.add_argument('--num-rounds', type=int, default=100000,
                      help='Number of rounds to play before checking stats.')
  parser.add_argument('--interactive', action='store_true', default=True,
                      help='Allow the play of more games rather than exit.')
  return parser.parse_args()


def main():
  args = parse_args()

  blackjack_game = game.Game(num_players=args.players, rules=args.table_rules)
  blackjack_game.PlayRounds(args.num_rounds)
  blackjack_game.StatsForNerds()

  if args.interactive:
    while True:
      user_response = raw_input('Play more rounds? (y/n): ')
      # TODO(self): check for invalid response
      if user_response.lower() != 'y':
        break

      num_rounds = input('How many rounds?: ')
      blackjack_game.PlayRounds(args.num_arounds)
      blackjack_game.StatsForNerds()


if __name__ == '__main__':
  main()
