window.coviolations ?=
    views: {}
    models: {}

STATUS_NEW = 0
STATUS_SUCCESS = 1
STATUS_FAILED = 2

$ ->
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
                            parseInt(plot[1], 10) or 0


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
            view.render()

            data = new PlotData

            collection.each (task) =>
                _.each task.get('violations', []), (violation) ->
                    if violation.plot
                        _.each _.pairs(violation.plot), (pair) =>
                            data.push violation.name, pair[0], pair[1], task.get('resource_uri')

            data.normalise()

            _.each _.keys(data.violations), (name) =>
                datasets = _.map _.values(data.violations[name].plots), (plot) ->
                    preparedPlot = _.flatten [_.map(_.range(10), -> 0), [plot.reverse()]]

                    console.log preparedPlot

                    data: _.last preparedPlot, 10
                    fillColor : "rgba(151,187,205,0.5)"
                    strokeColor : "rgba(151,187,205,1)"
                    pointColor : "rgba(151,187,205,1)"
                    pointStrokeColor : "#fff"

                view = new app.views.TrendChartView
                    labels: _.range(10)
                    datasets: datasets
                    name: name
                view.render()
                view.$el.appendTo $('.js-charts-holder')
