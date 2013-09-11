window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

STATUS_NEW = 0
STATUS_SUCCESS = 1
STATUS_FAILED = 2

$ ->
    app = window.coviolations

    class LazyTemplatedView extends Backbone.View
        ### Lazy templated view ###
        templates: {}

        initialize: ->
            ### Init all templates ###
            _.each _.keys(@templates), (name) =>
                @[name] = _.template($(@templates[name]).html())


    class app.views.TaskLineView extends LazyTemplatedView
        ### Task line view ###
        templates:
            template: '#project-task-line-tmpl'
        tagName: 'tr'

        render: ->
            ### Render task line and set status class ###
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
            ### Render task line list ###
            if @collection.meta.total_count
                @waitRendering = @collection.length
                @$el.empty()
                @collection.each $.proxy @_renderTaskLine, @
            else
                @$el.find('td').html 'No tasks found'
                @trigger 'renderFinished'

        _renderTaskLine: (task) ->
            ### Render single task line ###
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


    class app.views.TrendChartView extends LazyTemplatedView
        ### Trend charts view ###
        tagName: 'div'
        templates:
            template: '#project-violation-plot-tmpl'
        attributes:
            'class': 'col-lg-4'

        render: ->
            ### Render trand chart on canvas ###
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
            ### Bind change event ###
            super
            @model.on 'change', $.proxy @render, @

        render: ->
            ### Render project line ###
            @$el.html @template @model.attributes
            @trigger 'renderFinished'

        enable: (e) ->
            ### Enable project ###
            e.preventDefault()
            @model.set 'is_enabled', true
            @model.save()

        disable: (e) ->
            ### Disable project ###
            e.preventDefault()
            @model.set 'is_enabled', false
            @model.save()


    class app.views.ManageProjectsView extends Backbone.View
        ### Manage projects view ###
        tagName: 'table'

        render: ->
            ### Render manage project table ###
            @$el.empty()
            @waitRendering = @collection.length
            @collection.each $.proxy @renderLine, @

        renderLine: (model) ->
            ### Render single project line ###
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
            ### Render statistic chart on canvas ###
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
            ### Render index page ###
            @initProgressBar()

            @renderProjects()
            @renderTasks()
            @renderFeed()
            @renderChart()

            @initReloads()
            prettyPrint()

        initProgressBar: ->
            ### Init progress bar and subscribe on updates ###
            NProgress.start()
            NProgress.inc()

            waitRendering = 3
            @on 'renderPartFinished', =>
                NProgress.inc()
                waitRendering -= 1
                if waitRendering <= 0
                    NProgress.done()

        initReloads: ->
            ### Subscribe to push for views rerendering ###
            @options.push.on 'project', =>
                @renderProjects()

            @options.push.on 'task', =>
                @renderTasks()
                @renderFeed()

        renderProjects: ->
            ### Render projects for authenticated ###
            if @options.userId
                @options.projectCollection.fetch
                    data:
                        limit: 0
                    success: $.proxy @_renderManageProjectsView, @
            else
                @_renderProjectsFinished()

        _renderManageProjectsView: (collection) ->
            ### Render manage projects view ###
            if collection.meta.total_count
                projectView = new app.views.ManageProjectsView
                    el: @$el.find('.js-enabled-projects')
                    collection: collection
                projectView.on 'renderFinished', $.proxy @_renderProjectsFinished, @

                projectView.render()
            else
                @$el.find('.js-enabled-projects td').html 'No projects found'

        _renderProjectsFinished: ->
            ### Send projects view rendered ###
            @trigger 'renderPartFinished', 'projects'

        renderTasks: ->
            ### Render tasks for authenticated ###
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
            ### Render task line view ###
            taskView = new app.views.TaskLineListView
                el: @$el.find('.js-last-tasks')
                collection: collection
                showProjectName: true
            taskView.on 'renderFinished', $.proxy @_renderTasksFinished, @
            taskView.render()

        _renderTasksFinished: ->
            ### Send tasks view rendered ###
            @trigger 'renderPartFinished', 'tasks'

        renderFeed: ->
            ### Render tasks feed ###
            @options.taskCollection.fetch
                data:
                    limit: 10
                    with_violations: true
                success: $.proxy @renderFeedView, @

        renderFeedView: (collection) ->
            ### Render task line list ###
            taskView = new app.views.TaskLineListView
                el: @$el.find('.js-tasks-feed')
                collection: collection
                showProjectName: true
            taskView.on 'renderFinished', =>
                @trigger 'renderPartFinished', 'feed'
            taskView.render()

        renderChart: ->
            ### Render statistic chart ###
            chartView = new app.views.StatisticView
                el: @$el.find('#js-statistic')
                successCount: @options.successPercent
                failedCount: @options.failedPercent
            chartView.render()


    class app.views.ManageProjectsPageView extends Backbone.View
        ### Manage projects page view ###
        tagName: 'div'

        render: ->
            ### Render manage projcts page ###
            @initProgressBar()
            @renderManageProjects()

        renderManageProjects: ->
            ### Render manage projects table ###
            @options.collection.fetch
                data:
                    limit: 0
                    fetch: true
                success: $.proxy @_renderManageProjectsView, @

        _renderManageProjectsView: (collection) ->
            ### Render manage projects view ###
            view = new app.views.ManageProjectsView
                el: @$el.find('.js-manage-projects')
                collection: collection
            view.on 'renderFinished', =>
                @trigger 'renderFinished'

            view.render()

        initProgressBar: ->
            ### Init progress bar and subscribe to updates ###
            NProgress.start()
            NProgress.inc()

            @on 'renderFinished', ->
                NProgress.done()


    class app.views.ProjectPageView extends Backbone.View
        ### Project page view

        Required options:
            project
            collection
            push
        ###
        tagName: 'div'

        render: ->
            ### Render project page view ###
            @initProgressBar()
            @initReloads()

            @options.collection.fetch
                data:
                    limit: 0
                    project: @options.project
                    with_violations: true
                success: (collection) =>
                    @options.collection = collection
                    @renderTaskLines()

                    @plotData = @getPlotData()
                    @trigger 'renderPartFinished', 'plotData'

                    @renderCharts()
                    prettyPrint()

        initProgressBar: ->
            ### Init progress bar and subscribe to updates ###
            NProgress.start()
            NProgress.inc()

            @on 'renderPartFinished', ->
                NProgress.inc()

            @on 'renderFinished', ->
                NProgress.done()

        initReloads: ->
            ### Init view reloads on push ###
            @options.push.on 'task', (task) =>
                if task.project == @options.project
                    @renderTaskLines()

        renderTaskLines: ->
            ### Render task line view ###
            view = new app.views.TaskLineListView
                el: @$el.find('.js-task-line-list')
                collection: @options.collection
                showCommitSummary: true

            view.on 'renderFinished', =>
                @trigger 'renderPartFinished', 'taskLine'

            view.render()

        getPlotData: ->
            ### Prepare data for plotting ###
            data = new app.plotting.PlotData
            @options.collection.each (task) =>
                violations = _.filter task.get('violations', []), (violation) ->
                    _.isObject violation.plot

                _.each violations, (violation) =>
                    _.each _.pairs(violation.plot), (pair) =>
                        data.push(
                            violation.name,
                            pair[0],
                            pair[1],
                            task.get('resource_uri')
                        )
            data.normalise()

            data

        renderCharts: ->
            ### Render trend charts ###
            @$el.find('.js-charts-holder').empty()

            _.each _.keys(@plotData.violations), (name) =>
                colorer = new app.plotting.PlotColorer

                colorNames = []

                datasets = _.chain(@plotData.violations[name].plots)
                    .pairs()
                    .map (plotPair) =>
                        plotName = plotPair[0]
                        plot = plotPair[1]
                        preparedPlot = _.flatten [_.map(_.range(30), -> 0), [plot.reverse()]]
                        preparedPlot = _.last preparedPlot, 30

                        color = colorer.getColor()
                        colorNames.push([plotName, color])

                        _.extend
                            data: preparedPlot
                        , color
                    .value()

                if datasets.length
                    @_renderTrendChartView datasets, colorNames
            @trigger 'renderFinished'

        _renderTrendChartView: (datasets, colorNames) ->
            ### Render single trend chart ###
            view = new app.views.TrendChartView
                labels: _.map _.range(30), -> ''
                datasets: datasets
                name: name
                colorNames: colorNames
            view.render()
            view.$el.appendTo @$el.find('.js-charts-holder')

            @trigger 'renderPartFinished', 'trandChart'
