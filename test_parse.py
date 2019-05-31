"""Test the parse module."""
import pytest

from names import Names
from devices import Devices
from parse import Parser
from scanner import Scanner
from scanner import Symbol
from network import Network
from monitors import Monitors


@pytest.fixture
def basic_parser():
    """Return a new instance of the Parser module,
    using a test description file."""
    new_names = Names()
    new_scanner = Scanner("test_def_files/checkbasicfunctions.txt", new_names)
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    return Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner)


def test_semicolon_skipper(basic_parser):
    """Tests the semicolon_skipper function."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.semicolon_skipper()
    assert my_parser.symbol.type == my_scanner.SEMICOLON


def test_check_semicolon_else_skip1(basic_parser):
    """Tests that check_semicolon_else_skip function returns no errors
    if checking a semicolon."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_semicolon_else_skip(my_parser.symbol)
    assert len(my_parser.syntax_errors_list) == 0


def test_check_semicolon_else_skip2(basic_parser):
    """Tests that check_semicolon_else_skip function
    gives required error if not checking a semicolon."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_semicolon_else_skip(my_parser.symbol)
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "semicolon"


def test_check_fixed_start1(basic_parser):
    """Tests that check_fixed_start gives no error if START is provided."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.check_fixed_start()
    assert len(my_parser.syntax_errors_list) == 0


def test_check_fixed_start2(basic_parser):
    """Tests that check_fixed_start gives the required error if
    START is not provided."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_fixed_start()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "start"


def test_check_fixed_others1(basic_parser):
    """Tests that check_fixed_others gives no error if DEVICES is
    provided before semicolon, and that it checks for the semicolon."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_fixed_others(my_scanner.DEVICES_ID)
    assert len(my_parser.syntax_errors_list) == 0
    assert my_parser.symbol.type == my_scanner.SEMICOLON


def test_check_fixed_others2(basic_parser):
    """Tests that check_fixed_others gives no error if DEVICES is provided,
    but gives semicolon error if not followed by semicolon. Also check if
    skips to semicolon."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_fixed_others(my_scanner.DEVICES_ID)
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "semicolon"
    assert my_parser.symbol.type == my_scanner.SEMICOLON


def test_check_fixed_others3(basic_parser):
    """Tests that check_fixed_others gives error if DEVICES is not provided,
    and also that it skips to semicolon."""
    my_parser = basic_parser
    my_scanner = my_parser.scanner
    my_parser.check_fixed_others(my_scanner.DEVICES_ID)
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == my_scanner.DEVICES_ID
    assert my_parser.symbol.type == my_scanner.SEMICOLON


@pytest.fixture
def parameter_parser():
    """Return a new instance of the Parser module, using a test
    description file."""
    new_names = Names()
    new_scanner = Scanner("test_def_files/sequential.txt", new_names)
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    return Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner)


@pytest.mark.parametrize("param, correct", [
    ("(Symbol(my_scanner.NAME, my_scanner.CLOCK_ID))", "False"),
    ("(Symbol(my_scanner.NAME, my_scanner.Q_ID))", "False"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.CLOCK_ID))", "True"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.Q_ID))", "False")
])
def test_check_validdevice(parameter_parser, param, correct):
    """Tests the check_validdevice function."""
    my_parser = parameter_parser
    my_scanner = my_parser.scanner
    left_expression = eval("".join(["my_parser.check_validdevice", param]))
    right_expression = eval(correct)
    assert left_expression == right_expression


@pytest.mark.parametrize("param, correct", [
    ("(Symbol(my_scanner.NAME, my_scanner.ip_ID))", "False"),
    ("(Symbol(my_scanner.NAME, my_scanner.Q_ID))", "False"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.ip_ID))", "True"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.Q_ID))", "False")
])
def test_check_validparam(parameter_parser, param, correct):
    """Tests the check_validparam function."""
    my_parser = parameter_parser
    my_scanner = my_parser.scanner
    left_expression = eval("".join(["my_parser.check_validparam", param]))
    right_expression = eval(correct)
    assert left_expression == right_expression


@pytest.mark.parametrize("param, correct", [
    ("(Symbol(my_scanner.NAME, my_scanner.DATA_ID))", "False"),
    ("(Symbol(my_scanner.NAME, my_scanner.Q_ID))", "False"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.DATA_ID))", "True"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.Q_ID))", "False")
])
def test_check_validdtypeinput(parameter_parser, param, correct):
    """Tests the check_validdtypeinput function."""
    my_parser = parameter_parser
    my_scanner = my_parser.scanner
    left_expression = eval("".join(["my_parser.check_validdtypeinput", param]))
    right_expression = eval(correct)
    assert left_expression == right_expression


@pytest.mark.parametrize("param, correct", [
    ("(Symbol(my_scanner.NAME, my_scanner.Q_ID))", "False"),
    ("(Symbol(my_scanner.NAME, my_scanner.ip_ID))", "False"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.Q_ID))", "True"),
    ("(Symbol(my_scanner.KEYWORD, my_scanner.ip_ID))", "False")
])
def test_check_validdtypeoutput(parameter_parser, param, correct):
    """Tests the check_validdtypeoutput function."""
    my_parser = parameter_parser
    my_scanner = my_parser.scanner
    left_expression = eval(
        "".join(["my_parser.check_validdtypeoutput", param]))
    right_expression = eval(correct)
    assert left_expression == right_expression


@pytest.fixture
def deviceline_parser():
    """Return a new instance of the Parser module, using a test
    description file."""
    new_names = Names()
    new_scanner = Scanner("test_def_files/for_check_deviceline.txt", new_names)
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    return Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner)


def test_check_deviceline1(deviceline_parser):
    """Tests check_deviceline to see if correct errors are raised
    in 1st line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "devicename"


