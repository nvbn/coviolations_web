define [
    'chai'
    'underscore'
    'controllers'
], (chai, _, controllers) ->
    chai.should()
    describe 'Index controller', =>
        it 'should set not authentication status', =>
            scope = {}
            window.isAuthenticated = false
            controllers.IndexCtrl scope
            scope.isAuthenticated.should.be.false

        it 'should set authentication status', =>
            scope = {}
            window.isAuthenticated = true
            controllers.IndexCtrl scope
            scope.isAuthenticated.should.be.true

        it 'should prepare statistic chart', =>
            scope = {}
            window.successTasks = 10
            window.failedTasks = 5
            controllers.IndexCtrl scope
            scope.successPercent.should.be.equal 10
            scope.failedPercent.should.be.equal 5

    describe 'Dashboard controller', =>
        http =
            get: ->
                success: (callback) ->
                    callback.call null,
                        objects: 'test'
        tasks = -> {load: -> @}

        it 'should fill projects', =>
            scope = {}
            controllers.DashboardCtrl scope, http, tasks
            scope.projects.should.be.equal 'test'

    describe 'Manage projects controller', =>
        it 'should fill projects', =>
            scope = {$watch: -> @}
            controllers.ManageCtrl scope,
                get: ->
                    success: (callback) ->
                        callback.call null,
                            objects: 'test'
            scope.projects.should.be.equal 'test'

        it 'should change loading state', =>
            scope = {$watch: -> @}
            controllers.ManageCtrl scope,
                get: =>
                    scope.loading.should.be.true
                    success: (callback) =>
                        callback.call null,
                            objects: 'test'
                        scope.loading.should.be.false

    describe 'Single project controller', =>
        http =
            get: ->
                success: (callback) ->
                    callback.call null, 'test'
        it 'should attach project', =>
            scope = {'$watch': -> @}
            controllers.ProjectCtrl scope, http, {owner: 'test', name: 'test'}
            scope.project.should.be.equal 'test'
