define ['angular', 'angles', 'angularBootstrap'], (angular) ->
    module = angular.module 'coviolations.controllers', [
        'angles'
        'ui.bootstrap'
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

    DashboardCtrl = ($scope, $http) ->
        $http.get('/api/v1/projects/project/?limit=0').success (data) =>
                $scope.projects = data.objects
                console.log $scope
    module.controller 'DashboardCtrl', [
        '$scope', '$http', DashboardCtrl,
    ]
