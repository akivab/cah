'use strict';

/* Controllers */

var LobbyCtrl = function($scope, $location, AppCtrl) {
	AppCtrl.do_action('list_all').success(function(data){
		$scope.user = data.user;
		$scope.games = data.games;
		$scope.login_url = data.login_url;
		console.log(data);
	});

	$scope.add_room = function() {
		if (!$scope.user) return;
		AppCtrl.do_action('add_room', {'name' : $scope.room_name }).success(
			function(data){
				console.log(data);
				if (data.error) {
					$scope.alert = data.error;
					return;
				}
				$location.path('/game/' + data.game.id);
		});
	};
};

angular.module('cahApp.lobbyController', []).
controller('LobbyCtrl', ['$scope', '$location', 'AppCtrl', LobbyCtrl]);