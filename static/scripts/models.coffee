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
                @loadLock = false

            load: (callback=->@) ->
                if @canLoad
                    if @loadLock
                        setTimeout 100, => @load(callback)
                    else
                        @loadLock = true
                        $http.get(@getUrl()).success (data) =>
                            @onLoaded(data, callback)
                            @loadLock = false
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

            onLoaded: (data, callback) ->
                _.each data.objects, (item) =>
                    @items.push @prepareItem item
                if data.meta.total_count <= @offset
                    @canLoad = false
                callback.call @

            prepareItem: (item) ->
                item.created = item.created.replace('T', ' ').slice(0, -7)
                if item.commit.inner
                    item.lastCommit = _.last item.commit.inner
                    if item.commit.inner.length > 3
                        item.lastCommits = _.last item.commit.inner, 3
                        item.commitsToExpand = item.commit.inner.length - 3
                    else
                        item.lastCommits = item.commit.inner
                        item.commitsToExpand = 0
                else
                    item.lastCommit = item.commit
                    item.lastCommits = []
                    item.commitsToExpand = 0
                return item

            getByCid: (cid) ->
                (_.last @items, 30).reverse()[cid]
    module.factory 'Tasks', getTaskModel

    getTaskModel: getTaskModel
