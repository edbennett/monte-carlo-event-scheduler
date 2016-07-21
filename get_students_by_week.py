#!/usr/bin/env python

from weeks import all_dates
from datetime import date, timedelta
from sys import argv, exit
from loadstore import load_pairs
from lab_mc import null_experiment, experiments
from itertools import zip_longest
from assign_students import get_students

if __name__ == "__main__":
    if len(argv) < 5:
        printf("Usage: python get_students_by_week YYYY MM DD XXX")
        printf("       where XXX is the acronym for the experiment")
        exit()
    target_date = date(int(argv[1]), int(argv[2]), int(argv[3]))
    if not (target_date in all_dates or target_date + timedelta(days=-1) in all_dates):
        printf("Date not found.")
        exit()
    
    if target_date + timedelta(days=-1) in all_dates:
        target_date += timedelta(days=-1)

    pairs = load_pairs("schedule.dat")
    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))

    target_index = all_dates.index(target_date)
    week = experiments_by_week[target_index]
    
    found_pairs = [pair + 1
                   for pair, ex in enumerate(week) 
                   if ex.acronym == argv[4] or ex.acronym == "{}*".format(argv[4])]
    students = get_students("students.csv")
    found_students = [student
                      for student in students.values()
                      if student.pair_number in found_pairs]
    print("Found pairs: {}".format(", ".join(map(str, found_pairs))))
    print("Found students:")
    for student in sorted(found_students):
        print(" - {} {}".format(student.number, student.name))
        
