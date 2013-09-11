window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    app = window.coviolations

    class app.plotting.PlotData
        ### Plot data organizer ###

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


    class app.plotting.PlotColorer
        ### Plot colors selector ###

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
