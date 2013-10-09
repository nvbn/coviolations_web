define ['angular', 'controllers'], (angular, controllers) ->
    angular.module('coviolations', ['coviolations.controllers'])
        .config ['$routeProvider', ($routeProvider) ->
            $routeProvider
                .when '/welcome/',
                    templateUrl: '/static/views/index.html'
                    controller: 'IndexCtrl'
                .when '/dashboard/',
                    templateUrl: '/static/views/dashboard.html'
                    controller: 'DashboardCtrl'
                .otherwise
                    redirectTo:
                        if window.isAuthenticated then '/dashboard/' else '/welcome/'
        ]
