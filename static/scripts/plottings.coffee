define ['underscore', 'underscoreString'], (_, _s) ->
    _.mixin _s.exports()

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
            _.map (_.last prepared, @limit), (item, num) -> [num, item]

        _checkDatasets: (datasets) ->
            datasets.length and (_.any datasets, (@item) ->
                _.any item.values)

        _createChartObject: (name, datasets, colors) ->
            name: name
            data: datasets
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
                    values: @_preparePlot plot
                    key: plotName
                    color: color.strokeColor

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
            @data = _.map (_.last prepared, @limit), (item, num) -> [num, item]

        createChartObject: ->
            data: [
                key: 'success rate'
                values: @data
                color: @color
            ]


    class BaseByDateChart
        ### Base by date chart ###

        constructor: (params) ->
            @initialize.apply @, params

        initialize: (data, @field, @color, @name) ->
            @data = _.map _.range(@counter), (part, num) =>
                if data[@attr][part] and data[@attr][part][@field]
                    value = data[@attr][part][@field]
                else
                    value = 0
                key: @labels[num]
                values: [[@labels[num], value]]

        createChartObject: ->
            data: @data
            name: @name
            tooltip: (day, y ,x) ->
                "<strong>#{day}</strong><br /> Value: #{x}"


    class WeekChart extends BaseByDateChart
        ### Week bar chart ###
        attr: 'days'
        counter: 7
        labels: [
            'Mon', 'Tue', 'Wed', 'Thu',
            'Fri', 'Sat', 'Sun'
        ]


    class DayTimeChart extends BaseByDateChart
        ### Day time chart ###
        attr: 'parts'
        counter: 6
        labels: [
            '00-04', '04-08', '08-12', '12-16', '16-20', '20-00'
        ]


    PlotData: PlotData
    PlotColorer: PlotColorer
    SuccessPercentPlot: SuccessPercentPlot
    WeekChart: WeekChart
    DayTimeChart: DayTimeChart
