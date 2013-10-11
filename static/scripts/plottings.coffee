define ['underscore'], (_) ->
    class PlotData
        ### Plot data organizer ###

        constructor: (tasks) ->
            @violations = {}
            @fill tasks

        fill: (tasks) ->
            _.each tasks, (task) =>
                taskViolations = _.filter (task.violations or []), (violation) ->
                    _.isObject violation

                _.each taskViolations, (violation) =>
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

    PlotData: PlotData
    PlotColorer: PlotColorer