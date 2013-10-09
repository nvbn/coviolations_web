require.config
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
        nprogress:
            exports: 'NProgress'
        angles:
            deps: ['angular', 'chartjs']
            exports: 'angles'
        angularBootstrap:
            deps: ['angular']
        ngInfiniteScroll:
            deps: ['angular']
    paths:
        angular: '../angular/angular.min'
        jquery: '../jquery/jquery.min'
        bootstrap: '../bootstrap/dist/js/bootstrap.min'
        underscore: '../underscore/underscore-min'
        chartjs: '../nnnick-chartjs/Chart.min'
        prettify: '../google-code-prettify/distrib/google-code-prettify/prettify'
        sockjs: '../sockjs-client/sockjs.min'
        nprogress: '../nprogress/nprogress'
        angles: '../angles/libs/angles'
        angularBootstrap: '../angular-bootstrap/ui-bootstrap-tpls.min'
        ngInfiniteScroll: '../ngInfiniteScroll/ng-infinite-scroll'
    urlArgs: "bust=" + (new Date()).getTime()


require ['angular', 'application'], ->
    angular.bootstrap document, ['coviolations']
