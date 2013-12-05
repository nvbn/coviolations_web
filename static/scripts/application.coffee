define ['angular', 'angularRoute', 'controllers'], (angular) ->
    getFirstPage = ->
        if window.isAuthenticated
            '/user/' + window.user + '/'
        else
            '/welcome/'

    app = angular.module('coviolations', ['ngRoute', 'coviolations.controllers'])
        .config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
            $routeProvider
                .when '/',
                    redirectTo: getFirstPage()
                .when '/welcome/',
                    templateUrl: '/static/views/index.html'
                    controller: 'IndexCtrl'
                .when '/projects/manage/',
                    templateUrl: '/static/views/manage.html'
                    controller: 'ManageCtrl'
                .when '/projects/:owner/:name/',
                    templateUrl: '/static/views/project.html'
                    controller: 'ProjectCtrl'
                .when '/tasks/:pk/',
                    templateUrl: '/static/views/task.html'
                    controller: 'TaskCtrl'
                .when '/user/:user/',
                    templateUrl: '/static/views/dashboard.html'
                    controller: 'UserPageCtrl'
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

    app.run ($rootScope) ->
        $rootScope.getId = (obj) -> obj._id if obj
