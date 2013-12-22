'use strict';


// Declare app level module which depends on filters, and services
angular.module('cahApp', [
  'ngRoute',
  'cahApp.filters',
  'cahApp.services',
  'cahApp.directives',
  'cahApp.controllers'
]).
config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/lobby', {templateUrl: 'partials/lobby.html', controller: 'LobbyCtrl'});
  $routeProvider.when('/game/:roomId', {templateUrl: 'partials/game.html', controller: 'GameCtrl'});
  $routeProvider.otherwise({redirectTo: '/lobby'});
}]);
