#!/usr/bin/env python

from datetime import date, timedelta
from lab_defs import teaching_length
start_michaelmas = date(2018, 10, 4)
start_hilary = date(2019, 2, 7)
hilary_length = 10
start_trinity = date(2019, 5, 9)
trinity_length = teaching_length - hilary_length

semester1_dates = [start_michaelmas + timedelta(days = i * 7) for i in range(teaching_length)]
semester2_dates = ([start_hilary + timedelta(days = i * 7) for i in range(hilary_length)] +
                   [start_trinity + timedelta(days = i * 7) for i in range(trinity_length)])
all_dates = semester1_dates + semester2_dates
