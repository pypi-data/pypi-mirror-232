# -*- coding: utf-8 -*-
import pytest


def test_collectinfo(pytester):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    pytester.makepyfile("""
        def test_getinfo():
            method = interface.api_v2_users_info_get
            result = method(token="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEyNywiZXhwIjoxNjk1ODgzNjMwfQ.B1yYArU01qWuYxH2mczJtNxtCj1HY0PzO20edJIBBu0")
    """)

    # run pytest with the following cmd args
    result = pytester.runpytest(
        '--collectinfo',
    )

    # fnmatch_lines does an assertion internally
    # result.stdout.fnmatch_lines([
    #     '*::test_sth PASSED*',
    # ])

    # make sure that that we get a '0' exit code for the testsuite
    # assert result.ret == 0

# def test_help_message(testdir):
#     result = testdir.runpytest(
#         '--help',
#     )
#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         'collect_info_plugin:',
#         '*--foo=DEST_FOO*Set the value for the fixture "bar".',
#     ])


# def test_hello_ini_setting(testdir):
#     testdir.makeini("""
#         [pytest]
#         HELLO = world
#     """)

#     testdir.makepyfile("""
#         import pytest

#         @pytest.fixture
#         def hello(request):
#             return request.config.getini('HELLO')

#         def test_hello_world(hello):
#             assert hello == 'world'
#     """)

#     result = testdir.runpytest('-v')

#     # fnmatch_lines does an assertion internally
#     result.stdout.fnmatch_lines([
#         '*::test_hello_world PASSED*',
#     ])

#     # make sure that that we get a '0' exit code for the testsuite
#     assert result.ret == 0
