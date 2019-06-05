"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""


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

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        # Create an internal symbol attribute to be passed around functions
        self.symbol = None

        # Store all syntax and semantic errors separately
        self.syntax_errors_list = []
        self.semantic_errors_list = []

        # To check for valid device, parameters and DType inputs/outputs
        self.validdeviceids = [
            self.scanner.CLOCK_ID,
            self.scanner.SWITCH_ID,
            self.scanner.AND_ID,
            self.scanner.NAND_ID,
            self.scanner.OR_ID,
            self.scanner.NOR_ID,
            self.scanner.DTYPE_ID,
            self.scanner.XOR_ID,
            self.scanner.SIGGEN_ID]
        self.validparamids = [
            self.scanner.ip_ID,
            self.scanner.init_ID,
            self.scanner.cycles_ID,
            self.scanner.sig_ID]
        self.validdtypeinputs = [
            self.scanner.DATA_ID,
            self.scanner.CLK_ID,
            self.scanner.SET_ID,
            self.scanner.CLEAR_ID]
        self.validdtypeoutputs = [self.scanner.Q_ID, self.scanner.QBAR_ID]

        # Initialise some attributes that will be used when checking devices,
        # connections and monitors.
        # Allows for the correct symbol to be passed between functions for
        # accurate error reporting.
        self.device_name = None
        self.device_kind = None
        self.device_param = None
        self.device_paramvalue = None
        self.connection_first_device = None
        self.connection_first_port = None
        self.connection_second_device = None
        self.connection_second_port = None
        self.monitor_device = None
        self.monitor_port = None

        # Handles the fact that the same error id is used in both network
        # and monitor.
        # Set to 1 when the error comes from monitors
        self.duplicate_error_checker = 0

    def parse_network(self):
        """Parse the circuit definition file."""
        self._check_fixed_start()
        self._check_fixed_others(self.scanner.DEVICES_ID)
        self._check_devicelist()
        self._check_fixed_others(self.scanner.DEVICES_ID)
        self._check_fixed_start()
        self._check_fixed_others(self.scanner.CONNECTIONS_ID)
        self._check_connectionlist()
        self._check_fixed_others(self.scanner.CONNECTIONS_ID)
        # Move on to checking monitors
        self.duplicate_error_checker = 1
        self._check_whole_network()
        self._check_fixed_start()
        self._check_fixed_others(self.scanner.MONITORS_ID)
        self._check_monitorlist()
        self._check_fixed_others(self.scanner.MONITORS_ID)
        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.EOF:
            print("Finished parsing!")
            print("No of errors:" +
                  str(len(self.syntax_errors_list) +
                      len(self.semantic_errors_list)))
        else:
            print("There shouldn't be anything here.")

        if len(
                self.syntax_errors_list) == 0 and len(
                self.semantic_errors_list) == 0:
            # No errors in definition file
            return True
        else:
            # Either semantic or syntax error(s) in file
            return False

    # What follows are some internal functions for the parser.
    # They have been modularised like this so that if there are any
    # changes to the scanner, only one change has to be made.

    def _check_name(self, symbol):
        """Checks if device name is valid"""
        if symbol.type == self.scanner.NAME:
            return True
        else:
            return False

    def _check_validdevice(self, symbol):
        """Checks if symbol is a valid device"""
        if symbol.type == self.scanner.KEYWORD and \
                symbol.id in self.validdeviceids:

            return True
        else:
            return False

    def _check_validparam(self, symbol):
        """Checks if symbol is a valid parameter"""
        if symbol.type == self.scanner.KEYWORD and \
                symbol.id in self.validparamids:
            return True
        else:
            return False

    def _check_fixed_start(self):
        """Check correctness of the symbol START"""
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.KEYWORD and \
                self.symbol.id == self.scanner.START_ID:
            pass
        elif self._is_eof(self.symbol):
            # In case file ends prematurely
            pass
        else:
            self._display_syntax_error("start")

    def _check_fixed_others(self, symbol_id):
        """Check correctness of other fixed symbols, e.g. DEVICES"""

        # Get the next symbol
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.KEYWORD and \
                self.symbol.id == symbol_id:
            self.symbol = self.scanner.get_symbol()
            self._check_semicolon_else_skip(self.symbol)
        elif self._is_eof(self.symbol):
            # In case file ends prematurely
            pass
        else:
            # Error in symbol
            self._display_syntax_error(symbol_id)
            # Skip to semicolon at end of line
            self._semicolon_skipper()

    def _check_validdtypeinput(self, symbol):
        """Check if symbol is a valid DType input"""
        if symbol.type == self.scanner.KEYWORD and \
                symbol.id in self.validdtypeinputs:
            return True
        else:
            return False

    def _check_validdtypeoutput(self, symbol):
        """Check if symbol is a valid DType output"""
        if symbol.type == self.scanner.KEYWORD and \
                symbol.id in self.validdtypeoutputs:
            return True
        else:
            return False

    def _is_semicolon(self, symbol):
        """Checks for a semicolon"""
        if symbol.type == self.scanner.SEMICOLON:
            return True
        else:
            return False

    def _semicolon_skipper(self):
        """When error found, skips to end of line by identifying semicolon"""
        while (
            not self._is_semicolon(
                self.symbol)) and (
            not self._is_eof(
                self.symbol)):
            self.symbol = self.scanner.get_symbol()
        if self._is_eof(self.symbol):
            # In case file ends prematurely
            pass
        return None

    def _check_semicolon_else_skip(self, symbol):
        """Check for a semicolon, otherwise skip to end of line"""
        if symbol.type == self.scanner.SEMICOLON:
            pass
        else:
            self._display_syntax_error("semicolon")
            # Skip to semicolon at end of line
            self._semicolon_skipper()

    def _is_comma(self, symbol):
        """Checks for a comma"""
        if symbol.type == self.scanner.COMMA:
            return True
        else:
            return False

    def _is_equal(self, symbol):
        """Checks if symbol is ="""
        if symbol.type == self.scanner.EQUALS:
            return True
        else:
            return False

    def _is_number(self, symbol):
        """Checks if symbol is a number"""
        if symbol.type == self.scanner.NUMBER:
            return True
        else:
            return False

    def _is_end(self, symbol):
        """Checks if symbol is END"""
        if symbol.id == self.scanner.END_ID:
            return True
        else:
            return False

    def _is_period(self, symbol):
        """Checks if symbol is period"""
        if symbol.type == self.scanner.PERIOD:
            return True
        else:
            return False

    def _is_arrow(self, symbol):
        """Checks if symbol is arrow"""
        if symbol.type == self.scanner.ARROW:
            return True
        else:
            return False

    def _is_eof(self, symbol):
        """Checks if symbol is EOF"""
        if symbol.type == self.scanner.EOF:
            return True
        else:
            return False

    def _device_type_returner(self, symbol):
        """Returns the correct device type to input into Devices module."""
        if self.names.get_name_string(symbol.id) == "AND":
            return self.devices.AND
        if self.names.get_name_string(symbol.id) == "OR":
            return self.devices.OR
        if self.names.get_name_string(symbol.id) == "NAND":
            return self.devices.NAND
        if self.names.get_name_string(symbol.id) == "NOR":
            return self.devices.NOR
        if self.names.get_name_string(symbol.id) == "XOR":
            return self.devices.XOR
        if self.names.get_name_string(symbol.id) == "CLOCK":
            return self.devices.CLOCK
        if self.names.get_name_string(symbol.id) == "SWITCH":
            return self.devices.SWITCH
        if self.names.get_name_string(symbol.id) == "DTYPE":
            return self.devices.D_TYPE
        if self.names.get_name_string(symbol.id) == "SIGGEN":
            return self.devices.SIGGEN

    def _check_devicelist(self):
        """Checks the entire devices list until END DEVICE is reached"""
        self.symbol = self.scanner.get_symbol()
        # Repeatedly call _check_deviceline() until END DEVICE
        while (
            not self._is_end(
                self.symbol)) and (
            not self._is_eof(
                self.symbol)):
            self._check_deviceline()
        if self._is_eof(self.symbol):
            # In case file ends prematurely
            pass
        return None

    def _check_deviceline(self):
        """Checks validity of each line in the devices list"""
        # Check if device name is valid
        if self._check_name(self.symbol):
            self.device_name = self.symbol
            self.symbol = self.scanner.get_symbol()
            # Check if '=' is used
            if self._is_equal(self.symbol):
                # Get next symbol
                self.symbol = self.scanner.get_symbol()
                # Check if name has been assigned to a valid device type
                if self._check_validdevice(self.symbol):
                    self.device_kind = self.symbol
                    self.symbol = self.scanner.get_symbol()
                    if self._is_semicolon(self.symbol):
                        # No device property
                        if len(
                                self.semantic_errors_list) == 0 and len(
                                self.syntax_errors_list) == 0:
                            # Only create device if no previous errors
                            device_error = self.devices.make_device(
                                self.device_name.id,
                                self._device_type_returner(
                                    self.device_kind))
                            # Send the returned error ID for error reporting
                            self._display_semantic_error(device_error)
                        self.symbol = self.scanner.get_symbol()
                    elif self._is_comma(self.symbol):
                        # Device property set
                        self.symbol = self.scanner.get_symbol()
                        self.device_param, \
                            self.device_paramvalue \
                            = self._check_paramindevice()
                        if len(
                                self.semantic_errors_list) == 0 and len(
                                self.syntax_errors_list) == 0:
                            # Only create device if no previous errors
                            if self._device_type_returner(
                                self.device_kind) == \
                                    self.devices.SIGGEN:
                                # Use symbol attribute 'value' to get parameter
                                # value, since the symbol's 'id' attribute
                                # would not capture a leading '0' in the signal
                                # generator's signal string
                                device_error = self.devices.make_device(
                                    self.device_name.id,
                                    self._device_type_returner(
                                        self.device_kind),
                                    self.device_paramvalue.value)
                            else:
                                # For other device types
                                device_error = self.devices.make_device(
                                    self.device_name.id,
                                    self._device_type_returner(
                                        self.device_kind),
                                    self.device_paramvalue.id)
                            # Send the returned error ID for error reporting
                            self._display_semantic_error(device_error)
                        self._check_semicolon_else_skip(self.symbol)
                        self.symbol = self.scanner.get_symbol()
                    else:
                        # Neither semicolon nor comma
                        self._display_syntax_error("semicoloncomma")
                        self._semicolon_skipper()
                        self.symbol = self.scanner.get_symbol()
                else:
                    # The device type is not valid
                    self._display_syntax_error("devicetype")
                    self._semicolon_skipper()
                    self.symbol = self.scanner.get_symbol()
            else:
                # No '='
                self._display_syntax_error("equal")
                self._semicolon_skipper()
                self.symbol = self.scanner.get_symbol()
        else:
            # The device name is not valid
            self._display_syntax_error("devicename")
            self._semicolon_skipper()
            self.symbol = self.scanner.get_symbol()

        return None

    def _check_paramindevice(self):
        """Returns the parameter of a device"""
        if self._check_validparam(self.symbol):
            param = self.symbol
            self.symbol = self.scanner.get_symbol()
            # Check if '=' is used
            if self._is_equal(self.symbol):
                self.symbol = self.scanner.get_symbol()
                # Check if value is valid
                if self._is_number(self.symbol):
                    value = self.symbol
                    self.symbol = self.scanner.get_symbol()
                    return param, value
                else:
                    # The parameter value is not valid
                    self._display_syntax_error("number")
                    self._semicolon_skipper()
                    return None, None
            else:
                # No '='
                self._display_syntax_error("equal")
                self._semicolon_skipper()
                return None, None
        else:
            # The parameter type is not valid
            self._display_syntax_error("parameter")
            self._semicolon_skipper()
            return None, None

    def _check_connectionlist(self):
        """Checks the entire connections list until END CONNECTIONS
        is reached"""
        self.symbol = self.scanner.get_symbol()
        # Repeatedly call _check_connectionline() until END CONNECTIONS
        while (
            not self._is_end(
                self.symbol)) and (
            not self._is_eof(
                self.symbol)):
            self._check_connectionline()
        if self._is_eof(self.symbol):
            # In case file ends prematurely
            pass
        return None

    def _check_connectionline(self):
        """Checks validity of each line in the connections list"""
        self.connection_first_device, \
            self.connection_first_port \
            = self._check_validconnectionoutput()
        if self._is_arrow(self.symbol):
            # Get next symbol
            self.symbol = self.scanner.get_symbol()
            self.connection_second_device, \
                self.connection_second_port \
                = self._check_validconnectioninput()
            if len(
                    self.semantic_errors_list) == 0 and len(
                    self.syntax_errors_list) == 0:
                # Only create connection if no previous errors
                connection_error = self._connection_maker(
                    self.connection_first_device,
                    self.connection_first_port,
                    self.connection_second_device,
                    self.connection_second_port)
                # Send the returned error ID for error reporting
                self._display_semantic_error(connection_error)
            # Run a while loop to check for possible multiple connections from
            # same output
            while (
                not self._is_semicolon(
                    self.symbol)) and (
                not self._is_eof(
                    self.symbol)):
                if self._is_comma(self.symbol):
                    self.symbol = self.scanner.get_symbol()
                    self.connection_second_device, \
                        self.connection_second_port \
                        = self._check_validconnectioninput()
                    if len(
                            self.semantic_errors_list) == 0 and len(
                            self.syntax_errors_list) == 0:
                        # Only create connection if no previous errors
                        connection_error = self._connection_maker(
                            self.connection_first_device,
                            self.connection_first_port,
                            self.connection_second_device,
                            self.connection_second_port)
                        # Send the returned error ID for error reporting
                        self._display_semantic_error(connection_error)
                else:
                    # No comma
                    self._display_syntax_error("comma")
                    self._semicolon_skipper()
            self.symbol = self.scanner.get_symbol()
        elif self._is_semicolon(self.symbol):
            self.symbol = self.scanner.get_symbol()
        else:
            # No '->'
            self._display_syntax_error("arrow")
            self._semicolon_skipper()
            self.symbol = self.scanner.get_symbol()
        return None

    def _check_validconnectioninput(self):
        """Return device and port for input in connections"""
        # Check if name is valid
        if self._check_name(self.symbol):
            second_device = self.symbol
            self.symbol = self.scanner.get_symbol()
            # Check if '.' is used:
            if self._is_period(self.symbol):
                self.symbol = self.scanner.get_symbol()
                # Check if device input begins with 'I'
                if self.names.get_name_string(self.symbol.id)[0] == "I":
                    # Check if input number is a positive number
                    try:
                        inputno = int(
                            self.names.get_name_string(
                                self.symbol.id)[
                                1:])
                        second_port = self.symbol
                        self.symbol = self.scanner.get_symbol()
                        return second_device, second_port
                    except BaseException:
                        # Input number is not valid
                        self._display_syntax_error("number")
                        self._semicolon_skipper()
                        return None, None
                # OR if DType input
                elif self._check_validdtypeinput(self.symbol):
                    second_port = self.symbol
                    self.symbol = self.scanner.get_symbol()
                    return second_device, second_port
                else:
                    # Input is not valid
                    self._display_syntax_error("input")
                    self._semicolon_skipper()
                    return None, None
            else:
                # No '.'
                self._display_syntax_error("period")
                self._semicolon_skipper()
                return None, None
        else:
            # Device does not exist
            self._display_syntax_error("devicename")
            self._semicolon_skipper()
            return None, None

    def _check_validconnectionoutput(self):
        """Return device and port for output in connections"""
        # Check if name is valid and has been initialised
        if self._check_name(self.symbol):
            first_device = self.symbol
            self.symbol = self.scanner.get_symbol()
            # Check if '->' is used
            if self._is_arrow(self.symbol):
                return first_device, None
            elif self._is_period(self.symbol):
                self.symbol = self.scanner.get_symbol()
                if self._check_validdtypeoutput(self.symbol):
                    first_port = self.symbol
                    self.symbol = self.scanner.get_symbol()
                    return first_device, first_port
                else:
                    # Invalid DType output
                    self._display_syntax_error("doutput")
                    self._semicolon_skipper()
                    return None, None
            else:
                # Neither an arrow nor a DType output
                self._display_syntax_error("arrowperiod")
                self._semicolon_skipper()
                return None, None
        else:
            # Device does not exist
            self._display_syntax_error("devicename")
            self._semicolon_skipper()
            return None, None

    def _connection_maker(
            self,
            first_device,
            first_port,
            second_device,
            second_port):
        """Create own make_connection to handle the fact that first device
        may sometimes not have a port specified."""
        if first_port is None:
            return self.network.make_connection(
                first_device.id, None,
                second_device.id, second_port.id)
        else:
            return self.network.make_connection(
                first_device.id, first_port.id,
                second_device.id, second_port.id)

    def _check_whole_network(self):
        """Use network's check_network() to test all connections."""
        if not self.network.check_network():
            # check_network has failed, issue error
            self._display_semantic_error("network")

    def _check_monitorlist(self):
        """Checks the entire monitors list until END MONITORS is reached"""
        self.symbol = self.scanner.get_symbol()
        # Repeatedly call _check_monitorline() until END MONITORS
        while (
            not self._is_end(
                self.symbol)) and (
            not self._is_eof(
                self.symbol)):
            self._check_monitorline()
        if self._is_eof(self.symbol):
            # In case file ends prematurely
            pass
        return None

    def _check_monitorline(self):
        """Checks validity of each line in the monitors list"""
        # Check if device name is valid
        if self._check_name(self.symbol):
            self.monitor_device = self.symbol
            self.symbol = self.scanner.get_symbol()
            # Check if ';' is used
            if self._is_semicolon(self.symbol):
                # End of line reached, exit function
                self.symbol = self.scanner.get_symbol()
                if len(
                        self.semantic_errors_list) == 0 and len(
                        self.syntax_errors_list) == 0:
                    monitor_error = self.monitors.make_monitor(
                        self.monitor_device.id, None)
                    self._display_semantic_error(monitor_error)
            elif self._is_period(self.symbol):
                # DType output
                self.symbol = self.scanner.get_symbol()
                if self._check_validdtypeoutput(self.symbol):
                    self.monitor_port = self.symbol
                    self.symbol = self.scanner.get_symbol()
                    if self._is_semicolon(self.symbol):
                        # End of line reached, exit function
                        self.symbol = self.scanner.get_symbol()
                        if len(
                                self.semantic_errors_list) == 0 and len(
                                self.syntax_errors_list) == 0:
                            monitor_error = self.monitors.make_monitor(
                                self.monitor_device.id,
                                self.monitor_port.id)
                            self._display_semantic_error(monitor_error)
                    else:
                        # Semicolon error
                        self._display_syntax_error("semicolon")
                        self._semicolon_skipper()
                        self.symbol = self.scanner.get_symbol()
                else:
                    self._display_syntax_error("doutput")
                    self._semicolon_skipper()
                    self.symbol = self.scanner.get_symbol()
            else:
                # Semicolon error
                self._display_syntax_error("semicolon")
                self._semicolon_skipper()
                self.symbol = self.scanner.get_symbol()
        else:
            # Device does not exist
            self._display_syntax_error("devicename")
            self._semicolon_skipper()
            self.symbol = self.scanner.get_symbol()

        return None

    def _display_syntax_error(self, errorid):
        """Handles syntax error reporting"""

        # For total error count
        self.syntax_errors_list.append(errorid)

        if errorid == "start":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected START.")
        elif errorid == self.scanner.END_ID:
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected END.")
        elif errorid == self.scanner.DEVICES_ID:
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected DEVICES.")
        elif errorid == self.scanner.CONNECTIONS_ID:
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected CONNECTIONS.")
        elif errorid == self.scanner.MONITORS_ID:
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected MONITORS.")

        elif errorid == "devicename":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Invalid device name.")
        elif errorid == "devicetype":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Invalid device type.")
        elif errorid == "parameter":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Invalid parameter type.")
        elif errorid == "semicoloncomma":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected a semicolon or a comma.")
        elif errorid == "number":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Invalid input number.")
        elif errorid == "doutput":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Only DTypes can specify an output. \
                Either an invalid DType output or should not have an output.")
        elif errorid == "arrowperiod":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected either an arrow or a DType output")

        elif errorid == "semicolon":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected a semicolon.")
        elif errorid == "equal":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected an equal sign.")
        elif errorid == "comma":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected a comma.")
        elif errorid == "period":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected a period.")
        elif errorid == "arrow":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Expected an arrow ->.")
        elif errorid == "input":
            self.scanner.print_error(self.symbol, self.symbol)
            print("Inputs must either start with I or be \
                DATA, CLK, SET, CLEAR.")

        return None

    def _display_semantic_error(self, errorid):
        """Handles semantic error reporting"""

        # For total error count
        self.semantic_errors_list.append(errorid)

        if errorid == self.devices.NO_ERROR:
            self.semantic_errors_list.pop()
        elif errorid == self.devices.INVALID_QUALIFIER:
            self.scanner.print_error(
                self.symbol, self.device_paramvalue)
            print("This device cannot have this parameter.")
        elif errorid == self.devices.NO_QUALIFIER:
            self.scanner.print_error(self.symbol, self.device_kind)
            print("This device needs a parameter.")
        elif errorid == self.devices.BAD_DEVICE:
            self.scanner.print_error(self.symbol, self.device_name)
            print("Invalid device provided.")
        elif errorid == self.devices.QUALIFIER_PRESENT:
            self.scanner.print_error(self.symbol, self.device_param)
            print("This device should not have a parameter.")
        elif errorid == self.devices.DEVICE_PRESENT:
            self.scanner.print_error(self.symbol, self.device_name)
            print("This device already exists.")
        elif errorid == self.devices.INVALID_SIGGEN:
            self.scanner.print_error(
                self.symbol, self.device_paramvalue)
            print("Only binary waveforms can be specified.")

        elif errorid == self.network.NO_ERROR:
            self.semantic_errors_list.pop()
        elif errorid == self.network.INPUT_TO_INPUT:
            self.scanner.print_error(
                self.symbol, self.connection_second_port)
            print("Cannot connect an input to an input.")
        elif errorid == self.network.OUTPUT_TO_OUTPUT:
            self.scanner.print_error(
                self.symbol, self.connection_second_port)
            print("Cannot connect an output to an output.")
        elif errorid == self.network.INPUT_CONNECTED:
            self.scanner.print_error(
                self.symbol, self.connection_second_port)
            print("This port is already in a connection.")
        elif errorid == self.network.PORT_ABSENT:
            self.scanner.print_error(
                self.symbol, self.connection_second_port)
            print("This is not a valid port.")
        elif errorid == self.network.DEVICE_ABSENT:
            if self.duplicate_error_checker == 0:
                # Error is in connections list
                self.scanner.print_error(
                    self.symbol,
                    self.connection_first_device,
                    self.connection_second_device)
                print("One or both of these devices do not exist.")
            else:
                # Error is in monitors list
                self.scanner.print_error(
                    self.symbol, self.monitor_device)
                print("Device does not exist.")

        elif errorid == "network":
            print("Not all inputs in the network are connected.")

        elif errorid == self.monitors.NO_ERROR:
            self.semantic_errors_list.pop()
        elif errorid == self.monitors.NOT_OUTPUT:
            self.scanner.print_error(
                self.symbol, self.monitor_device)
            print("Not a valid output.")
        elif errorid == self.monitors.MONITOR_PRESENT:
            self.scanner.print_error(
                self.symbol, self.monitor_device)
            print("This output is already being monitored.")

        return None
