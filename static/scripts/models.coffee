define ['angular', 'underscore'], (angular, _) ->
    module = angular.module 'coviolations.models', []

    module.factory 'Tasks', ($http) ->
        class Tasks
            ### Tasks model ###

            constructor: (@limit=20, @withViolations=false, @self=true) ->
                @items = []
                @canLoad = true
                @offset = 0

            load: ->
                if @canLoad
                    $http.get(@getUrl()).success _.bind @onLoaded, @
                    @offset += @limit

            getUrl: ->
                [
                    '/api/v1/tasks/task/?with_violations=',
                    @withViolations, '&self=', @self, '&limit=',
                    @limit, '&offset=', @offset,
                ].join('')

            onLoaded: (data) ->
                _.each data.objects, (item) =>
                    @items.push @prepareItem item
                if data.meta.total_count < @offset
                    @canLoad = false

            prepareItem: (item) ->
                item.created = item.created.replace('T', ' ').slice(0, -7)
                item
