window.coviolations ?=
    views: {}
    models: {}

$ ->
    app = window.coviolations

    collection = new app.models.UserProjectCollection
    collection.fetch
        data:
            limit: 0
        success: (collection) ->
            view = new app.views.ManageProjectsView
                el: $('.js-manage-projects')
                collection: collection
            view.render()
