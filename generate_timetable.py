#!/usr/bin/env python


from lab_mc import schedule, null_start, cold_start, tableform, null_experiment, tableform
from lab_defs import Student
from assign_students import get_students, match_students
from print_student import build_document
from weeks import semester1_dates, semester2_dates
from sys import exit, argv
from loadstore import load_pairs, save_pairs
from itertools import zip_longest 

include_names = True
out_filename = 'coversheets.pdf'
students_filename = 'students.csv'
print_table = False
if len(argv) < 2:
    generated_already = True
elif argv[1] == "new":
    generated_already = False
elif argv[1] == "table":
    generated_already = True
    print_table = True
elif argv[1] == "anon":
    generated_already = True
    include_names = False
    out_filename = 'anon.pdf'
    students_filename = 'pairs.csv'
else:
    print("Syntax: python generate_timetable.py [new]")
    exit()

if generated_already:
    print("Reading in experiments…")
    pairs = load_pairs("schedule.dat")
    if print_table:
        tableform(pairs)
        exit()
else:
    print("Scheduling experiments…")
    pairs, success = schedule(cold_start)
    if not success:
        print(tableform(pairs))
        exit()
        
    print("Done! Dumping to disk…")
    save_pairs(pairs, "schedule.dat")

print("Done! Now assigning to students…")
students = get_students(students_filename)
match_students(students, pairs)

print("Done! Now generating cover sheets…")
#print("generate_timetable", include_names)
build_document(sorted(list(students.values())), semester1_dates + semester2_dates, "1+2", out_filename, include_names=include_names)

#print("Done! Now generating experiment count list…")
#experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))
#build_document(experiments_by_week, "1+2", 2, "list.pdf")

print("Done!!")
