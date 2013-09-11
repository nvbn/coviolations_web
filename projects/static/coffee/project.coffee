window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    pageView = new coviolations.views.ProjectPageView
        collection: new coviolations.models.TaskCollection()
        project: window.project
        push: coviolations.push.push
        el: $('#main-container')

    pageView.render()
