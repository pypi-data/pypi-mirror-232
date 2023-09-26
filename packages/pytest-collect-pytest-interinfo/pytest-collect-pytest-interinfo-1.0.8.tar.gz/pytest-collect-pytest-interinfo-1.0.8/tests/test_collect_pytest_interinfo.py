# -*- coding: utf-8 -*-
import pytest

def test_collectinfo(pytester):

    pytester.makepyfile(
        """
        def test_getinfo():
            print("hello world")
        """
    )

    # run all tests with pytest
    result = pytester.runpytest("--collectinfo")
    print(result.stderr.lines)
    # assert result.ret == 0
