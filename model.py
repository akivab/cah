from google.appengine.ext import ndb

class Player(ndb.Model):
	# User property. In the future, we'll want to add stuff for authenticating other users.
	# We may want to use Facebook/Twitter/Firebase login in the future.
	user = ndb.UserProperty(required=True)
	 # When we pick our card, set it here and in current_round.white_cards.
	 # This will be used to find who had the winning card. Will be cleared
	 # at the start of each new round. Will be -1 when not set.
	white_card = ndb.IntegerProperty(required=True, default=-1)
	# At the start of a new round, make sure this hand is full.
	white_cards = ndb.IntegerProperty(repeated=True)
	# These are the cards won by the player.
	black_cards = ndb.IntegerProperty(repeated=True)
	# This is the room that we are currently playing in.
	current_game = ndb.KeyProperty(required=False)
	# This is the date the player joined.
	joined = ndb.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def to_json(p, is_current_user=False):
		ret = {
			'name': p.user.nickname(),
			'key': p.user.user_id(),
			'joined': str(p.joined),
			'current_game': p.current_game.id() if p.current_game else None
		}
		if is_current_user:
			ret['white_cards'] = p.white_cards
			ret['black_cards'] = p.black_cards
		return ret


class Round(ndb.Model):
	# Leader of this round.
	leader = ndb.IntegerProperty(required=True, default=0)
	# Current black card used.
	black_card = ndb.IntegerProperty(required=True, default=0)
	# Time that the round started.
	round_start = ndb.DateTimeProperty(required=True,auto_now_add=True)
	# White cards submitted for winning.
	white_cards = ndb.IntegerProperty(repeated=True)
	# Winning card for this round.
	winning_card = ndb.IntegerProperty()
	# Last round's information.
	last_winner = ndb.KeyProperty(kind=Player)
	last_winning_card = ndb.IntegerProperty()

class Game(ndb.Model):
	# Name of the current game.
	name = ndb.StringProperty(required=True)
	# Players of the current game.
	players = ndb.KeyProperty(repeated=True, kind=Player)
	# Key for the current round.
	current_round = ndb.KeyProperty(kind=Round)
	# Creator of this game.
	creator = ndb.KeyProperty(required=True, kind=Player)
	# List of all the cards that are currently not in play.
	all_cards = ndb.IntegerProperty(repeated=True)

	@staticmethod
	def to_json(game):
		return {
			'name': game.name,
			'id': game.key.id(),
			'players': [Player.to_json(p.get()) for p in game.players],
			'creator': Player.to_json(game.creator.get()),
			'current_round': game.current_round.id() if game.current_round else None
		}
	
