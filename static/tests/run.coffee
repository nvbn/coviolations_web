window.testSuite = true
require ['/static/scripts/main.js'], ->
    mocha.setup 'bdd'
    require ['/static/tests/test_models.js'], ->
        mocha.run()
