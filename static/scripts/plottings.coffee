define ['underscore'], (_) ->
    class PlotData
        ### Plot data organizer ###

        constructor: (tasks, @limit=30) ->
            @violations = {}
            @fill tasks

        fill: (tasks) ->
            _.each tasks, (task) =>
                taskViolations = _.filter (task.violations or []), (violation) ->
                    _.isObject violation

                _.each taskViolations, (violation) =>
                    if violation.plot
                         _.each _.pairs(violation.plot), (pair) =>
                            @push(
                                violation.name,
                                pair[0],
                                pair[1],
                                task.resource_uri
                            )

        push: (violationName, plotName, plotValue, id) ->
            ### Push new violation ###
            @violations[violationName] ?=
                ids: []
                plots: {}
            @violations[violationName].plots[plotName] ?= []

            @violations[violationName].plots[plotName].push [id, plotValue]
            @violations[violationName].ids.push id

        normalise: ->
            ### Prepare plot data ###
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

        _preparePlot: (plot) ->
            prepared = _.flatten [_.map(_.range(@limit), -> 0), [plot.reverse()]]
            _.last prepared, @limit

        _checkDatasets: (datasets) ->
            datasets.length and (_.any datasets, (@item) ->
                _.any item.data)

        _createChartObject: (name, datasets, colors) ->
            name: name
            data:
                labels: _.map(_.range(@limit), (-> ''))
                datasets: datasets
            options:
                pointDot: false
                datasetFill: false
                animation: false
            colors: colors

        createChartObjects: ->
            ### Create objects for angles ###
            _.reduce @violations, (acc, value, name) =>
                colorer = new PlotColorer
                colors = []
                datasets = _.map value.plots, (plot, plotName) =>
                    color = colorer.getColor()
                    colors.push
                        name: plotName
                        code: color.strokeColor
                    _.extend
                        data: @_preparePlot plot
                    , color

                if @_checkDatasets datasets
                    acc.push @_createChartObject name, datasets, colors
                return acc
            , []


    class PlotColorer
        ### Plot colors selector ###

        constructor: ->
            ### Set default colors ###
            @colors = _.map [
                "#5cb85c", "#428bca", "#f0ad4e",
                "#d9534f", "#5bc0de"
            ], (color) ->
                strokeColor : color

        getColor: ->
            ### Get color ###
            color = _.first @colors
            @colors = _.rest @colors
            @colors.push color

            color


    class SuccessPercentPlot
        ### Success percent plot ###

        constructor: (@project, @limit=100, @options={}, @color="#5bc0de") ->
            @prepareData()

        prepareData: ->
            prepared = _.flatten [_.map(_.range(@limit), -> 0), [
                @project.success_percents.reverse()
            ]]
            @data = _.last prepared, @limit

        createChartObject: ->
            data:
                labels: _.map(_.range(@limit), (-> ''))
                datasets: [
                    fillColor: @color
                    strokeColor: @color
                    data: @data
                ]
            options: _.extend
                pointDot: false
                animation: false
                scaleShowLabels: false
            , @options


    class WeekChart
        ### Week bar chart ###
        constructor: (params) ->
            @initialize.apply @, params

        initialize: (data, @field, @color, @name) ->
            @data = _.map _.range(7), (day) =>
                if data.days[day] and data.days[day][@field]
                    data.days[day][@field]
                else
                    0

        createChartObject: ->
            data:
                labels: [
                    'Mon', 'Tue', 'Wed', 'Thu',
                    'Fri', 'Sat', 'Sun'
                ]
                datasets: [
                    data: @data
                    fillColor: @color
                ]
            name: @name


    PlotData: PlotData
    PlotColorer: PlotColorer
    SuccessPercentPlot: SuccessPercentPlot
    WeekChart: WeekChart
