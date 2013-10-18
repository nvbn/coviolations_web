define ['angular', 'controllers'], (angular) ->
    angular.module('coviolations', ['coviolations.controllers'])
        .config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
            $routeProvider
                .when '/',
                    redirectTo:
                        if window.isAuthenticated then '/dashboard/' else '/welcome/'
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
                .when '/tasks/:pk/',
                    templateUrl: '/static/views/task.html'
                    controller: 'TaskCtrl'
                .when '/not_found/',
                    templateUrl: '/static/views/not_found.html'
                .when '/access/:task/',
                    templateUrl: '/static/views/access.html'
                    controller: 'AccessCtrl'
                .when '/access/:owner/:name/',
                    templateUrl: '/static/views/access.html'
                    controller: 'AccessCtrl'
                .otherwise
                    redirectTo: '/not_found/'
        ]
