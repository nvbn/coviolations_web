window.coviolations ?=
    views: {}
    models: {}

$ ->
    pageView = new coviolations.views.ManageProjectsPageView
        el: $('#main-container')
        collection: new coviolations.models.UserProjectCollection

    pageView.render()
