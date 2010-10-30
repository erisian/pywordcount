#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
class MockVimBuffer(object):

    def __init__(self):
        self.lines = []

    def __contains__(self, item):
        return item in self.lines

    def __iter__(self):
        return self.lines.__iter__()

    def __getitem__(self, index):
        return self.lines.__getitem__(index)

    def __setitem__(self, index, value):
        return self.lines.__setitem__(index, value)

class MockVimCurrent(object):

    def __init__(self):
        self.__dict__["buffer"] = MockVimBuffer()

    def __setattr__(self, attr, value):
        if attr == "buffer":
            self.__dict__["buffer"].lines = value
        else:
            self.__dict__[attr] = value

class MockVim(object):

    def __init__(self):
        self.current = MockVimCurrent()
        self.commands = []
        self.eval_list ={
            "exists('b:TotalWordCount')": lambda: False,
        }

    def eval(self, command):
        return self.eval_list.get(command, lambda: "")()

    def command(self, command):
        self.commands.append(command)

class EmptyObject(object):
    range = None
