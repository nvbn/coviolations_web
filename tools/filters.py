class FiltersAccumulator(object):
    """Filters accumulator"""

    def __init__(self):
        self._filters = []

    def add(self, fnc):
        """Add filter"""
        self._filters.append(fnc)
        return fnc

    def get_spec(self, inst, bundle, initial):
        """Perform filterting"""
        return reduce(
            lambda kwargs, builder: builder(inst, kwargs, bundle),
            self._filters, initial,
        )
