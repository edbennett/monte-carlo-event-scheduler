#!/usr/bin/env python

from collections import namedtuple
#Student = namedtuple("Student", ["name", "number", "tb1_experiments", "tb2_experiments", "pair_number", "cymraeg"])
class Student:
    def __init__(self, name, number, tb1_experiments, tb2_experiments, pair_number, cymraeg=False):
        self.name = name
        self.number = number
        self.tb1_experiments = tb1_experiments
        self.pair_number = pair_number
        self.cymraeg = cymraeg

    def __lt__(self, other):
        return self.number < other.number

Experiment = namedtuple("Experiment", ["number", "title", "teitl", "acronym", "count", "writeup", "reserve", "fixed", "undesirable"])
Experiment.__new__.__defaults__ = (4, True, False, False, False)

teaching_length = 11
