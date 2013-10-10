define [
    'chai'
    'underscore'
    'models'
], (chai, _, models) ->
    chai.should()
    describe 'Task model', =>
        it 'should change offset on load', =>
            http =
                get: =>
                    success: (callback) =>
                        callback.call null,
                            objects: _.map _.range(25), ->
                                created: "2013-10-10T10:31:07.280000"
                            meta:
                                total_count: 25
            Tasks = models.getTaskModel(http)
            tasks = new Tasks 20
            tasks.load()
            tasks.offset.should.be.equal 20

        it 'should prepare url', =>
            Tasks = models.getTaskModel {}
            tasks = new Tasks 5, true, false
            tasks.getUrl().should.be.equal \
                '/api/v1/tasks/task/?with_violations=true&self=false&limit=5&offset=0'

        it 'should not load more than can', =>
            http =
                get: =>
                    success: (callback) =>
                        callback.call null,
                            objects: _.map _.range(5), ->
                                created: "2013-10-10T10:31:07.280000"
                            meta:
                                total_count: 5
            Tasks = models.getTaskModel(http)
            tasks = new Tasks 5
            tasks.load()
            tasks.load()
            tasks.canLoad.should.be.false
