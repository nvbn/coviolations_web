window.coviolations ?=
    views: {}
    models: {}

$ ->
    app = window.coviolations

    projectCollection = new app.models.UserProjectCollection
    projectCollection.fetch
        data:
            limit: 0
        success: (collection) ->
            if collection.meta.total_count
                projectView = new app.views.ManageProjectsView
                    el: $('.js-enabled-projects')
                    collection: collection
                projectView.render()
            else
                $('.js-enabled-projects td').html 'No projects found'

    taskCollection = new app.models.TaskCollection()
    taskCollection.fetch
        data:
            limit: 30
            with_violations: true
            self: true
        success: (collection) ->
            taskView = new app.views.TaskLineListView
                el: $('.js-last-tasks')
                collection: collection
            taskView.render()

    prettyPrint()
