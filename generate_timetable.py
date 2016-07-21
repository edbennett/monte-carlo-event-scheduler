#!/usr/bin/env python


from lab_mc import schedule, cold_start, tableform, null_experiment
from lab_defs import Student
from assign_students import get_students, match_students
from print_student import build_document
from weeks import semester1_dates, semester2_dates
from sys import exit, argv
from loadstore import load_pairs, save_pairs
from itertools import zip_longest 

if len(argv) < 2:
    generated_already = True
elif argv[1] == "new":
    generated_already = False
else:
    print("Syntax: python generate_timetable.py [new]")

if generated_already:
    print("Reading in experiments…")
    pairs = load_pairs("schedule.dat")
else:
    print("Scheduling experiments…")
    pairs, success = schedule(cold_start)
    if not success:
        print(tableform(pairs))
        exit()
        
    print("Done! Dumping to disk…")
    save_pairs(pairs, "schedule.dat")

print("Done! Now assigning to students…")
students = get_students('students.csv')
match_students(students, pairs)

print("Done! Now generating cover sheets…")
build_document(sorted(list(students.values())), semester1_dates + semester2_dates, "1+2", 'coversheets.pdf')

#print("Done! Now generating experiment count list…")
#experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))
#build_document(experiments_by_week, "1+2", 2, "list.pdf")

print("Done!!")
