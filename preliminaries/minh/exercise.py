#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    try:
        f = open(path, "r")
        return f
    except BaseException:
        print("Path does not exist")
        return


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    character = input_file.read(1)
    return character


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    character = input_file.read(1)
    while character.isspace():
        character = input_file.read(1)
    return character


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    character = input_file.read(1)

    if character.isdigit():
        number = ''
        while character.isdigit():
            number += character
            character = input_file.read(1)
        output = [int(number), character]
    else:
        output = [None, character]
    return output


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    character = input_file.read(1)

    if character.isalpha():
        name = ''
        while character.isalnum():
            name += character
            character = input_file.read(1)
        output = [name, character]
    else:
        output = [None, character]
    return output


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:
        path = arguments[0]

        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        print(path)
        file = open_file(path)

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        while True:
            next_character = get_next_character(file)
            if next_character == '':
                break
            print(next_character, end='')

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        file.seek(0, 0)
        while True:
            next_character = get_next_non_whitespace_character(file)
            if next_character == '':
                break
            print(next_character, end='')

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        file.seek(0, 0)
        while True:
            next_number = get_next_number(file)
            if next_number[0]:
                print(next_number[0])
            if next_number[1] == '':
                break

        print("\nNow reading names...")
        # Print out all the names in the file
        file.seek(0, 0)
        while True:
            next_name = get_next_name(file)
            if next_name[0]:
                print(next_name[0])
            if next_name[1] == '':
                break

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]
        file.seek(0, 0)
        while True:
            next_name = get_next_name(file)
#            print(next_name,'-----------')
            if next_name[0]:
                valid = next_name[0]
                ID = name.lookup(valid)
                try:
                    bad_name_ids.index(ID)
                except BaseException:
                    good = name.get_string(ID)
                    print(good)
            else:
                pass
            if next_name[1] == '':
                break


if __name__ == "__main__":
    main()
