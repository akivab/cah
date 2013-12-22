'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('cahApp.services', [])
.factory('AppCtrl', function($http) {
	var AppCtrl = function() {
		this.do_action = function(type, data) {
			var reqData = { 'action': type };
			var reqObj = {
				method: 'POST',
				url: '/game',
			};
			if (data) {
				angular.extend(reqData, data);
			}
			reqObj['params'] = reqData;
			return $http(reqObj)
		};
	};
	return new AppCtrl();
});