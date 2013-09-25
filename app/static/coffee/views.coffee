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
            context = _.extend
                editable: @options.editable
            , @model.attributes

            @$el.html @template context
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
            if @collection.length == 0
                @trigger 'renderFinished'
            else
                @waitRendering = @collection.length
                @collection.each $.proxy @renderLine, @

        renderLine: (model) ->
            ### Render single project line ###
            lineView = new app.views.ProjectLineView
                model: model
                editable: @options.editable
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


    class app.views.GenerateTokenAlertView extends LazyTemplatedView
        ### Generate token alert view ###
        tagName: 'div'
        attributes:
            'class': 'alert alert-danger fade in generate-token-alert'
        templates:
            template: '#project-generate-token-alert-tmpl'
        events:
            'click .js-no': 'sayNo'
            'click .js-yes': 'sayYes'

        render: ->
            ### Render alert ###
            @$el.html @template()

        sayNo: ->
            ### Say no ###
            @$el.remove()

        sayYes: ->
            ### Say yes ###
            @$el.remove()
            @trigger 'yes'


    class app.views.GenerateTokenView extends LazyTemplatedView
        ### Generate token view ###
        tagName: 'form'
        templates:
            template: '#project-generate-token-tmpl'
        events:
            'click button': 'showAlert'

        render: ->
            ### Render regenrate page ###
            @$el.html @template()
            @$el.find('button').tooltip
                title: 'Regenerate token'

        showAlert: (e) ->
            ### Show alert ###
            e.preventDefault()
            alertView = new app.views.GenerateTokenAlertView
            alertView.render()
            alertView.on 'yes', $.proxy @regenerate, @
            @$el.append(alertView.$el)

        regenerate: ->
            @$el.submit()


    class app.views.IndexHowToView extends Backbone.View
        ### Index how-to view ###
        tagName: 'div'
        events:
            'click .how-to-btn ': 'changeHowTo'

        changeHowTo: (e) ->
            ### Change displayed how to ###
            @$el.find('.js-how-to-part').addClass 'hidden'
            @$el.find($(e.currentTarget).data('show')).removeClass 'hidden'


    class app.views.SelectBranchView extends Backbone.View
        ### Select branch view ###
        tagName: 'select'
        events:
            'change': 'onChange'

        onChange: ->
            @trigger 'branchChanged', @$el.val()


    class app.views.LinkToSourceView extends Backbone.View
        ### Link to source view ###
        tagName: 'a'
        hrefTemplate: _.template 'https://github.com/<%= project %>/blob/<%= commit %>/<%= file %><% if (line){ %>#L<%= line %><% } %>'

        render: ->
            @$el.attr 'href', @getHref()

        getHref: ->
            @hrefTemplate
                project: @options.project
                commit: @options.commit
                file: @$el.data 'file-name'
                line: @$el.data 'line'


    class app.views.ProjectSettingsView extends LazyTemplatedView
        ### Project settings view ###
        tagName: 'div'
        templates:
            template: '#project-settings-tmpl'
        events:
            'click .js-enabled-line button': 'changeEnabled'
            'click .js-comment-line button': 'changeComment'

        initialize: ->
            ### Bind change event ###
            super
            @model.on 'change', $.proxy @render, @

        render: ->
            @$el.html @template @model.attributes

        changeEnabled: (e) ->
            ### Change is_enabled of project ###
            @model.set 'is_enabled', $(e.currentTarget).hasClass 'js-yes'
            @model.save()

        changeComment: (e) ->
            ### Change comment_from_owner_account attribute ###
            @model.set 'comment_from_owner_account',
                $(e.currentTarget).hasClass 'js-yes'
            @model.save()


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
            @renderHowTo()

            @initReloads()
            prettyPrint()

        initProgressBar: ->
            ### Init progress bar and subscribe on updates ###
            NProgress.start()
            NProgress.inc()

            waitRendering = if @options.userId then 3 else 1
            @on 'renderPartFinished', =>
                NProgress.inc()
                waitRendering -= 1
                if waitRendering <= 0
                    NProgress.done()
            @on 'renderReloaded', NProgress.done

        initReloads: ->
            ### Subscribe to push for views rerendering ###
            @options.push.on 'project', =>
                @renderProjects()
                @trigger 'renderReloaded'

            @options.push.on 'task', =>
                @renderTasks()
                @renderFeed()
                @trigger 'renderReloaded'

        renderHowTo: ->
            ### Render how to view ###
            view = new app.views.IndexHowToView
                el: @$el.find('.js-how-to')
            view.render()

        renderProjects: ->
            ### Render projects for authenticated ###
            if @options.userId
                @options.projectCollection.fetch
                    data:
                        limit: 0
                    reset: true
                    success: $.proxy @_renderManageProjectsView, @
            else
                @_renderProjectsFinished()

        _renderManageProjectsView: (collection) ->
            ### Render manage projects view ###
            if collection.meta.total_count
                projectView = new app.views.ManageProjectsView
                    el: @$el.find('.js-enabled-projects')
                    collection: collection
                    editable: false
                projectView.on 'renderFinished', $.proxy @_renderProjectsFinished, @

                projectView.render()
            else
                @$el.find('.js-enabled-projects td').html 'No projects found'
                @_renderProjectsFinished()

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
                    reset: true
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
                editable: true
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
            @renderToken()
            @renderTasks()
            @renderSelectBranch()
            @renderSettings()
            @renderMenu()

        renderSelectBranch: ->
            view = new app.views.SelectBranchView
                el: @$el.find('.js-select-branch')
            view.render()
            view.on 'branchChanged', (branch) =>
                @branch = branch
                @reloadView()

        renderTasks: ->
            @fetchCollection =>
                @renderTaskLines()

                @plotData = @getPlotData()
                @trigger 'renderPartFinished', 'plotData'

                @renderCharts()
                prettyPrint()

        renderMenu: ->
            @minOffset = @$el.find('.js-options').offset().top
            @minOffset -= @$el.find('.js-project-menu').height()
            $(window).scroll $.proxy @onScroll,  @

        onScroll: ->
            if $(window).scrollTop() > @minOffset
                @$el.find('.js-project-menu').css 'display', 'block'
            else
                @$el.find('.js-project-menu').css 'display', 'none'

        renderSettings: ->
            ### Render settings for author ###
            holder = @$el.find('.js-project-settings')
            if holder.length
                project = new app.models.UserProject
                    id: @options.projectId
                project.fetch
                    success: =>
                        view = new app.views.ProjectSettingsView
                            model: project
                            el: holder
                        view.render()

        initProgressBar: ->
            ### Init progress bar and subscribe to updates ###
            NProgress.start()
            NProgress.inc()

            @on 'renderPartFinished', NProgress.inc
            @on 'renderFinished', NProgress.done
            @on 'renderReload', NProgress.done

        initReloads: ->
            ### Init view reloads on push ###
            @options.push.on 'task', (task) =>
                if task.project == @options.project
                    @reloadView()

        reloadView: ->
            @renderTasks()
            @trigger 'renderReload'

        fetchCollection: (callback) ->
            ### Fetch collection ###
            data =
                limit: 0
                project: @options.project
                with_violations: true

            if @branch
                data.branch = @branch

            @options.collection.fetch
                data: data
                reset: true
                success: (collection) =>
                    @collection = collection
                    callback.call @, collection

        renderToken: ->
            ### Render generate token view ###
            if @$el.find('.js-generate-token').length
                view = new app.views.GenerateTokenView
                    model: @
                    el: $('.js-generate-token')
                view.render()

        renderTaskLines: ->
            ### Render task line view ###
            view = new app.views.TaskLineListView
                el: @$el.find('.js-task-line-list')
                collection: @collection
                showCommitSummary: true

            view.on 'renderFinished', =>
                @trigger 'renderPartFinished', 'taskLine'

            view.render()

        getPlotData: ->
            ### Prepare data for plotting ###
            data = new app.plotting.PlotData
            @collection.each (task) =>
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
                    @_renderTrendChartView name, datasets, colorNames
            @trigger 'renderFinished'

        _renderTrendChartView: (name, datasets, colorNames) ->
            ### Render single trend chart ###
            if @_datasetHasValues datasets
                view = new app.views.TrendChartView
                    labels: _.map(_.range(30), (-> ''))
                    datasets: datasets
                    name: name
                    colorNames: colorNames
                view.render()
                view.$el.appendTo @$el.find('.js-charts-holder')

            @trigger 'renderPartFinished', 'trandChart'

        _datasetHasValues: (dataset) ->
            ### Is dataset has values? ###
            _.any dataset, (item) ->
                _.any item.data

    class app.views.DetailTaskPageView extends Backbone.View
        ### Task page view ###
        tagName: 'div'
        events:
            'click '

        render: ->
            @$el.find('.js-link-to-source').each (n, el) =>
                view = new app.views.LinkToSourceView
                    project: @options.project
                    commit: @options.commit
                    el: el
                view.render()

            if @$el.find('.js-first-violation').length
                @minOffset = @$el.find('.js-first-violation').offset().top
                @minOffset -= @$el.find('.js-violations-menu').height()
                $(window).scroll $.proxy @onScroll,  @
                @$el.find('pre').addClass 'prettyprint'
                prettyPrint()

        onScroll: ->
            if $(window).scrollTop() > @minOffset
                @$el.find('.js-violations-menu').css 'display', 'block'
            else
                @$el.find('.js-violations-menu').css 'display', 'none'
