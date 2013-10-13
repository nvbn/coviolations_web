define ['angular', 'controllers'], (angular) ->
    angular.module('coviolations', ['coviolations.controllers'])
        .config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
            $routeProvider
                .when '/welcome/',
                    templateUrl: '/static/views/index.html'
                    controller: 'IndexCtrl'
                .when '/dashboard/',
                    templateUrl: '/static/views/dashboard.html'
                    controller: 'DashboardCtrl'
                .when '/projects/manage/',
                    templateUrl: '/static/views/manage.html'
                    controller: 'ManageCtrl'
                .when '/projects/:owner/:name/',
                    templateUrl: '/static/views/project.html'
                    controller: 'ProjectCtrl'
                .otherwise
                    redirectTo:
                        if window.isAuthenticated then '/dashboard/' else '/welcome/'
        ]
