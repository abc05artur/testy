import unittest
import pytest


# ut1=unittest.TestCase()
# ut1.assertEqual()

@pytest.fixture
def tt():
    print("called" + "*" * 20)
    return 3


def test_1(tt):
    print("t1")
    assert tt == 1


def test_2(tt):
    assert tt == 2


def test_3(tt):
    assert tt == 3
