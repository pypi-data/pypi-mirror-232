#!/usr/bin/env python3
import pytest

from subc import Command


def test_basic():
    cmd = None

    class MyBase(Command):
        description = 'foo'

        def run(self):
            nonlocal cmd
            cmd = self

    class FirstCmd(MyBase):
        name = 'first'

        def add_args(self, parser):
            parser.add_argument('required', type=str)
            parser.add_argument('--foobar', action='store_true')

    class SecondCmd(MyBase):
        name = 'second'

    MyBase.main('bar', args=['first', 'blah', '--foobar'])
    assert isinstance(cmd, FirstCmd)
    assert cmd.args.foobar
    assert cmd.args.required == 'blah'
    MyBase.main('bar', args=['second'])
    assert isinstance(cmd, SecondCmd)


def test_shortest_prefix():
    cmd = None

    class MyBase(Command):
        description = 'foo'

        def run(self):
            nonlocal cmd
            cmd = self

    class FirstCmd(MyBase):
        name = 'first'

    class SecondCmd(MyBase):
        name = 'second'

    class FindCmd(MyBase):
        name = 'find'

    class AppCmd(MyBase):
        name = 'app'

    class ApplyCmd(MyBase):
        name = 'apply'

    cases = [
        ('f', None),
        ('fi', None),
        ('fir', FirstCmd),
        ('fin', FindCmd),
        ('first', FirstCmd),
        ('a', None),
        ('ap', None),
        ('app', AppCmd),
        ('appl', ApplyCmd),
        ('apply', ApplyCmd),
        ('s', SecondCmd),
    ]
    for arg, cls in cases:
        try:
            MyBase.main('blah', args=[arg], shortest_prefix=True)
            assert isinstance(cmd, cls)
        except SystemExit:
            assert cls is None


def test_shortest_prefix_disabled():
    class MyBase(Command):
        description = 'foo'

        def run(self):
            ''

    class FirstCmd(MyBase):
        name = 'first'

    class SecondCmd(MyBase):
        name = 'second'

    with pytest.raises(SystemExit):
        MyBase.main('blah', args=['fir'])


def test_shortest_prefix_dup():
    class MyBase(Command):
        description = 'foo'

        def run(self):
            ''

    class FirstCmd(MyBase):
        name = 'first'

    class SecondCmd(MyBase):
        name = 'first'

    with pytest.raises(ValueError):
        MyBase.main('blah', args=['fir'], shortest_prefix=True)


def test_default():
    cmd = None

    class MyBase(Command):
        description = 'foo'

        def run(self):
            nonlocal cmd
            cmd = self

    class FirstCmd(MyBase):
        name = 'first'

    class SecondCmd(MyBase):
        name = 'second'

    MyBase.main('blah', args=[], default='second')
    assert isinstance(cmd, SecondCmd)


def test_nodefault():
    class MyBase(Command):
        description = 'foo'

        def run(self):
            ''

    class FirstCmd(MyBase):
        name = 'first'

    class SecondCmd(MyBase):
        name = 'second'

    with pytest.raises(Exception):
        MyBase.main('blah', args=[])


def test_intermediate_not_included():
    class MyBase(Command):
        description = 'foo'

        def run(self):
            ''

    class Intermediate(MyBase):
        name = 'intermediate'

        def add_args(self, parser):
            parser.add_argument('--foo', action='store_true')

    class SecondCmd(Intermediate):
        name = 'second'

    with pytest.raises(SystemExit):
        MyBase.main('blah', args=['intermediate'])
