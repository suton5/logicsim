import pytest

from names import Names
from scanner import Scanner


@pytest.fixture
def type_scanner():
    """Return a scanner instance that reads a file containing only names
    or keywords"""
    my_name = Names()
    type_scanner = Scanner("test_def_files/for_get_symbol_type.txt", my_name)
    return type_scanner


@pytest.fixture
def name_scanner():
    """Return a scanner instance that reads a file containing only names
    or keywords"""
    my_name = Names()
    name_scanner = Scanner("test_def_files/for_get_symbol_id.txt", my_name)
    return name_scanner


@pytest.fixture
def error_scanner():
    """Return a scanner instance that reads a file containing print error examples"""
    my_name = Names()
    error_scanner = Scanner("test_def_files/for_print_error.txt", my_name)
    return error_scanner


def test_get_symbol_type(type_scanner):
    """Test the get_symbol function returns all possible
    correct types"""
    symbol = type_scanner.get_symbol()
    types = []
    while symbol.type != type_scanner.EOF:
        types.append(symbol.type)
        symbol = type_scanner.get_symbol()
    types.append(symbol.type)
    type_actual = [
        type_scanner.NAME,
        type_scanner.NAME,
        type_scanner.KEYWORD,
        type_scanner.NAME,
        type_scanner.KEYWORD,
        type_scanner.NAME,
        type_scanner.NUMBER,
        type_scanner.NUMBER,
        type_scanner.PERIOD,
        type_scanner.NUMBER,
        type_scanner.INVALID,
        type_scanner.ARROW,
        type_scanner.INVALID,
        type_scanner.INVALID,
        type_scanner.INVALID,
        type_scanner.NAME,
        type_scanner.EQUALS,
        type_scanner.COMMA,
        type_scanner.SEMICOLON,
        type_scanner.PERIOD,
        type_scanner.INVALID,
        type_scanner.INVALID,
        type_scanner.INVALID,
        type_scanner.INVALID,
        type_scanner.INVALID,
        type_scanner.EOF]
    assert types == type_actual


def test_get_symbol_id(name_scanner):
    """Test the get_symbol function returns correct id from names list
    For keywords, return initialised id. For names, return appropriate id
    For new names, add names to names list and return that id
    For numbers, return number as actual id"""
    symbol = name_scanner.get_symbol()
    name_id = []
    while symbol.type != name_scanner.EOF:
        name_id.append(symbol.id)
        symbol = name_scanner.get_symbol()
    name_id.append(symbol.id)
    id_actual = [name_scanner.START_ID,
                 name_scanner.END_ID,
                 name_scanner.DEVICES_ID,
                 name_scanner.CONNECTIONS_ID,
                 name_scanner.MONITORS_ID,
                 name_scanner.ip_ID,
                 name_scanner.init_ID,
                 name_scanner.cycles_ID,
                 name_scanner.CLOCK_ID,
                 name_scanner.SWITCH_ID,
                 name_scanner.AND_ID,
                 name_scanner.NAND_ID,
                 name_scanner.OR_ID,
                 name_scanner.NOR_ID,
                 name_scanner.DTYPE_ID,
                 name_scanner.XOR_ID,
                 name_scanner.Q_ID,
                 name_scanner.QBAR_ID,
                 name_scanner.DATA_ID,
                 name_scanner.CLK_ID,
                 name_scanner.SET_ID,
                 name_scanner.CLEAR_ID] + [5,
                                           6,
                                           7,
                                           8,
                                           9,
                                           10,
                                           100] + list(range(len(name_scanner.keywords_list),
                                                             len(name_scanner.keywords_list) + 12)) + [name_scanner.START_ID,
                                                                          name_scanner.END_ID,
                                                                          name_scanner.DEVICES_ID,
                                                                          name_scanner.CONNECTIONS_ID,
                                                                          name_scanner.MONITORS_ID] + list(range(len(name_scanner.keywords_list),
                                                                                                                 len(name_scanner.keywords_list) + 12)) + [None]
    assert name_id == id_actual


def test_get_symbol_add_names(name_scanner):
    '''Test that get symbol appends new names to name list as it reads the symbols
    and it doesn't add numbers to the names list'''
    initialised_name_list_length = len(name_scanner.names.names)
    # Check that all the keywords are appended to the names list on
    # initialisation
    assert initialised_name_list_length == len(name_scanner.keywords_list)
    symbol = name_scanner.get_symbol()
    while symbol.type != name_scanner.EOF:
        symbol = name_scanner.get_symbol()
    final_name_list_length = len(name_scanner.names.names)
    # assert that all new names are added to the names list as it is read and
    # numbers are ignored
    assert final_name_list_length == initialised_name_list_length + 12


