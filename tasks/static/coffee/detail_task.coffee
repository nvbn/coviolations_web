window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    pageView = new coviolations.views.DetailTaskPageView
        project: window.project
        commit: window.commit
        broken: window.broken
        el: $('#main-container')

    pageView.render()
