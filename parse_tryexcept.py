"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from errors import CustomError

class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    # def __init__(self, names, devices, network, monitors, scanner):
    def __init__(self, names, scanner):
        """Initialise constants."""
        self.names = names
        # self.devices = devices
        # self.network = network
        # self.monitors = monitors
        self.scanner = scanner
        self.symbol = None
        self.error_count = 0
        self.validdeviceids = [self.scanner.CLOCK_ID, self.scanner.SWITCH_ID, self.scanner.AND_ID, 
            self.scanner.NAND_ID, self.scanner.OR_ID, self.scanner.NOR_ID, self.scanner.DTYPE_ID,
            self.scanner.XOR_ID]
        self.validparamids = [self.scanner.ip_ID, self.scanner.init_ID, self.scanner.cycles_ID]
        self.validdtypeinputs = [self.scanner.DATA_ID, self.scanner.CLK_ID, self.scanner.SET_ID,
            self.scanner.CLEAR_ID]
        self.validdtypeoutputs = [self.scanner.Q_ID, self.scanner.QBAR_ID]



    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        while self.symbol.type!=self.scanner.EOF:
            self.check_fixed(self.scanner.START_ID)
            self.check_fixed(self.scanner.DEVICES_ID)
            self.check_devicelist()
            self.check_fixed(self.scanner.DEVICES_ID)
            self.check_fixed(self.scanner.START_ID)
            self.check_fixed(self.scanner.CONNECTIONS_ID)
            self.check_connectionlist()
            self.check_fixed(self.scanner.CONNECTIONS_ID)
            self.check_fixed(self.scanner.START_ID)
            self.check_fixed(self.scanner.MONITORS_ID)
            self.check_monitorlist()
            self.check_fixed(self.scanner.MONITORS_ID)
            self.symbol=self.scanner.get_symbol()
        # if self.symbol.type==self.scanner.EOF:
        #     print("Finished parsing!")
        #     print("No of errors:"+str(self.error_count))
        # else:
        #     print("There shouldn't be anything here.")
        print("Finished parsing!")
        print("No of errors:"+str(self.error_count))

        return True

    def semicolon_skipper(self):
        """When error found, skips to end of line by identifying semicolon"""
        while self.symbol.type != self.scanner.SEMICOLON:
            self.symbol = self.scanner.get_symbol()

        return None

    def check_name(self, symbol):
        """Checks if device name is valid"""
        if symbol.type == self.scanner.NAME:
            return True
        else:
            return False

    # def check_name_exists(self, symbol):
    #     """Checks if device name is valid, and that it has been initialised"""
    #     if self.check_name(symbol) and self.names.get_name_string(symbol.id) != None:
    #         return True
    #     else:
    #         return False

    def check_validdevice(self, symbol):
        """Checks if symbol is a valid device"""
        if symbol.type == self.scanner.KEYWORD and symbol.id in self.validdeviceids:
            return True
        else:
            return False

    def check_validparam(self, symbol):
        """Checks if symbol is a valid parameter"""
        if symbol.type == self.scanner.KEYWORD and symbol.id in self.validparamids:
            return True
        else:
            return False

    # def check_fixed(self, symbolid):
    #     """Check correctness of fixed sections of the file, e.g. START DEVICES"""

    #     # Get the next symbol
    #     self.symbol = self.scanner.get_symbol()

    #     if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == symbolid):
    #         # Symbol matches expectation
    #         if self.symbol.id == self.scanner.START_ID:
    #             pass
    #         else:
    #             self.symbol = self.scanner.get_symbol()
    #             self.check_semicolon_else_skip(self.symbol)
    #     else:
    #         # Error in symbol
    #         self.display_error(symbolid)
    #         # Skip to semicolon at end of line
    #         self.semicolon_skipper()
    #     return None

    def check_fixed(self, symbolid):
        """Check correctness of fixed sections of the file, e.g. START DEVICES"""
        try:
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == symbolid):
                if self.symbol.id == self.scanner.START_ID:
                    pass
                else:
                    self.symbol = self.scanner.get_symbol()
                    self.check_semicolon_else_skip(self.symbol)
            else:
                self.display_error(symbolid)

        except CustomError as ex:
            self.semicolon_skipper()
            print(ex)


    def check_validdtypeinput(self, symbol):
        """Check if symbol is a valid DType input"""
        if symbol.type == self.scanner.KEYWORD and symbol.id in self.validdtypeinputs:
            return True
        else:
            return False

    def check_validdtypeoutput(self, symbol):
        """Check if symbol is a valid DType output"""
        if symbol.type == self.scanner.KEYWORD and symbol.id in self.validdtypeoutputs:
            return True
        else:
            return False

    def is_semicolon(self, symbol):
        """Checks for a semicolon"""
        if symbol.type == self.scanner.SEMICOLON:
            return True
        else:
            return False


    def check_semicolon_else_skip(self, symbol):
        """Check for a semicolon, otherwise skip to end of line"""
        try:
            if symbol.type == self.scanner.SEMICOLON:
                pass
            else:
                self.display_error("semicolon")
        except CustomError as ex:
            self.semicolon_skipper()
            print(ex)
            

    def is_comma(self, symbol):
        """Checks for a comma"""
        if symbol.type == self.scanner.COMMA:
            return True
        else:
            return False

    def is_equal(self, symbol):
        """Checks if symbol is ="""
        if symbol.type == self.scanner.EQUALS:
            return True
        else:
            return False

    def is_number(self, symbol):
        """Checks if symbol is a number"""
        if symbol.type == self.scanner.NUMBER:
            return True
        else:
            return False

    def is_end(self, symbol):
        """Checks if symbol is END"""
        if symbol.id == self.scanner.END_ID:
            return True
        else:
            return False

    def is_period(self, symbol):
        """Checks if symbol is period"""
        if symbol.type == self.scanner.PERIOD:
            return True
        else:
            return False

    def is_arrow(self, symbol):
        """Checks if symbol is arrow"""
        if symbol.type == self.scanner.ARROW:
            return True
        else:
            return False

    def check_devicelist(self):
        """Checks the entire devices list until END DEVICE is reached"""
        self.symbol = self.scanner.get_symbol()
        # Repeatedly call check_deviceline() until END DEVICE
        while not self.is_end(self.symbol):
            self.check_deviceline()
        return None

    def check_deviceline(self):
        """Checks validity of each line in the devices list"""
        try:
            # Check if device name is valid
            if self.check_name(self.symbol):
                # Pass devicename into required module, and get next symbol
                self.symbol = self.scanner.get_symbol()
                # Check if '=' is used
                if self.is_equal(self.symbol):
                    # Get next symbol
                    self.symbol = self.scanner.get_symbol()
                    # Check if name has been assigned to a valid device type
                    if self.check_validdevice(self.symbol):
                        # Pass devicetype into required module
                        self.symbol = self.scanner.get_symbol()
                        while not self.is_semicolon(self.symbol):
                            if self.is_comma(self.symbol):
                                self.symbol = self.scanner.get_symbol()
                                self.check_paramindevice()
                            else:
                                self.display_error("comma")
                        self.symbol = self.scanner.get_symbol()        
                        pass
                    else:
                        # The device type is not valid
                        self.display_error("devicetype")
                else:
                    # No '='
                    self.display_error("equal")
            else: 
                # The device name is not valid
                self.display_error("devicename")
        except CustomError as ex:
            self.semicolon_skipper()
            self.symbol=self.scanner.get_symbol()
            print(ex)

    def check_paramindevice(self):
        """Checks the parameter of a device"""
        try:
            if self.check_validparam(self.symbol):
                # Pass parameter into required module
                self.symbol = self.scanner.get_symbol()
                # Check if '=' is used
                if self.is_equal(self.symbol):
                    self.symbol = self.scanner.get_symbol()
                    # Check if value is valid
                    if self.is_number(self.symbol):
                        # Pass value into required module
                        self.symbol = self.scanner.get_symbol()
                    else:
                        # The parameter value is not valid
                        self.display_error("number")
                else:
                    # No '='
                    self.display_error("equal")
            else:
                # The parameter type is not valid
                self.display_error("parameter")
        except CustomError as ex:
            self.semicolon_skipper()
            print(ex)

    def check_connectionlist(self):
        self.symbol = self.scanner.get_symbol()
        # Repeatedly call check_connectionline() until END CONNECTIONS
        while not self.is_end(self.symbol):
            self.check_connectionline()
        return None 

    def check_connectionline(self):
        self.check_validconnectionoutput()
        try:
            if self.is_arrow(self.symbol):
                # Get next symbol
                self.symbol = self.scanner.get_symbol()
                self.check_validconnectioninput()
                while not self.is_semicolon(self.symbol):
                    if self.is_comma(self.symbol):
                        self.symbol = self.scanner.get_symbol()
                        self.check_validconnectioninput()
                    else:
                        self.display_error("comma")
                self.symbol = self.scanner.get_symbol()
            elif self.is_semicolon(self.symbol):
                self.symbol = self.scanner.get_symbol()
            else:
                # No '->'
                self.display_error("arrow")
        except CustomError as ex:
            self.semicolon_skipper()
            self.symbol=self.scanner.get_symbol()
            print(ex)

    def check_validconnectioninput(self):
        try:
            # Check if name is valid
            if self.check_name(self.symbol):
                # Pass devicename into required module
                self.symbol = self.scanner.get_symbol()
                # Check if '.' is used:
                if self.is_period(self.symbol):
                    self.symbol = self.scanner.get_symbol()
                    # Check if device input begins with 'I'
                    if self.names.get_name_string(self.symbol.id)[0] == "I":
                        # Check if input number is a positive number
                        try:
                            inputno=int(self.names.get_name_string(self.symbol.id)[1:])
                            # Pass input number into required module
                            self.symbol = self.scanner.get_symbol()
                        except:
                            # Input number is not valid
                            self.display_error("number")
                    # OR if DType input
                    elif self.check_validdtypeinput(self.symbol):
                        self.symbol = self.scanner.get_symbol()
                    else:
                        # Input is not valid
                        self.display_error("input")
                else:
                    # No '.'
                    self.display_error("period")
            else:
                # Device does not exist
                self.display_error("deviceexist")
        except CustomError as ex:
            self.semicolon_skipper()
            print(ex)

    def check_validconnectionoutput(self):
        try:
            # Check if name is valid and has been initialised
            if self.check_name(self.symbol):
                # Pass devicename into required module, and get next symbol
                self.symbol = self.scanner.get_symbol()
                # Check if '->' is used
                if self.is_arrow(self.symbol):
                    pass
                elif self.is_period(self.symbol):
                    self.symbol = self.scanner.get_symbol()
                    if self.check_validdtypeoutput(self.symbol):
                        self.symbol = self.scanner.get_symbol()
                    else:
                        # Invalid DType output
                        self.display_error("doutput")
                else:
                    # Neither an arrow nor a DType output
                    self.display_error("arrowperiod")
            else:
                # Device does not exist
                self.display_error("deviceexist")
        except CustomError as ex:
            self.semicolon_skipper()
            print(ex)

    def check_monitorlist(self):
        self.symbol = self.scanner.get_symbol()
        # Repeatedly call check_monitorline() until END MONITORS
        while not self.is_end(self.symbol):
            self.check_monitorline()

        return None  

    def check_monitorline(self):
        try:
            # Check if device name is valid
            if self.check_name(self.symbol):
                # Pass devicename into required module, and get next symbol
                self.symbol = self.scanner.get_symbol()
                # Check if ';' is used
                if self.is_semicolon(self.symbol):
                    # End of line reached, exit function
                    self.symbol=self.scanner.get_symbol()
                    pass
                elif self.is_period(self.symbol):
                    # DType output
                    self.symbol = self.scanner.get_symbol()
                    if self.check_validdtypeoutput(self.symbol):
                        self.symbol = self.scanner.get_symbol()
                        if self.is_semicolon(self.symbol):
                            # End of line reached, exit function
                            self.symbol=self.scanner.get_symbol()
                            pass
                        else:
                            # Semicolon error
                            self.display_error("semicolon")
                    else:
                        self.display_error("doutput")
                else:
                    # Semicolon error
                    self.display_error("semicolon")
            else:
                # Device does not exist
                self.display_error("deviceexist")
        except CustomError as ex:
            self.semicolon_skipper()
            self.symbol=self.scanner.get_symbol()
            print(ex)


    def display_error(self,symbolid):

        self.error_count += 1

        # FUTURE: exact character with error? maybe use symbol.position()?
        if symbolid == self.scanner.START_ID:
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected START.")
        if symbolid == self.scanner.END_ID:
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected END.")
        if symbolid == self.scanner.DEVICES_ID:
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected DEVICES.")
        if symbolid == self.scanner.CONNECTIONS_ID:
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected CONNECTIONS.")
        if symbolid == self.scanner.MONITORS_ID:
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected MONITORS.")

        if symbolid == "devicename":
            self.scanner.print_error(self.symbol)
            raise CustomError("Invalid device name.")
        if symbolid == "devicetype":
            self.scanner.print_error(self.symbol)
            raise CustomError("Invalid device type.")
        if symbolid == "deviceexist":
            self.scanner.print_error(self.symbol)
            raise CustomError("Device does not exist.")
        if symbolid == "parameter":
            self.scanner.print_error(self.symbol)
            raise CustomError("Invalid parameter type.")
        if symbolid == "semicolonparam":
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected a semicolon or a valid parameter type.")
        if symbolid == "number":
            self.scanner.print_error(self.symbol)
            raise CustomError("Invalid input number.")
        if symbolid == "doutput":
            self.scanner.print_error(self.symbol)
            raise CustomError("Invalid DType output.")
        if symbolid == "arrowperiod":
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected either an arrow or a DType output")


        if symbolid == "semicolon":
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected a semicolon.")
        if symbolid == "equal":            
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected an equal sign.")
        if symbolid == "comma":
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected a comma.")
        if symbolid == "period":            
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected a period.")
        if symbolid == "arrow":
            self.scanner.print_error(self.symbol)
            raise CustomError("Expected an arrow ->.")
        if symbolid == "input":
            self.scanner.print_error(self.symbol)
            raise CustomError("Inputs must either start with I or be DATA, CLK, SET, CLEAR.")

        return None