def test_check_deviceline2(deviceline_parser):
    """Tests check_deviceline to see if correct errors are raised
    in 2nd line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    # Skips to 2nd line
    for i in range(9):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "equal"


def test_check_deviceline3(deviceline_parser):
    """Tests check_deviceline to see if correct errors are raised
    in 3rd line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    # Skips to 3rd line
    for i in range(18):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "devicetype"


def test_check_deviceline4(deviceline_parser):
    """Tests check_deviceline to see if correct errors are raised
    in 4th line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    # Skips to 4th line
    for i in range(26):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "semicoloncomma"


def test_check_deviceline5(deviceline_parser):
    """Tests check_deviceline to see if no errors are raised
    in 5th line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    # Skips to 5th line
    for i in range(33):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 0


def test_check_deviceline6(deviceline_parser):
    """Tests check_deviceline to see if correct errors are raised
    in 6th line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    # Skips to 6th line
    for i in range(41):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "parameter"


def test_check_paramindevice1(deviceline_parser):
    """Tests check_paramindevice to see if correct errors are raised
    in 7th line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    # Skips to 7th line
    for i in range(49):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "equal"


def test_check_paramindevice2(deviceline_parser):
    """Tests check_paramindevice to see if correct errors are raised
    in 8th line."""
    my_parser = deviceline_parser
    my_scanner = my_parser.scanner
    # Skips to 8th line
    for i in range(57):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_deviceline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "number"


@pytest.fixture
def connectionline_parser():
    """Return a new instance of the Parser module, using a test
    description file."""
    new_names = Names()
    new_scanner = Scanner(
        "test_def_files/for_check_connectionline.txt",
        new_names)
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    return Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner)


def test_check_validconnectionoutput1(connectionline_parser):
    """Tests check_validconnectionoutput to see if correct errors
    are raised in 1st line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "devicename"


def test_check_validconnectionoutput2(connectionline_parser):
    """Tests check_validconnectionoutput to see if correct errors
    are raised in 2nd line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 2nd line
    for i in range(7):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "arrowperiod"


def test_check_validconnectionoutput3(connectionline_parser):
    """Tests check_validconnectionoutput to see if correct errors
    are raised in 3rd line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 3rd line
    for i in range(15):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "doutput"


def test_check_validconnectioninput1(connectionline_parser):
    """Tests check_validconnectioninput to see if correct errors
    are raised in 4th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 4th line
    for i in range(23):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "devicename"


def test_check_validconnectioninput2(connectionline_parser):
    """Tests check_validconnectioninput to see if correct errors
    are raised in 5th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 5th line
    for i in range(29):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "period"


def test_check_validconnectioninput3(connectionline_parser):
    """Tests check_validconnectioninput to see if correct errors
    are raised in 6th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 6th line
    for i in range(35):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "input"


