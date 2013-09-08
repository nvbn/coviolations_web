window.coviolations ?=
    views: {}
    models: {}

$ ->
    NProgress.start()
    NProgress.inc()

    app = window.coviolations

    collection = new app.models.UserProjectCollection
    collection.fetch
        data:
            limit: 0
            fetch: true
        success: (collection) ->
            view = new app.views.ManageProjectsView
                el: $('.js-manage-projects')
                collection: collection
            view.on 'renderFinished', =>
                NProgress.done()

            view.render()
