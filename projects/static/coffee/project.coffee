window.coviolations ?=
    views: {}
    models: {}

STATUS_NEW = 0
STATUS_SUCCESS = 1
STATUS_FAILED = 2


$ ->
    NProgress.start()
    NProgress.inc()

    app = window.coviolations

    class PlotData
        constructor: ->
            @violations = {}

        push: (violationName, plotName, plotValue, id) ->
            @violations[violationName] ?=
                ids: []
                plots: {}
            @violations[violationName].plots[plotName] ?= []

            @violations[violationName].plots[plotName].push [id, plotValue]
            @violations[violationName].ids.push id

        normalise: ->
            _.each _.keys(@violations), (name) =>
                _.each _.keys(@violations[name].plots), (plotName) =>
                    @violations[name].plots[plotName] =
                        _.map @violations[name].ids, (id) =>
                            plot = _.find @violations[name].plots[plotName], (plot) =>
                                plot[0] == id
                            if plot and plot[1]
                                parseInt(plot[1], 10)
                            else
                                0


    class PlotColorer
        constructor: ->
            @colors = [
                    strokeColor : "#5cb85c"
                ,
                    strokeColor : "#428bca"
                ,
                    strokeColor : "#f0ad4e"
                ,
                    strokeColor : "#d9534f"
                ,
                    strokeColor : "#5bc0de"
            ]

        getColor: ->
            color = _.first @colors
            @colors = _.rest @colors
            @colors.push color

            color

    renderPage = =>
        collection = new app.models.TaskCollection()
        collection.fetch
            data:
                limit: 0
                project: window.project
                with_violations: true
            success: (collection) ->
                view = new app.views.TaskLineListView
                    el: $('.js-task-line-list')
                    collection: collection
                    showProjectName: false

                view.on 'renderFinished', =>
                    NProgress.inc()

                view.render()

                data = new PlotData

                collection.each (task) =>
                    _.each task.get('violations', []), (violation) ->
                        if violation.plot
                            _.each _.pairs(violation.plot), (pair) =>
                                data.push violation.name, pair[0], pair[1], task.get('resource_uri')

                data.normalise()

                NProgress.inc()

                $('.js-charts-holder').empty()

                _.each _.keys(data.violations), (name) =>
                    colorer = new PlotColorer

                    colorNames = []

                    datasets = _.map _.pairs(data.violations[name].plots), (plotPair) =>
                        plotName = plotPair[0]
                        plot = plotPair[1]

                        preparedPlot = _.flatten [_.map(_.range(30), -> 0), [plot.reverse()]]

                        color = colorer.getColor()
                        colorNames.push([plotName, color])

                        _.extend
                            data: _.last preparedPlot, 30
                        , color

                    view = new app.views.TrendChartView
                        labels: _.map _.range(30), -> ''
                        datasets: datasets
                        name: name
                        colorNames: colorNames
                    view.render()
                    view.$el.appendTo $('.js-charts-holder')
                    NProgress.inc()

                NProgress.done()

    renderPage()
    window.push.on 'task', (task) =>
        if task.project == window.project
            renderPage()

    prettyPrint()
