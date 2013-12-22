'use strict';

/* Directives */


angular.module('cahApp.directives', [])
.directive('draggable', function() {
	return {
        restrict:'A',
        link: function(scope, element, attrs) {
        	element.draggable({
        		revert:true,
        		start: function(event, ui) {
        			console.log("start");
        			console.log(event);
        			console.log(ui);
        		},
        		stop: function(event, ui) {
        			console.log("stop");
        			console.log(event);
        			console.log(ui);	
        		}
        	});
        }
      };
    })
.directive('droppable', function($compile) {
	return {
		restrict: 'A',
		link: function(scope,element,attrs){
			element.droppable({
				accept: ".card",
				hoverClass: "drop-hover",
				drop:function(event,ui) {
					console.log("dropped");
					console.log(event);
				}
			});
		}
	};
});