def test_get_symbol_position(type_scanner):
    symbol = type_scanner.get_symbol()
    positions = []
    while symbol.type != type_scanner.EOF:
        positions.append((symbol.line, symbol.line_pos))
        symbol = type_scanner.get_symbol()
    positions.append((symbol.line, symbol.line_pos))
    # Weird thing happens here where if last symbol in line is character then
    # the position shifted by 1 to the right
    position_actual = [(1, 4), (1, 9), (1, 15), (1, 21), (1, 24), (1, 28),
                       (2, 1), (2, 3), (2, 4), (2, 5), (2, 8),
                       (3, 1), (3, 4), (3, 5), (3, 8), (3, 13),
                       (4, 0), (4, 2), (4, 4), (4, 6),
                       (5, 0), (5, 2), (5, 4), (5, 6), (5, 8), (5, 8)]
    assert positions == position_actual


@pytest.mark.parametrize("compare_file", [
    "test_def_files/space_invariant.txt",
    "test_def_files/block_comment_invariant.txt",
    "test_def_files/line_comment_invariant.txt"
])
def test_skip_things(name_scanner, compare_file):
    '''Test if scanner is space, line break invariant and comment invariant
    by comparing two texts with same symbols and different spacing/comments'''
    my_name = Names()
    compare_scanner = Scanner(compare_file, my_name)
    name_id = []
    compare_id = []

    symbol1 = name_scanner.get_symbol()
    while symbol1.type != name_scanner.EOF:
        name_id.append(symbol1.type)
        symbol1 = name_scanner.get_symbol()
    name_id.append(symbol1.type)

    symbol2 = compare_scanner.get_symbol()
    while symbol2.type != compare_scanner.EOF:
        compare_id.append(symbol2.type)
        symbol2 = compare_scanner.get_symbol()
    compare_id.append(symbol2.type)
    assert compare_id == name_id


def test_print_error_correct_place(capfd, error_scanner):
    '''Test the print_error in the scanner so that it can
    print carrot at the end of correct error symbol
    and the next symbol fetched is the symbol immediately after'''
    for i in range(3):
        symbol = error_scanner.get_symbol()
    error_scanner.print_error(symbol, symbol)
    out, err = capfd.readouterr()
    next_symbol = error_scanner.get_symbol()
    assert out == "Error occured in line  1\nSTART END DEVICES CONNECTIONS MONITORS\n                ^\n"
    assert next_symbol.id == error_scanner.CONNECTIONS_ID


def test_print_error_2_inputs(capfd, error_scanner):
    '''Test the print_error gives the carrot under the second input parameter
    and fetch symbol immediately after first parameter'''
    for i in range(2):
        symbol_1 = error_scanner.get_symbol()
    for i in range(2):
        symbol_2 = error_scanner.get_symbol()
    error_scanner.print_error(symbol_2, symbol_1)
    out, err = capfd.readouterr()
    next_symbol = error_scanner.get_symbol()
    assert out == "Error occured in line  1\nSTART END DEVICES CONNECTIONS MONITORS\n        ^\n"
    assert next_symbol.id == error_scanner.MONITORS_ID
    error_scanner.print_error(symbol_1, symbol_2)
    out, err = capfd.readouterr()
    next_symbol = error_scanner.get_symbol()
    assert out == "Error occured in line  1\nSTART END DEVICES CONNECTIONS MONITORS\n                            ^\n"
    assert next_symbol.id == error_scanner.DEVICES_ID


def test_print_error_2_carrots(capfd, error_scanner):
    '''Test print_error gives the two carrots under second and third parameter
    and fetches symbol after first parameter'''
    for i in range(1):
        symbol_1 = error_scanner.get_symbol()
    for i in range(2):
        symbol_2 = error_scanner.get_symbol()
    for i in range(2):
        symbol_3 = error_scanner.get_symbol()

    error_scanner.print_error(symbol_3, symbol_1, symbol_2)
    out, err = capfd.readouterr()
    next_symbol = error_scanner.get_symbol()
    print(out)
    assert out == "Error occured in line  1\nSTART END DEVICES CONNECTIONS MONITORS\n    ^           ^\n"
    assert next_symbol.id == error_scanner.ip_ID


def test_print_error_end_linebreak(capfd, error_scanner):
    '''Test that print_error only prints the error line up until a semicolon
    line break or the end of the file, whichever comes first
    Case: Linebreak'''
    for i in range(11):
        symbol = error_scanner.get_symbol()
    error_scanner.print_error(symbol, symbol)
    out, err = capfd.readouterr()
    print(out)
    assert out == "Error occured in line  2\nip init cycles CLOCK; SWITCH AND NAND OR NOR\n                           ^\n"


def test_print_error_end_semicolon(capfd, error_scanner):
    '''Test that print_error only prints the error line up until a line break
     or the end of the file, whichever comes first
    Case: EOF'''
    for i in range(16):
        symbol = error_scanner.get_symbol()
    error_scanner.print_error(symbol, symbol)
    out, err = capfd.readouterr()
    assert out == "Error occured in line  3\nchrists college cambridge\n      ^\n"
