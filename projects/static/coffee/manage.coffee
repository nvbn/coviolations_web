window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    pageView = new coviolations.views.ManageProjectsPageView
        el: $('#main-container')
        collection: new coviolations.models.UserProjectCollection

    pageView.render()
