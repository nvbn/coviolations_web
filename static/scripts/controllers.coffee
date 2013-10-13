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
        ### Index page controller ###
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
        ### Dashboard controller ###
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
        ### Manage projects page controller ###
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

    ProjectCtrl = ($scope, $http, $routeParams, $modal, Tasks) ->
        ### Single project page controller ###
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
            $scope.tasks.load =>
                plotData = new plottings.PlotData $scope.tasks.items
                plotData.normalise()
                $scope.charts = plotData.createChartObjects()

        $scope.toggleBadgeHelp = =>
            $scope.showBadgeHelp =
                if $scope.showBadgeHelp then false else true

        $scope.regenerateToken = =>
            $scope.project.token = ''
            $http.put(projectUrl, $scope.project).success =>
                loadProject()

        $scope.showSettings = =>
            $modal.open
                templateUrl: '/static/views/project_settings.html'
                controller: ProjectSettingsCtrl
                resolve:
                    $http: => $http
                    project: => $scope.project

        $scope.domain = window.domain
    module.controller 'ProjectCtrl', [
        '$scope', '$http', '$routeParams', '$modal', 'Tasks', ProjectCtrl,
    ]

    ProjectSettingsCtrl = ($scope, $modalInstance, $http, project) ->
        $scope.project = project
        $scope.close = =>
            $modalInstance.close()
        $scope.$watch 'project', =>
            $http.put($scope.project.resource_uri, $scope.project)
        , true


    TaskCtrl = ($scope, $http, $routeParams) ->
        ### Single task controller ###
        taskUrl = _.sprintf '/api/v1/tasks/task/%s/', $routeParams['pk']

        $http.get(taskUrl).success (data) =>
            $scope.task = data

            projectUrl = _.sprintf '/api/v1/projects/project/%s/', data['project']
            $http.get(projectUrl).success (project) =>
                $scope.project = project
    module.controller 'TaskCtrl', [
        '$scope', '$http', '$routeParams', TaskCtrl,
    ]


    IndexCtrl: IndexCtrl
    DashboardCtrl: DashboardCtrl
    ManageCtrl: ManageCtrl
    ProjectCtrl: ProjectCtrl
    ProjectSettingsCtrl: ProjectSettingsCtrl
    TaskCtrl: TaskCtrl
