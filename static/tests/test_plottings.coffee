define [
    'chai'
    'underscore'
    'plottings'
], (chai, _, plottings) ->
    chai.should()

    describe 'Plot colorer', =>
        it 'should not duplicate color in order', =>
            colorer = new plottings.PlotColorer
            colorer.getColor().should.not.be.equal colorer.getColor()

        it 'should be cyclic', =>
            colorer = new plottings.PlotColorer
            first = colorer.getColor()
            _.each _.range(colorer.colors.length - 1), => colorer.getColor()
            colorer.getColor().should.be.equal first

    describe 'Plot data', =>
        getViolation = (name='test') ->
            name: name
            plot:
                x: 1
                y: 2

        it 'should ignore tasks without violations', =>
            data = new plottings.PlotData [
                {name: 'test'}, {name: 'test2', violations: null}
            ]
            _.keys(data.violations).length.should.be.equal 0

        it 'should not create duplicate violations', =>
            data = new plottings.PlotData [
                {violations: [getViolation()]}, {violations: [getViolation()]}
            ]
            _.values(data.violations).length.should.be.equal 1