def test_check_validconnectioninput4(connectionline_parser):
    """Tests check_validconnectioninput to see if correct errors
    are raised in 7th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 7th line
    for i in range(41):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "number"


def test_check_connectionline1(connectionline_parser):
    """Tests check_connectionline to see if correct errors
    are raised in 8th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 8th line
    for i in range(47):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "arrow"


def test_check_connectionline2(connectionline_parser):
    """Tests check_connectionline to see if correct errors
    are raised in 9th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 9th line
    for i in range(56):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "comma"


def test_check_connectionline3(connectionline_parser):
    """Tests check_connectionline to see if correct errors
    are raised in 10th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 10th line
    for i in range(69):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 0


def test_check_connectionline4(connectionline_parser):
    """Tests check_connectionline to see if correct errors
    are raised in 11th line."""
    my_parser = connectionline_parser
    my_scanner = my_parser.scanner
    # Skips to 11th line
    for i in range(83):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_connectionline()
    assert len(my_parser.syntax_errors_list) == 0


@pytest.fixture
def monitorline_parser():
    """Return a new instance of the Parser module, using a
    test description file."""
    new_names = Names()
    new_scanner = Scanner(
        "test_def_files/for_check_monitorline.txt",
        new_names)
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    return Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner)


def test_check_monitorline1(monitorline_parser):
    """Tests check_monitorline to see if correct errors
    are raised in 1st line."""
    my_parser = monitorline_parser
    my_scanner = my_parser.scanner

    # Set the duplicate error checker to 1, since this is monitors list
    # Handles the fact that the same error id is used in both network and
    # monitor
    my_parser.duplicate_error_checker = 1

    my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_monitorline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "devicename"


def test_check_monitorline2(monitorline_parser):
    """Tests check_monitorline to see if correct errors
    are raised in 2nd line."""
    my_parser = monitorline_parser
    my_scanner = my_parser.scanner

    # Set the duplicate error checker to 1, since this is monitors list
    # Handles the fact that the same error id is used in both network and
    # monitor
    my_parser.duplicate_error_checker = 1

    # Skips to 2nd line
    for i in range(3):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_monitorline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "semicolon"


def test_check_monitorline3(monitorline_parser):
    """Tests check_monitorline to see if correct errors
    are raised in 3rd line."""
    my_parser = monitorline_parser
    my_scanner = my_parser.scanner

    # Set the duplicate error checker to 1, since this is monitors list
    # Handles the fact that the same error id is used in both network and
    # monitor
    my_parser.duplicate_error_checker = 1

    # Skips to 3rd line
    for i in range(4):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_monitorline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "doutput"


def test_check_monitorline4(monitorline_parser):
    """Tests check_monitorline to see if correct errors
    are raised in 4th line."""
    my_parser = monitorline_parser
    my_scanner = my_parser.scanner

    # Set the duplicate error checker to 1, since this is monitors list
    # Handles the fact that the same error id is used in both network and
    # monitor
    my_parser.duplicate_error_checker = 1

    # Skips to 4th line
    for i in range(8):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_monitorline()
    assert len(my_parser.syntax_errors_list) == 1
    assert my_parser.syntax_errors_list[0] == "semicolon"


def test_check_monitorline5(monitorline_parser):
    """Tests check_monitorline to see if correct errors
    are raised in 5th line."""
    my_parser = monitorline_parser
    my_scanner = my_parser.scanner

    # Set the duplicate error checker to 1, since this is monitors list
    # Handles the fact that the same error id is used in both network and
    # monitor
    my_parser.duplicate_error_checker = 1

    # Skips to 5th line
    for i in range(11):
        my_parser.symbol = my_scanner.get_symbol()
    my_parser.check_monitorline()
    assert len(my_parser.syntax_errors_list) == 0


def test_parse_network_correct():
    """Test the overall parse.py flow with a complicated
    enough but correct definition file."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/sequential.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that no semantic or syntax errors were made
    assert my_parser.parse_network()


def test_parse_network_incorrect_syntax():
    """Test the overall parse.py flow with a definition file
    with incorrect syntax."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/srbistablewrong.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    assert my_parser.parse_network() == False
    assert len(my_parser.syntax_errors_list) == 2
    assert my_parser.syntax_errors_list[0] == "start"
    assert my_parser.syntax_errors_list[1] == my_scanner.DEVICES_ID


