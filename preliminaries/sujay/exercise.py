#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
import mynames


def open_file(path):
    """Open and return the file specified by path."""
    try:
        file_object = open(path)
    except BaseException:
        print("There was an error opening the file!")
        sys.exit()

    return file_object


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    letter = input_file.read(1)
    return letter


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    letter = input_file.read(1)
    while letter.isspace():
        letter = input_file.read(1)
    return letter


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    letter = input_file.read(1)
    if letter.isdigit():
        nextletter = input_file.read(1)
        while nextletter.isdigit():
            letter += nextletter
            nextletter = input_file.read(1)
        return [int(letter), nextletter]

    else:
        return [None, letter]


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    letter = input_file.read(1)
    if letter.isalpha():
        nextletter = input_file.read(1)
        while nextletter.isalnum():
            letter += nextletter
            nextletter = input_file.read(1)
        return [letter, nextletter]

    else:
        return [None, letter]


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:

        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        print(arguments[0])

        fileobj = open_file(arguments[0])

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        while True:
            lettertoprint = get_next_character(fileobj)
            if lettertoprint == '':
                break
            print(lettertoprint, end='')

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        fileobj.seek(0, 0)
        while True:
            lettertoprint = get_next_non_whitespace_character(fileobj)
            if lettertoprint == '':
                break
            print(lettertoprint, end='')

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        fileobj.seek(0, 0)
        while True:
            lettertoprint = get_next_number(fileobj)
            if lettertoprint[1] == '':
                break
            if lettertoprint[0] is not None:
                print(lettertoprint[0])

        print("\nNow reading names...")
        # Print out all the names in the file
        fileobj.seek(0, 0)
        while True:
            lettertoprint = get_next_name(fileobj)
            if lettertoprint[1] == '':
                break
            if lettertoprint[0] is not None:
                print(lettertoprint[0])

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        fileobj.seek(0, 0)
        name = mynames.MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]
        while True:
            lettertoprint = get_next_name(fileobj)
            if lettertoprint[1] == '':
                break
            if lettertoprint[0] is not None and name.lookup(
                    lettertoprint[0]) not in bad_name_ids:
                print(lettertoprint[0])


if __name__ == "__main__":
    main()
