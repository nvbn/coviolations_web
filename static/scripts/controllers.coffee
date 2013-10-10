define [
    'angular'
    'underscore'
    'angles'
    'angularBootstrap'
    'ngInfiniteScroll'
    'models',
], (angular, _) ->
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

    ManageCtrl = ($scope, $http) ->
        $scope.loading = true
        $http.get('/api/v1/projects/project/?fetch=true&limit=0').success (data) =>
            $scope.projects = data.objects
            $scope.loading = false
            $scope.$watch 'projects', (newProjects, oldProjects) =>
                _.each newProjects, (project, num) =>
                    if project.is_enabled != oldProjects[num].is_enabled
                        $http.put(project.resource_uri, project)
            , true
    module.controller 'ManageCtrl', [
        '$scope', '$http', ManageCtrl,
    ]

    IndexCtrl: IndexCtrl
    DashboardCtrl: DashboardCtrl
    ManageCtrl: ManageCtrl
