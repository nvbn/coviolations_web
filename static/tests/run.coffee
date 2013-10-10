window.testSuite = true
require ['/static/scripts/main.js'], ->
    mocha.setup 'bdd'
    require ['/static/tests/test_index.js'], ->
        mocha.run()
