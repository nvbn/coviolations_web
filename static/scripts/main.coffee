config =
    baseUrl: '/static/scripts/'
    shim:
        jquery:
            exports: '$'
        angular:
            exports: 'angular'
            deps: ['jquery']
        bootsrap:
            deps: ['jquery']
            exports: '$.fn.popover'
        underscore:
            exports: '_'
        chartjs:
            deps: ['jquery']
            exports: 'Chart'
        prettify:
            exports: 'prettyPrint'
        sockjs:
            exports: 'SockJS'
        ngprogress:
            deps: ['angular']
        angles:
            deps: ['angular', 'chartjs']
            exports: 'angles'
        angularBootstrap:
            deps: ['angular']
        ngInfiniteScroll:
            deps: ['angular']
        underscoreString:
            deps: ['underscore']
            exports: '_.str'
        chai:
            exports: ['chai']
        favico:
            exports: ['Favico']
        angularUiJq:
            deps: ['angular', 'jquery']
        waypoints:
            deps: ['jquery']
    paths:
        angular: '../angular/angular.min'
        jquery: '../jquery/jquery.min'
        bootstrap: '../bootstrap/dist/js/bootstrap.min'
        underscore: '../underscore/underscore-min'
        chartjs: '../nnnick-chartjs/Chart.min'
        prettify: '../google-code-prettify/distrib/google-code-prettify/prettify'
        sockjs: '../sockjs-client/sockjs.min'
        ngprogress: '../ngprogress/build/ngProgress.min'
        angles: '../angles/libs/angles'
        angularBootstrap: '../angular-bootstrap/ui-bootstrap-tpls.min'
        ngInfiniteScroll: '../ngInfiniteScroll/ng-infinite-scroll'
        underscoreString: '../underscore.string/dist/underscore.string.min'
        favico: '../favico.js/favico-0.3.0.min'
        angularUiJq: '../angular-ui-utils/modules/jq/jq'
        waypoints: '../jquery-waypoints/waypoints.min'
        chai: '../chai/chai'

if window.debug
    config.urlArgs = "bust=" + (new Date()).getTime()

require.config config

if not window.testSuite
    require ['angular', 'application'], ->
        angular.bootstrap document, ['coviolations']
