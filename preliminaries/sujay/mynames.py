"""Implements a name table for lexical analysis.

Classes
-------
MyNames - implements a name table for lexical analysis.
"""


class MyNames:

    """Implements a name table for lexical analysis.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    lookup(self, name_string): Returns the corresponding name ID for the
                 given name string. Adds the name if not already present.

    get_string(self, name_id): Returns the corresponding name string for the
                 given name ID. Returns None if the ID is not a valid index.
    """

    def __init__(self):
        """Initialise the names list."""
        self.list = []

    def lookup(self, name_string):
        """Return the corresponding name ID for the given name_string.

        If the name string is not present in the names list, add it.
        """
        try:
            index = self.list.index(name_string)
            return index
        except  ValueError:
             self.list.append(name_string)
             return len(self.list) - 1


    def get_string(self, name_id):
        """Return the corresponding name string for the given name_id.

        If the name ID is not a valid index into the names list, return None.
        """
        if type(name_id) is not int:
            return None
            raise TypeError
        elif name_id < 0:
            return None
            raise ValueError
        elif name_id >= len(self.list):
            return None
            raise ValueError
        else:
            name = self.list[name_id]
            return name