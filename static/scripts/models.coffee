define ['angular', 'underscore', 'underscoreString'], (angular, _, _s) ->
    _.mixin _s.exports()

    module = angular.module 'coviolations.models', []

    getTaskModel = ($http) ->
        class Tasks
            ### Tasks model ###

            constructor: (@limit=20, @options={}) ->
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
                @addOption base, 'withViolations', 'with_violations'
                @addOption base, 'self'
                @addOption base, 'project'
                @addOption base, 'branch'
                base.join('')

            addOption: (base, option, uriName=option) ->
                if @options[option]
                    base.push _.sprintf '&%s=', uriName
                    base.push @options[option]

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
