window.coviolations ?=
    views: {}
    models: {}
    plotting: {}
    push: {}

$ ->
    pageView = new coviolations.views.IndexPageView
        userId: window.userId
        successPercent:window.successPercent
        failedPercent: window.failedPercent
        taskCollection: new coviolations.models.TaskCollection()
        projectCollection: new coviolations.models.UserProjectCollection
        push: coviolations.push.push
        el: $('#main-container')

    pageView.render()
