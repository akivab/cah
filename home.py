import controller
import webapp2

app = webapp2.WSGIApplication([
    ('/', controller.MainController),
    ('/game', controller.GameController),
    ('/player', controller.PlayerController)
], debug=True)