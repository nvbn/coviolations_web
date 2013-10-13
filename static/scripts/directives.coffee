define ['angular', 'jquery'], (angular, $) ->
    module = angular.module 'coviolations.directives', []
    module.directive 'fullfill', ->
        (scope, element) ->
            $el = $(element)
            $el.attr 'width', $el.parent().width()
