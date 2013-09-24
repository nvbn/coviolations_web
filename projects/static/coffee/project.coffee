window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    pageView = new coviolations.views.ProjectPageView
        collection: new coviolations.models.TaskCollection()
        project: window.project
        projectId: window.projectId
        push: coviolations.push.push
        el: $('#main-container')

    pageView.render()
