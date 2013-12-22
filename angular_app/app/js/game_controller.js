var GameController = function($scope, $location, $routeParams, AppCtrl) {
	AppCtrl.do_action('info', { id: $routeParams.roomId }).success(function(data){
		if (!data.game) {
			$location.path('/');
		}
		$scope.user = data.user;
		$scope.game = data.game;
		$scope.login_url = data.login_url;
	});

	$scope.join_room = function() {
		AppCtrl.do_action('join_room', { id: $routeParams.roomId }).success(function(data){
			if (data.error) {
				alert(data.reason);
				return;
			}
			$scope.game = data.game;
			$scope.user = data.user;
		})
	};

	$scope.leave_room = function() {
		AppCtrl.do_action('leave_room', { id: $routeParams.roomId }).success(function(data){
			if (data.error) {
				if (data.reason == 'No game.') {
					$location.path('/');
				} else {
					alert(data.reason);
				}
				return;
			}
			$scope.game = data.game;
			$scope.user = data.user;
		});
	};


	$scope.is_in_room = function() {
		return $scope.user && $scope.user.current_game == $routeParams.roomId;
	};
};

angular.module('cahApp.gameController', []).controller('GameCtrl',
	['$scope',
	 '$location',
	 '$routeParams',
	 'AppCtrl', GameController]);