def test_parse_network_incorrect_semantics1():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/deviceinvalidqualifier.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 2 semantic errors are raised (one from
    # network.check_network())
    assert len(my_parser.semantic_errors_list) == 2
    assert my_parser.semantic_errors_list[0] == my_devices.INVALID_QUALIFIER


def test_parse_network_incorrect_semantics2():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/devicenoqualifier.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 2 semantic errors are raised (one from
    # network.check_network())
    assert len(my_parser.semantic_errors_list) == 2
    assert my_parser.semantic_errors_list[0] == my_devices.NO_QUALIFIER


def test_parse_network_incorrect_semantics3():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/devicequalifierpresent.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 2 semantic errors are raised (one from
    # network.check_network())
    assert len(my_parser.semantic_errors_list) == 2
    assert my_parser.semantic_errors_list[0] == my_devices.QUALIFIER_PRESENT


def test_parse_network_incorrect_semantics4():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/deviceexists.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 2 semantic errors are logged (one from actual error, one from
    # network.check_network())
    assert len(my_parser.semantic_errors_list) == 2
    assert my_parser.semantic_errors_list[0] == my_devices.DEVICE_PRESENT


def test_parse_network_incorrect_semantics5():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner(
        "test_def_files/connectioninputconnected.txt",
        my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 2 semantic errors are logged (one from actual error, one from
    # network.check_network())
    assert len(my_parser.semantic_errors_list) == 2
    assert my_parser.semantic_errors_list[0] == my_network.INPUT_CONNECTED


def test_parse_network_incorrect_semantics6():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/connectionportabsent.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 2 semantic errors are logged (one from actual error, one from
    # network.check_network())
    assert len(my_parser.semantic_errors_list) == 2
    assert my_parser.semantic_errors_list[0] == my_network.PORT_ABSENT


def test_parse_network_incorrect_semantics7():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/connectiondeviceabsent.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 2 semantic errors are logged (one from actual error, one from
    # network.check_network())
    assert len(my_parser.semantic_errors_list) == 2
    assert my_parser.semantic_errors_list[0] == my_network.DEVICE_ABSENT


def test_parse_network_incorrect_semantics8():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/connectionchecknetwork.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 1 semantic error is logged (from network.check_network())
    assert len(my_parser.semantic_errors_list) == 1
    assert my_parser.semantic_errors_list[0] == "network"


def test_parse_network_incorrect_semantics9():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/monitornotoutput.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 1 semantic error is logged (from actual error)
    assert len(my_parser.semantic_errors_list) == 1
    assert my_parser.semantic_errors_list[0] == my_monitors.NOT_OUTPUT


def test_parse_network_incorrect_semantics10():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/monitorpresent.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 1 semantic error is logged (from actual error)
    assert len(my_parser.semantic_errors_list) == 1
    assert my_parser.semantic_errors_list[0] == my_monitors.MONITOR_PRESENT


def test_parse_network_incorrect_semantics11():
    """Test the overall parse.py flow with a definition file
    with incorrect semantics."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/monitordeviceabsent.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
    # Check that there are no syntax errors
    assert len(my_parser.syntax_errors_list) == 0
    # Check that 1 semantic error is logged (from actual error)
    assert len(my_parser.semantic_errors_list) == 1
    assert my_parser.semantic_errors_list[0] == my_network.DEVICE_ABSENT


def test_parse_network_incorrect_semantics12():
    """Test the overall parse.py flow with a definition file with incorrect
    semantics. Basically, this file opens a block comment but does not close
    it. Ensure that parser does not get stuck in infinite loop."""
    my_names = Names()
    my_scanner = Scanner("test_def_files/for_check_infiniteloop.txt", my_names)
    my_devices = Devices(my_names)
    my_network = Network(my_names, my_devices)
    my_monitors = Monitors(my_names, my_devices, my_network)
    my_parser = Parser(
        my_names,
        my_devices,
        my_network,
        my_monitors,
        my_scanner)
    # Check that parse_network() returns False
    assert my_parser.parse_network() == False
