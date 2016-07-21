#!/usr/bin/env python

import pickle

def load_pairs(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)

def save_pairs(pairs, filename):
    with open(filename, "wb") as f:
        return pickle.dump(pairs, f)
