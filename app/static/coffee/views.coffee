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
            popover: '#project-task-line-popover-tmpl'
        tagName: 'tr'

        render: ->
            context = _.extend
                showProjectName: @options.showProjectName
            , @model.attributes

            @$el.html @template context

            if @model.get('status') == STATUS_SUCCESS
                @$el.addClass 'success'

            if @model.get('status') == STATUS_FAILED
                @$el.addClass 'danger'

            @$el.find('.js-commit-name').popover
                html: true
                trigger: 'hover'
                content: @popover @model.attributes
                title: @model.get('commit').summary
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
