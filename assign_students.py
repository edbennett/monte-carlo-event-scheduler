#!/usr/bin/env python

import csv

from lab_defs import Student, teaching_length
from lab_mc import num_theory

def get_students(filename):
    students = {}
    with open(filename, 'r') as f:
        student_reader = csv.reader(f, delimiter=',', quotechar='"')
        for record in student_reader:
            students[record[1][:6]] = Student("{} {}".format(record[3],record[2]), record[1][:6], None, None, int(record[4]), record[5])
    return students

def match_students(students, pairs):
    for student in students.values():
        student.tb1_experiments = pairs[student.pair_number - 1][:teaching_length]
        if student.pair_number > num_theory:
            student.tb2_experiments = pairs[student.pair_number - 1][teaching_length:]
        else:
            student.tb2_experiments = []


if __name__ == "__main__":
    from sys import exit, argv

    students = get_students("students.csv")
    student_number = argv[1]
    if not student_number in students:
        print("No such student")
        exit()
    student = [students[student_number]]
    import pickle
    with open("schedule.dat", "rb") as f:
        pairs = pickle.load(f)
    match_students(students,pairs)
    from print_student import build_document
    from weeks import semester1_dates, semester2_dates
    build_document(student, semester1_dates + semester2_dates, "1+2", "{}.pdf".format(student_number))
