define ['angular', 'underscore'], (angular, _) ->
    module = angular.module 'coviolations.models', []

    getTaskModel = ($http) ->
        class Tasks
            ### Tasks model ###

            constructor: (@limit=20, @options) ->
                @items = []
                @canLoad = true
                @offset = 0

            load: ->
                if @canLoad
                    $http.get(@getUrl()).success _.bind @onLoaded, @
                    @offset += @limit

            getUrl: ->
                base = [
                    '/api/v1/tasks/task/',
                    '?limit=', @limit, '&offset=', @offset,
                ]
                if @options.withViolations
                    base.push '&with_violations='
                    base.push @options.withViolations
                if @options.self
                    base.push '&self='
                    base.push @options.self
                if @options.project
                    base.push '&project='
                    base.push @options.project
                base.join('')

            onLoaded: (data) ->
                _.each data.objects, (item) =>
                    @items.push @prepareItem item
                if data.meta.total_count <= @offset
                    @canLoad = false

            prepareItem: (item) ->
                item.created = item.created.replace('T', ' ').slice(0, -7)
                item
    module.factory 'Tasks', getTaskModel

    getTaskModel: getTaskModel
