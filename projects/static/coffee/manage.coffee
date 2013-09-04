window.coviolations ?=
    views: {}
    models: {}

$ ->
    app = window.coviolations

    class app.models.UserProject extends Backbone.Model
        ### User project model ###
        urlRoot: '/api/v1/userprojects/'


    class app.models.UserProjectCollection extends Backbone.Collection
        ### User project collection ###
        url: '/api/v1/userprojects/'
        model: app.models.UserProject


    class app.views.ProjectLineView extends Backbone.View
        ### Project line view ###
        events:
            'click .js-yes': 'enable'
            'click .js-no': 'disable'
        template: _.template $('#manage-project-line-tmpl').html()
        tagName: 'tr'

        initialize: ->
            @model.on 'change', $.proxy @render, @

        render: ->
            @$el.html @template @model.attributes

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
            @collection.each $.proxy @renderLine, @

        renderLine: (model) ->
            lineView = new app.views.ProjectLineView
                model: model
            lineView.render()
            @$el.append lineView.$el


    collection = new app.models.UserProjectCollection
    collection.fetch
        success: (collection) ->
            view = new app.views.ManageProjectsView
                el: $('.js-manage-projects')
                collection: collection
            view.render()
