define [
    'angular'
    'underscore'
    'underscoreString'
    'plottings'
    'angles'
    'angularBootstrap'
    'ngInfiniteScroll'
    'models',
], (angular, _, _s, plottings) ->
    _.mixin _s.exports()

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

        $scope.tasks = new Tasks 20,
            withViolations: true
            self: true
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

    ProjectCtrl = ($scope, $http, $routeParams, Tasks) ->
        projectName = _.sprintf '%s/%s', $routeParams['owner'], $routeParams['name']
        projectUrl = _.sprintf '/api/v1/projects/project/%s/', projectName

        loadProject = =>
            $http.get(projectUrl).success (data) =>
                $scope.project = data
                if not $scope.branches
                    $scope.branches = data.branches
        loadProject()

        $scope.$watch 'branch', (branch) =>
            $scope.tasks = new Tasks 20,
                withViolations: true
                project: projectName
                branch: branch
            $scope.tasks.load()

        $scope.toggleBadgeHelp = =>
            $scope.showBadgeHelp =
                if $scope.showBadgeHelp then false else true

        $scope.regenerateToken = =>
            $scope.project.token = ''
            $http.put(projectUrl, $scope.project).success =>
                loadProject()

        $scope.domain = window.domain
    module.controller 'ProjectCtrl', [
        '$scope', '$http', '$routeParams', 'Tasks', ProjectCtrl,
    ]

    IndexCtrl: IndexCtrl
    DashboardCtrl: DashboardCtrl
    ManageCtrl: ManageCtrl
    ProjectCtrl: ProjectCtrl
