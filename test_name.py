import pytest
from names import Names

"""Test the names module."""


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    return my_name


def test_get_name_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (3, None)
])
def test_get_name_string(used_names, new_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None


@pytest.mark.parametrize("expected_id_list, name_list", [
    ([1, 2, 3], ["Bob", "Eve", "John"])
])
def test_lookup(used_names, new_names, expected_id_list, name_list):
    """Test if lookup returns the expected string id, or adds to the list
    and return new id if string not present."""
    # Name is present
    assert used_names.lookup(name_list) == expected_id_list


@pytest.mark.parametrize("expected_query_id_list, name_list_2", [
    ([0, 2, None, None], ["Alice", "Eve", "John", 423])
])
def test_query(used_names, new_names, expected_query_id_list, name_list_2):
    """Test if lookup returns the expected string id, or adds to the list
    and return new id if string not present."""
    # Name is present
    for i in range(len(name_list_2)):
        assert used_names.query(name_list_2[i]) == expected_query_id_list[i]
