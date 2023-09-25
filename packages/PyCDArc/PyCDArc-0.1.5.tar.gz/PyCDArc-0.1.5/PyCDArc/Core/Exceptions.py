""" Exception Module For CDA """


class InvalidGivenValue(Exception):
    """ One or more given value is invalid """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class InvalidGivenSubelementData(Exception):
    """ The given data of the subelement is invalid """

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
