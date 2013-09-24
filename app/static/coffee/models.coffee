window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    app = window.coviolations

    class app.models.UserProject extends Backbone.Model
        ### User project model ###
        urlRoot: '/api/v1/projects/project/'

        url: ->
            @urlRoot + @get('id') + '/'


    class app.models.UserProjectCollection extends Backbone.Collection
        ### User project collection ###
        url: '/api/v1/projects/project/'
        model: app.models.UserProject


    class app.models.Task extends Backbone.Model
        ### Task model ###
        urlRoot: '/api/v1/tasks/task/'


    class app.models.TaskCollection extends Backbone.Collection
        ### Task collection ###
        url: '/api/v1/tasks/task/'
        model: app.models.Task
