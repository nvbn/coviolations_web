window.coviolations ?=
    views: {}
    models: {}

$ ->
    NProgress.start()
    NProgress.inc()

    app = window.coviolations
    waitRendering = 3

    renderFinished = =>
        NProgress.inc()
        waitRendering -= 1
        if waitRendering <= 0
            NProgress.done()

    renderProjects = =>
        if window.userId
            projectCollection = new app.models.UserProjectCollection
            projectCollection.fetch
                data:
                    limit: 0
                success: (collection) =>
                    if collection.meta.total_count
                        projectView = new app.views.ManageProjectsView
                            el: $('.js-enabled-projects')
                            collection: collection
                        projectView.on 'renderFinished', $.proxy renderFinished, @

                        projectView.render()
                    else
                        $('.js-enabled-projects td').html 'No projects found'
        else
            renderFinished()

    renderProjects()
    window.push.on 'project', =>
        renderProjects()

    renderTasks = =>
        if window.userId
            taskCollection = new app.models.TaskCollection()
            taskCollection.fetch
                data:
                    limit: 20
                    with_violations: true
                    self: true
                success: (collection) ->
                    taskView = new app.views.TaskLineListView
                        el: $('.js-last-tasks')
                        collection: collection
                        showProjectName: true
                    taskView.on 'renderFinished', $.proxy renderFinished, @
                    taskView.render()
        else
            renderFinished()
    renderTasks()
    window.push.on 'task', =>
        renderTasks()

    renderFeed = =>
        taskCollection = new app.models.TaskCollection()
        taskCollection.fetch
            data:
                limit: 10
                with_violations: true
            success: (collection) ->
                taskView = new app.views.TaskLineListView
                    el: $('.js-tasks-feed')
                    collection: collection
                    showProjectName: true
                taskView.on 'renderFinished', $.proxy renderFinished, @
                taskView.render()
    renderFeed()
    window.push.on 'task', =>
        renderFeed()

    prettyPrint()
