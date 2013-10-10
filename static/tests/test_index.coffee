define ['chai'], (chai) ->
    chai.should()

    describe 'Index page', ->
        it 'should redirect to dashboard when authenticated', ->
            window.isAuthenticated = true
