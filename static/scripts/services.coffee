define ['angular', 'favico'], (angular, Favico) ->
    module = angular.module 'coviolations.services', []

    module.factory 'favicoService', =>
        new Favico
