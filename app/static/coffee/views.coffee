window.coviolations ?=
    views: {}
    models: {}

STATUS_NEW = 0
STATUS_SUCCESS = 1
STATUS_FAILED = 2

$ ->
    app = window.coviolations

    class LazyTemplatedView extends Backbone.View
        ### lazy templated view ###
        templates: {}

        initialize: ->
            _.each _.keys(@templates), (name) =>
                @[name] = _.template($(@templates[name]).html())


    class app.views.TaskLineView extends LazyTemplatedView
        ### Task line view ###
        templates:
            template: '#project-task-line-tmpl'
        tagName: 'tr'

        render: ->
            context = _.extend
                showProjectName: @options.showProjectName
                showCommitSummary: @options.showCommitSummary
            , @model.attributes

            @$el.html @template context

            if @model.get('status') == STATUS_SUCCESS
                @$el.addClass 'success'

            if @model.get('status') == STATUS_FAILED
                @$el.addClass 'danger'

            @trigger 'renderFinished'


    class app.views.TaskLineListView extends Backbone.View
        ### Task line list view ###
        tagName: 'table'

        render: ->
            if @collection.meta.total_count
                @waitRendering = @collection.length

                @$el.empty()
                @collection.each (task) =>
                    view = new app.views.TaskLineView
                        model: task
                        showProjectName: @options.showProjectName
                        showCommitSummary: @options.showCommitSummary

                    view.on 'renderFinished', =>
                        @waitRendering -= 1

                        if @waitRendering == 0
                            @trigger 'renderFinished'

                    view.render()
                    @$el.append(view.$el)
            else
                @$el.find('td').html 'No tasks found'
                @trigger 'renderFinished'


    class app.views.TrendChartView extends LazyTemplatedView
        ### Trend charts view ###
        tagName: 'div'
        templates:
            template: '#project-violation-plot-tmpl'
        attributes:
            'class': 'col-lg-4'

        render: ->
            @$el.html @template
                name: @options.name
                colorNames: @options.colorNames
            context = @$el.find('canvas')[0].getContext '2d'
            @chart = new Chart(context).Line
                labels: @options.labels
                datasets: @options.datasets
            ,
                pointDot: false
                datasetFill: false
                animation: false


    class app.views.ProjectLineView extends LazyTemplatedView
        ### Project line view ###
        events:
            'click .js-yes': 'enable'
            'click .js-no': 'disable'
        templates:
            template: '#manage-project-line-tmpl'
        tagName: 'tr'

        initialize: ->
            super
            @model.on 'change', $.proxy @render, @

        render: ->
            @$el.html @template @model.attributes
            @trigger 'renderFinished'

        enable: (e) ->
            e.preventDefault()
            @model.set 'is_enabled', true
            @model.save()

        disable: (e) ->
            e.preventDefault()
            @model.set 'is_enabled', false
            @model.save()


    class app.views.ManageProjectsView extends Backbone.View
        ### Manage projects view ###
        tagName: 'table'

        render: ->
            @$el.empty()
            @waitRendering = @collection.length
            @collection.each $.proxy @renderLine, @

        renderLine: (model) ->
            lineView = new app.views.ProjectLineView
                model: model
            lineView.on 'renderFinished', =>
                @waitRendering -= 1
                if @waitRendering == 0
                    @trigger 'renderFinished'

            lineView.render()
            @$el.append lineView.$el


    class app.views.StatisticView extends LazyTemplatedView
        ### Statistic view ###
        tagName: 'canvas'
        templates:
            template: '#index-statistic-tmpl'
        successColor: "#5cb85c"
        failedColor: "#d9534f"

        render: ->
            @$el.html @template
                successColor: @successColor
                failedColor: @failedColor
                success: @options.successCount
                failed: @options.failedCount

            context = @$el.find('canvas')[0].getContext '2d'
            @chart = new Chart(context).Pie [
                    value: @options.successCount
                    color: @successColor
                ,
                    value: @options.failedCount
                    color: @failedColor
            ],
                animation: false


    class app.views.IndexPageView extends Backbone.View
        ### Index page view

        Required options:
            userId
            projectCollection
            taskCollecion
            successPercent
            failedPercent
            push

        Events:
            renderPartFinished: partName['projects', 'tasks', 'feed']
        ###
        tagName: 'div'

        render: ->
            @initProgressBar()

            @renderProjects()
            @renderTasks()
            @renderFeed()
            @renderChart()

            @initReloads()
            prettyPrint()

        initProgressBar: ->
            NProgress.start()
            NProgress.inc()

            waitRendering = 3
            @on 'renderPartFinished', =>
                NProgress.inc()
                waitRendering -= 1
                if waitRendering <= 0
                    NProgress.done()

        initReloads: ->
            @options.push.on 'project', =>
                @renderProjects()

            @options.push.on 'task', =>
                @renderTasks()
                @renderFeed()

        renderProjects: ->
            if @options.userId
                @options.projectCollection.fetch
                    data:
                        limit: 0
                    success: $.proxy @_renderManageProjectsView, @
            else
                @_renderProjectsFinished()

        _renderManageProjectsView: (collection) ->
            if collection.meta.total_count
                projectView = new app.views.ManageProjectsView
                    el: @$el.find('.js-enabled-projects')
                    collection: collection
                projectView.on 'renderFinished', $.proxy @_renderProjectsFinished, @

                projectView.render()
            else
                @$el.find('.js-enabled-projects td').html 'No projects found'

        _renderProjectsFinished: ->
            @trigger 'renderPartFinished', 'projects'

        renderTasks: ->
            if @options.userId
                @options.taskCollection.fetch
                    data:
                        limit: 20
                        with_violations: true
                        self: true
                    success: $.proxy @_renderTaskLineView, @

            else
                @_renderTasksFinished

        _renderTaskLineView: (collection) ->
            taskView = new app.views.TaskLineListView
                el: @$el.find('.js-last-tasks')
                collection: collection
                showProjectName: true
            taskView.on 'renderFinished', $.proxy @_renderTasksFinished, @
            taskView.render()

        _renderTasksFinished: ->
            @trigger 'renderPartFinished', 'tasks'

        renderFeed: ->
            @options.taskCollection.fetch
                data:
                    limit: 10
                    with_violations: true
                success: $.proxy @renderFeedView, @

        renderFeedView: (collection) ->
            taskView = new app.views.TaskLineListView
                el: @$el.find('.js-tasks-feed')
                collection: collection
                showProjectName: true
            taskView.on 'renderFinished', =>
                @trigger 'renderPartFinished', 'feed'
            taskView.render()

        renderChart: ->
            chartView = new app.views.StatisticView
                el: @$el.find('#js-statistic')
                successCount: @options.successPercent
                failedCount: @options.failedPercent
            chartView.render()
