"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""


class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self, init_type, init_id):
        """Initialise symbol properties."""
        self.type = init_type
        self.id = init_id
        self.line = None
        self.line_pos = None
        self.prev_pos = None
        self.position = None
        self.value = None


class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        try:
            f = open(path, "r")
            self.file = f
        except BaseException:
            print("Path does not exist")
        self.names = names
        self.symbol_type_list = [
            self.NAME,
            self.KEYWORD,
            self.NUMBER,
            self.COMMA,
            self.SEMICOLON,
            self.ARROW,
            self.EQUALS,
            self.PERIOD,
            self.EOF,
            self.INVALID] = range(10)
        self.keywords_list = [
            "START",
            "END",
            "DEVICES",
            "CONNECTIONS",
            "MONITORS",
            "ip",
            "init",
            "cycles",
            "CLOCK",
            "SWITCH",
            "AND",
            "NAND",
            "OR",
            "NOR",
            "DTYPE",
            "XOR",
            "Q",
            "QBAR",
            "DATA",
            "CLK",
            "SET",
            "CLEAR",
            "SIGGEN",
            "sig"]
        [self.START_ID,
         self.END_ID,
         self.DEVICES_ID,
         self.CONNECTIONS_ID,
         self.MONITORS_ID,
         self.ip_ID,
         self.init_ID,
         self.cycles_ID,
         self.CLOCK_ID,
         self.SWITCH_ID,
         self.AND_ID,
         self.NAND_ID,
         self.OR_ID,
         self.NOR_ID,
         self.DTYPE_ID,
         self.XOR_ID,
         self.Q_ID,
         self.QBAR_ID,
         self.DATA_ID,
         self.CLK_ID,
         self.SET_ID,
         self.CLEAR_ID,
         self.SIGGEN_ID,
         self.sig_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""
        # Position indicators of each symbol are w.r.t to the definition file
        # and so are initialised when scanner is called
        self.line = 0
        self.prev_pos = 1
        self.position = 0

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol(None, None)
        self.skip_spaces()

        # Find the type of the file and gives an ID to relevant symbols

        if self.current_character.isalpha():
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            else:
                symbol.type = self.NAME
            # if symbol is a name, add name to names list and get ID
            [symbol.id] = self.names.lookup([name_string])
            symbol.value = name_string

        elif self.current_character.isdigit():
            symbol.type = self.NUMBER
            # Assign actual number as symbol ID if symbol type is a number
            symbol.value = self.get_number()
            symbol.id = int(symbol.value)

        elif self.current_character == "/":
            '''Checking for comment by looking for /. Can either be a block comment
            or a line comment so look at the next character as well for * which signals
            a block comment'''
            self.current_character = self.file.read(1)
            if self.current_character == "*":
                '''if a block comment is received, get next character, then go into
                block comment method and then immediately perform checks on current character'''
                self.ccurrent_character = self.file.read(1)
                self.skip_comments_block()

            else:
                '''if a line comment then current character already relevant comment line
                Perform checks immediately on current character'''
                self.skip_comments_line()
            '''Once exits from comment, self call get_symbol to get the next immediate symbol
            after the comment along with relevant attributes and return it directly'''
            symbol = self.get_symbol()
            return symbol

        # Check punctuations
        elif self.current_character == "=":
            symbol.type = self.EQUALS
            symbol.value = "="

        elif self.current_character == ",":
            symbol.type = self.COMMA
            symbol.value = ","

        elif self.current_character == ";":
            symbol.type = self.SEMICOLON
            symbol.value = ";"

        elif self.current_character == ".":
            symbol.type = self.PERIOD
            symbol.value = "."

        elif self.current_character == "-":
            self.current_character = self.file.read(1)
            if self.current_character == ">":
                symbol.type = self.ARROW
                symbol.value = "->"
            else:
                symbol.type = self.INVALID
                symbol.value = 'invalid'

        elif self.current_character == "":
            symbol.type = self.EOF
            symbol.value = "end"

        else:
            symbol.type = self.INVALID
            symbol.value = 'invalid'

        symbol.prev_pos = self.prev_pos
        symbol.position = self.file.tell()
        symbol.line = self.line + 1
        symbol.line_pos = symbol.position - symbol.prev_pos

        return symbol

    def skip_spaces(self):
        '''Skip all the spaces in the file between symbols'''
        self.current_character = self.file.read(1)
        while self.current_character.isspace():
            # Finds the position of new line
            if self.current_character == "\n" or self.current_character == "\r":
                self.line += 1
                self.prev_pos = self.file.tell() + 1
            self.current_character = self.file.read(1)
        return

    def get_name(self):
        """Seek the next name string in input_file. Return the name string.
        """
        name = ''
        # name contains all adjacent alphanumeric symbol
        while self.current_character.isalnum():
            name += self.current_character
            self.current_character = self.file.read(1)
        self.file.seek(self.file.tell() - 1, 0)
        character = self.file.read(1)
        if character.isalnum():
            pass
        else:
            self.file.seek(self.file.tell() - 1, 0)
        return name

    def get_number(self):
        """Seek the next number in input_file. Returns the number
        """
        number = ''
        while self.current_character.isdigit():
            number += self.current_character
            self.current_character = self.file.read(1)
        self.file.seek(self.file.tell() - 1, 0)
        character = self.file.read(1)
        if character.isdigit():
            pass
        else:
            self.file.seek(self.file.tell() - 1, 0)
        return number

    def print_error(self, current_symbol, error_symbol_1, error_symbol_2=None):
        """Print line where error occurs and indicate position where error occurs
        """
        # return to beginning of the line
        current_loc = current_symbol.position
        print('Error occured in line ', error_symbol_1.line)
        self.file.seek(error_symbol_1.prev_pos - 1, 0)
        # print the complete line character by character until the end of the
        # line (semicolon)
        next_char = self.file.read(1)
        while next_char != "\n" and next_char != "\r" and next_char != "":
            print(next_char, end='')
            next_char = self.file.read(1)
        print('')
        # print first carrot at the position of the first error in the line
        for i in range(error_symbol_1.line_pos):
            print(' ', end='')
            i += 1
        print('^', end='')
        # print second carrot at the position of second error in line
        if error_symbol_2 is not None:
            for i in range(
                    error_symbol_2.line_pos -
                    error_symbol_1.line_pos -
                    1):
                print(' ', end='')
                i += 1
            print('^')
        else:
            print('')
        # Return to original position
        self.file.seek(current_loc, 0)
        return

    def skip_comments_line(self):
        '''Line comments end in line breaks so check current character, and then fetch next character
        '''
        while self.current_character != "\n" and self.current_character != "\r":
            # if line comment at the end, will encounter EOF character,
            # automatically break out and send EOF to parser
            if self.current_character == '':
                return
            self.current_character = self.file.read(1)
        # Line breaks affect the line and line_pos attributes
        self.line += 1
        self.prev_pos = self.file.tell() + 1
        #print('end line comment')
        return

    def skip_comments_block(self):
        '''Block comments enclosed by /* and */, must check for both *
        and / adjacently in order to exit block comment
        '''
        while self.current_character != "*":
            # if new line, must update line and line_pos accordingly
            if self.current_character == "\n" or self.current_character == "\r":
                self.line += 1
                self.prev_pos = self.file.tell() + 1
            # if EOF encountered before comments closed, exit function and send
            # EOF to parser
            if self.current_character == '':
                print("Error occured")
                print("Comment has not been closed!")
                return
            self.current_character = self.file.read(1)
        # check next character to see if actually end of block comment
        self.current_character = self.file.read(1)
        if self.current_character == "/":
            #print('end block comment')
            return
        elif self.current_character == '':
            print("Error occured")
            print("Comment has not been closed!")
            return
        else:
            # if not end of block comment, loop back into function, rechecking
            # for * first again
            self.skip_comments_block()
