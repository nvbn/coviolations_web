define [
    'angular'
    'angles'
    'angularBootstrap'
    'ngInfiniteScroll'
    'models',
], (angular) ->
    module = angular.module 'coviolations.controllers', [
        'angles'
        'ui.bootstrap'
        'infinite-scroll'
        'coviolations.models'
    ]
    IndexCtrl = ($scope) ->
        $scope.isAuthenticated = window.isAuthenticated
        $scope.successColor = "#5cb85c"
        $scope.failedColor = "#d9534f"
        $scope.chartData =
            [
                    value: window.successTasks
                    color: $scope.successColor
                ,
                    value: window.failedTasks
                    color: $scope.failedColor
            ]
        $scope.chartOptions =
            animation:false
        $scope.successPercent = window.successTasks
        $scope.failedPercent = window.failedTasks
    module.controller 'IndexCtrl', [
        '$scope', IndexCtrl,
    ]

    DashboardCtrl = ($scope, $http, Tasks) ->
        $http.get('/api/v1/projects/project/?limit=0').success (data) =>
            $scope.projects = data.objects

        $scope.tasks = new Tasks 20, true, true
        $scope.tasks.load()

    module.controller 'DashboardCtrl', [
        '$scope', '$http', 'Tasks', DashboardCtrl,
    ]
