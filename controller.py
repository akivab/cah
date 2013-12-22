from google.appengine.api import users
from google.appengine.ext import ndb

import cah_game
import logging
import json
import model
import webapp2

class MainController(webapp2.RequestHandler):
	def get(self):
		self.response.out.write('hello!')

class PlayerController(webapp2.RequestHandler):
	def get(self):
		self.response.out.write('player!')

class GameController(webapp2.RequestHandler):
	'''Controller for a Game.

	LEADER is the current LEADER of the round.
	TIMEOUT is set by start of last  round.

	GET /game?name=NAME
		returns: JSON detailing state of game

	POST /game
		returns: JSON detailing state of game
		params:
			name=NAME Lets us create a room by NAME.
			card=CARD	Lets a player submit a card.
			action={ next, add_room, add_pick }
				list_room: lists all rooms (no params needed)
				info: requires name
				next: requires name param
				join_room: requires name
				leave_room: requires name
				add_room: requires name param
				add_pick: requires name,pick params

	'''
	def get_player(self, add_player=True):
		user = users.get_current_user()
		player = model.Player.gql('where user=:1', user).get()
		if not player and add_player:
			player = model.Player(user=user, black_cards=[])
			player.put()
		return player

	@ndb.transactional(xg=True)
	def add_pick(self, game):
		card = self.request.get('card')
		if not game.game or not card: return self.game_info(game)
		success, reason = game.add_pick(card)
		if success:
			game.finalize()
			return self.game_info(game)
		return self.bad_request(reason)

	@ndb.transactional(xg=True)
	def add_room(self, game):
		if game.game: return self.game_info(game)
		if not game.player:
			game.player = self.get_player()

		name = self.request.get('name')
		if not name or not game.player:
			return self.bad_request('Cannot add game.')
		game.game = model.Game(name=name, players=[game.player.key], all_cards=range(cah_game.NUM_CARDS), creator=game.player.key)
		game.game.put()
		return self.game_info(game)

	@ndb.transactional(xg=True)
	def join_room(self, game):
		if not game.game: return self.game_info(game)
		if not game.player: game.player = self.get_player()
		success, reason = game.join_game()
		if success:
			game.finalize()
			return self.game_info(game)
		return self.bad_request(reason)

	@ndb.transactional(xg=True)
	def leave_room(self, game):
		if not game.game: return self.game_info(game)
		if not game.player:
			return self.need_login()
		success, reason = game.leave_game()
		if success:
			game.finalize()
			return self.game_info(game)
		return self.bad_request(reason)

	@ndb.transactional(xg=True)
	def next(self, game):
		if not game.game: self.game_info(game)
		if not game.player:
			return self.need_login()
		success, reason = game.next()
		if success:
			game.finalize()
			return self.game_info(game)
		return self.bad_request(reason)

	def need_login(self):
		url = users.create_login_url(self.request.path)
		self.response.out.write(json.dumps({
			'login_url': url,
			'error': 1,
			'reason': 'Need to login.'
		}))

	def bad_request(self, opt_reason=None, game=None):
		response = { 'error': 'Bad request.' }
		if game and game.player:
			response['player'] = {
				'user': model.Player.to_json(game.player)
			}
		if opt_reason:
			response['reason'] = opt_reason
		self.response.out.write(json.dumps(response))

	def game_info(self, game):
		if not game.game:
			return self.bad_request('No game.')
		ret = {}
		ret['game'] = model.Game.to_json(game.game)
		if game.player:
			ret['user'] = model.Player.to_json(game.player, True)
		elif not users.get_current_user():
			ret['login_url'] = users.create_login_url()
		self.response.out.write(json.dumps(ret))

	def get_db_info(self, game):
		name = self.request.get('name')
		roomId = self.request.get('id')
		if name:
			game.game = model.Game.gql('where name=:1', name).get()
		elif roomId and cah_game.is_int(roomId):
			game.game = ndb.Key('Game', int(roomId)).get()
		game.player = self.get_player(add_player=False)
		if game.game and game.game.current_round:
			game.current_round = game.game.current_round.get()
		elif game.game:
			game.current_round = model.Round()
			game.current_round.put()
			game.game.current_round = game.current_round.key
			logging.info(str(game.game.current_round))

	def list_all(self):
		games = model.Game.query().fetch(1000)
		ret = {}
		player = self.get_player()
		ret['games'] = [model.Game.to_json(g) for g in games]
		if player:
			ret['user'] = model.Player.to_json(player)
		elif not users.get_current_user():
			ret['login_url'] = users.create_login_url() 
		self.response.out.write(json.dumps(ret))

	def post(self):
		game = cah_game.Game()
		self.get_db_info(game)
		action = self.request.get('action')
		
		if action == 'list_all':
			return self.list_all()
		elif action == 'info':
			return self.game_info(game)
		
		user = users.get_current_user()
		if not user:
			return self.need_login()

		if action == 'add_room':
			return self.add_room(game)
		if action == 'next':
			return self.next(game)
		elif action == 'add_pick':
			return self.add_pick(game)
		elif action == 'join_room':
			return self.join_room(game)
		elif action == 'leave_room':
			return self.leave_room(game)
		self.bad_request('Action not recognized', game=game)