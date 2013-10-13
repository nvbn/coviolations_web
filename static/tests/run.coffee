window.testSuite = true
require ['/static/scripts/main.js'], ->
    mocha.setup 'bdd'
    Mocha.Runner.prototype.checkGlobals = -> @
    require [
        '/static/tests/test_models.js'
        '/static/tests/test_controllers.js'
        '/static/tests/test_plottings.js'
    ], ->
        mocha.run()
