window.coviolations ?=
    views: {}
    models: {}

$ ->
    pageView = new coviolations.views.IndexPageView
        userId: window.userId
        successPercent:window.successPercent
        failedPercent: window.failedPercent
        taskCollection: new coviolations.models.TaskCollection()
        projectCollection: new coviolations.models.UserProjectCollection
        push: window.push
        el: $('#main-container')

    pageView.render()
