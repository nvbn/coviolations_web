window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    app = window.coviolations

    class app.models.UserProject extends Backbone.Model
        ### User project model ###
        urlRoot: '/api/v1/userprojects/'


    class app.models.UserProjectCollection extends Backbone.Collection
        ### User project collection ###
        url: '/api/v1/userprojects/'
        model: app.models.UserProject


    class app.models.Task extends Backbone.Model
        ### Task model ###
        urlRoot: '/api/v1/tasks/'


    class app.models.TaskCollection extends Backbone.Collection
        ### Task collection ###
        url: '/api/v1/tasks/'
        model: app.models.Task
