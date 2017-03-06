#!/usr/bin/env python

from lab_mc import experiments, null_experiment
from lab_defs import teaching_length
from weeks import all_dates
from loadstore import load_pairs
from assign_students import get_students, match_students
from get_students_by_week import get_students_by_pair, get_pairs_by_week
from sys import argv
from itertools import zip_longest
from datetime import timedelta, date

def get_dates(argv):
    if len(argv) < 3:
        # borrowing http://stackoverflow.com/questions/8801084/how-to-calculate-next-friday-in-python            
        to_date = date.today()
        to_date += timedelta( (4-to_date.weekday()) % 7 - 1) # Get the Thursday before the next Friday           
        from_date = to_date - timedelta(7)
    elif len(argv) < 6:
        to_date = date.today()
        to_date += timedelta( (4-to_date.weekday()) % 7 - 1) # Get the Thursday before the next Friday           
        from_date = date(int(argv[1]), int(argv[2]), int(argv[3]))
    else:
        to_date = date(int(argv[4]), int(argv[5]), int(argv[6]))
        from_date = date(int(argv[1]), int(argv[2]), int(argv[3]))
    return to_date, from_date

if __name__ == "__main__":
    to_date, from_date = get_dates(argv)

    pairs = load_pairs("schedule.dat")
    students = get_students("students.csv")
    match_students(students, pairs)
    
    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))

    for experiment in experiments.values():
        found_pairs = get_pairs_by_week(from_date, experiment.acronym, all_dates, experiments_by_week)
        found_students = get_students_by_pair(students.values(), found_pairs)
        
        print("{}:".format(experiment.title))
        for student in sorted(found_students):
            student_experiments = student.tb1_experiments + student.tb2_experiments
            print(" - {} {}\t{}".format(student.number, student.name,
                                        student_experiments[all_dates.index(to_date)].acronym))

        
