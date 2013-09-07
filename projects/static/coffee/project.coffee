window.coviolations ?=
    views: {}
    models: {}

STATUS_NEW = 0
STATUS_SUCCESS = 1
STATUS_FAILED = 2

$ ->
    app = window.coviolations

    class app.models.Task extends Backbone.Model
        ### Task model ###
        urlRoot: '/api/v1/tasks/'


    class app.models.TaskCollection extends Backbone.Collection
        ### Task collection ###
        url: '/api/v1/tasks/'
        model: app.models.Task


    class app.views.TaskLineView extends Backbone.View
        ### Task line view ###
        template: _.template($('#project-task-line-tmpl').html())
        tagName: 'tr'

        render: ->
            @$el.html @template @model.attributes

            if @model.get('status') == STATUS_SUCCESS
                @$el.addClass 'success'

            if @model.get('status') == STATUS_FAILED
                @$el.addClass 'danger'


    class app.views.TaskLineListView extends Backbone.View
        ### Task line list view ###
        tagName: 'table'

        render: ->
            @collection.each (task) =>
                view = new app.views.TaskLineView
                    model: task
                view.render()
                @$el.append(view.$el)


    collection = new app.models.TaskCollection()
    collection.fetch
        data:
            limit: 0
            project: window.project
        success: (collection) ->
            view = new app.views.TaskLineListView
                el: $('.js-task-line-list')
                collection: collection
            view.render()
