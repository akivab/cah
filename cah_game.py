import datetime
import logging
import model

TIMEOUT = datetime.timedelta(seconds=30)
NUM_CARDS = 50
NUM_PER_HAND = 7
MAX_PLAYERS = 6

def is_int(num):
	try:
		int(num)
		return True
	except Exception:
		return False

class Game(object):
	game = None
	player = None
	all_players = None
	current_round = None

	def finalize(self):
		if self.game: self.game.put()
		if self.player: self.player.put()
		if self.current_round: self.current_round.put()

	def in_round(self):
		if not self.player or not self.current_round or self.player.current_game != self.game.key:
			return False
		return True

	def add_card(self, card):
		if not self.in_round():
			return False, 'Player not in round.'
		if not is_int(card):
			return False, 'Card is not an int'
		if int(card) not in self.player.white_cards:
			return False, 'Card not in player hands'
		if self.player.key == self.game.players[self.current_round.leader]:
			return False, 'Leader cannot play in this round.'
		self.player.white_cards.remove(int(card))
		self.player.white_card = int(card)
		self.current_round.white_cards.append(int(card))
		return True, 'Added card.'

	def add_pick(self, card):
		if not self.in_round():
			return False, 'Player not in round.'
		if not is_int(card):
			return False, 'Card is not an int'
		if int(card) not in self.current_round.white_cards:
			return False, 'Card not in round'
		if self.player.key != self.game.players[self.current_round.leader]:
			return False, 'Not the round leader.'
		self.current_round.winning_card = int(card)
		return self.next()


	def reset_round(self):
		self.current_round.leader = (self.current_round.leader + 1) % len(self.game.players)
		self.current_round.black_card += 1
		self.current_round.round_start = datetime.datetime.now()
		self.current_round.white_cards = []
		self.current_round.winning_card = -1

	def get_all_players(self):
		if self.all_players: return
		self.all_players = []
		for player_key in self.game.players:
			self.all_players.append(player_key.get())
		return

	def reward_winner(self):
		if not self.current_round or not self.game:
			return False
		self.get_all_players()
		for player in self.all_players:
			if self.current_round.winning_card in player.white_cards:
				player.black_cards.append(self.current_round.black_card)
		return True

	def next(self):
		if len(self.game.players) < 2:
			return False, 'Fewer than 2 players. Cannot continue.'
		if not self.current_round:
			return False, 'No current round.'
		timeLeft = (datetime.datetime.now() - self.current_round.round_start)
		if not (self.current_round.winning_card != -1 or timeLeft < TIMEOUT):
			return False, '%d seconds till timeout.' % (TIMEOUT-timeLeft).seconds

		if self.current_round and self.current_round.winning_card != -1:
			self.reward_winner()

		self.add_player_cards()
		self.reset_round()
		return True, 'Reset round.'

	def add_player_cards(self):
		self.get_all_players()
		cards_in_play = []
		for player in self.all_players:
			cards_in_play.extend(player.white_cards)

		self.game.all_cards = set(range(NUM_CARDS)).difference(set(cards_in_play))

		for player in self.all_players:
			num_needed = NUM_PER_HAND - len(player.white_cards)
			player.white_cards.extend(self.game.all_cards[:num_needed])
			player.put()
			self.game.all_cards=self.game.all_cards[num_needed:]

	def leave_game(self):
		if (not self.player.current_game) or self.player.current_game != self.game.key:
			return False, 'Not in game.'
		self.remove_player_cards(self.player)
		self.game.players.remove(self.player.key)
		if self.game.creator == self.player.key:
			if len(self.game.players) > 0:
				self.game.creator = self.game.players[0]
			else:
				if self.current_round:
					self.current_round.key.delete()
					logging.info('Deleting current round')
				self.game.key.delete()
				logging.info('Deleting game')
				self.game = self.current_round = None
		self.player.current_game = None
		self.player.white_card = -1
		return True, 'Left game.'

	def join_game(self):
		if self.player.current_game:
			return False, 'Already in a game.'
		if len(self.game.players) > MAX_PLAYERS:
			return False, 'Room is full.'
		self.game.players = set(self.game.players + [self.player.key])
		self.player.current_game = self.game.key
		self.next()
		return True, 'Joined game.'

	def remove_player_cards(self, player):
		self.game.all_cards.extend(player.white_cards)
		player.white_cards = []