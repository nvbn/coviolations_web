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
