#!/usr/bin/env python

from collections import namedtuple
from math import ceil
from collections import Counter
from itertools import zip_longest 
from random import randint, choice, random, shuffle
from math import exp
from sys import exit
from lab_defs import Experiment, teaching_length

num_pairs = 56
num_theory = 5
pairs_per_cohort = ceil(num_pairs / 4)

tutorials = {"NA": Experiment(201, "Numerical Analysis", "NA", count=75, writeup=False, fixed=True),
             "LVT": Experiment(298, "LabVIEW Tutorial", "LVT", count=75, writeup=False, fixed=True)}

experiments = {"DoS": Experiment(202, "Density of States", "DoS", writeup=False, undesirable=True),
               "ESR": Experiment(221, "Electron Spin Resonance", "ESR"),
               "BG": Experiment(222, 
                                '<font face="AvenirNext">α</font>, <font face="AvenirNext">β</font>, and <font face="AvenirNext">γ</font>-radiation', 
                                "BG"),
               "FHz": Experiment(223, "Franck Hertz", "FHz"),
               "RS": Experiment(224, "Rutherford Scattering", "RS"),
               "HL": Experiment(238, "Hubble's Law", "HL", writeup=False),
               "BS": Experiment(241, "Balmer Series of the Hydrogen Atom", "BS"),
               "VIS": Experiment(242, "Measurement of Viscosity", "VIS"),
               "POL": Experiment(244, "Polarimeter", "POL"),
               "MSD": Experiment(246, "Multiple Slit Diffraction", "MSD"),
               "EB": Experiment(247, "Edser Butler Method", "EB"),
               "BH": Experiment(261, "B/H Curve", "BH"),
               "LV": Experiment(299, "LabVIEW: Calibrating a Thermistor", "LV", count=12, writeup=False, undesirable=True)}
experiment_list = list(experiments.values())

reserve_experiments = {"SE": Experiment(248, "Diffraction at a Straight Edge", "SE", 4, True, True),
                       "EM": Experiment(204, "e/m", "EM", 2, True, True),
                       "GYR": Experiment(252, "Gyroscope", "GYR", 4, True, True), 
                       "MSA": Experiment(271, "More Spectroscopic Analysis", "MSA", 50, False, True),
                       "SA": Experiment(270, "Spectroscopic Analysis", "SA", writeup=False, undesirable=True)}

GP = ([Experiment("", "Group Project – Week {}".format(i+1), "", count=20, fixed=True) for i in range(4)]
      + [Experiment("", "Group Project – Presentations", "", count=40, fixed=True)])

writeup1 = Experiment("", "Report write-up time", "", count=75, fixed=True)
writeup2 = Experiment(" ", "Report write-up time", "", count=75, fixed=True)

null_experiment = Experiment("", "", "", count=1000)
bad_null = Experiment("", "", "—", count=0)

all_experiments = {**experiments, **reserve_experiments, **tutorials}

def cold_start():
    pairs = [[tutorials["NA"]] + [bad_null] * 10 for _ in range(num_pairs)]

    for pair in pairs[num_theory:]:
        pair.extend([tutorials["LVT"]] + [bad_null] * 10)
        
    for pair_idx, pair in enumerate(pairs):
        gp_semester = (2 * pair_idx) // num_pairs
        semester_cohort = ((4 * pair_idx) // num_pairs) % 2
        base = 1 + teaching_length * gp_semester + semester_cohort * 5
        pair[base:base+5] = GP
        if semester_cohort == 0:
            pair[teaching_length - 1] = writeup1
            pair[-1] = writeup2
        else:
            if gp_semester == 0:
                pair[teaching_length // 2] = writeup1
                pair[-1] = writeup2
            else:
                pair[teaching_length - 1] = writeup1
                pair[teaching_length + teaching_length // 2] = writeup2

    return pairs

#def hot_start():
#    pairs = [[tutorials["NA"]] +  for _ in range(num_theory)]

def badness(pairs):
    duplicate_badness = 0
    resource_badness = 0
    labview_badness = 0

    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))

    for pair in pairs:
        duplicate_badness += 5 * (1 - len(set(pair)) / len(pair))
        if len(pair) > teaching_length and experiments["LV"] not in pair:
            labview_badness += 1
        elif experiments["LV"] in pair and pair.index(experiments["LV"]) < teaching_length:
            labview_badness += 3
#        if experiments["POL"] in pair and experiments["POL*"] in pair:
#            duplicate_badness += 1
        
    for week in experiments_by_week:
        counter = Counter(week)
        for required_count, experiment in zip(counter.values(), counter.keys()):
            if required_count > experiment.count:
                resource_badness += 1

    return duplicate_badness, resource_badness, labview_badness

def unpleasantness(pairs):
    undesirable_count = sum(1
                            for pair in pairs
                            for experiment in pair 
                            if experiment.undesirable)

    very_undesirable_count = 0
    for pair in pairs:
        local_count = sum(1 for experiment in pair[1:11]
                          if experiment.undesirable 
                          or "Group project" in experiment.title
                          or experiment.title == "LabVIEW") - 5
        if local_count > 0:
            very_undesirable_count += local_count ** 2

        if len(pair) > 11:
            local_count = sum(1 for experiment in pair[12:]
                              if experiment.undesirable 
                              or "Group project" in experiment.title
                              or experiment.title == "LabVIEW") - 5
            if local_count > 0:
                very_undesirable_count += local_count ** 2

    return undesirable_count + 5 * very_undesirable_count

def unpleasant_badness(pairs):
    return sum(badness(pairs)) + 0.1 * unpleasantness(pairs)

def randomupdate(pairs, beta):
    while True:
        pair = randint(0, num_pairs - 1)
        week = randint(0, 2 * teaching_length)
        if week >= len(pairs[pair]):
            continue
        if pairs[pair][week].fixed:
            continue
        old_expt = pairs[pair][week]
        old_badness = unpleasant_badness(pairs)
        pairs[pair][week] = choice(experiment_list)
        new_badness = unpleasant_badness(pairs)

        if new_badness < old_badness:
            return 1, new_badness
        elif random() < exp(beta * (old_badness - new_badness)):
            return 1, new_badness
        else:
            pairs[pair][week] = old_expt
            return 0, old_badness

def pleasantupdate(pairs, beta):
    unpleasant_experiments = [(pair_index, experiment_index)
                              for pair_index, pair in enumerate(pairs)
                              for experiment_index, experiment in enumerate(pair)
                              if experiment.undesirable]
    pair, week = choice(unpleasant_experiments)
    old_expt = pairs[pair][week]
    old_badness = unpleasant_badness(pairs)
    pairs[pair][week] = choice(experiment_list)
    new_badness = unpleasant_badness(pairs)
    
    if new_badness < old_badness:
        return 1, new_badness
    elif random() < exp(beta * (old_badness - new_badness)):
        return 1, new_badness
    else:
        pairs[pair][week] = old_expt
        return 0, old_badness
    
def target_duplicates(pairs, beta):
    for pair_index, pair in enumerate(pairs):
        if len(set(pair)) < len(pair):
            old_badness = unpleasant_badness(pairs)
            counter = Counter(pair)
            experiment_to_replace, n = counter.most_common(1)[0]
            index_to_replace = randint(0,n)
            indices = [i for i, j in enumerate(pair) 
                       if j == experiment_to_replace]
            index_to_replace = choice(indices)
            pair[index_to_replace] = choice(experiment_list)
            new_badness = unpleasant_badness(pairs)
            
            if new_badness <= old_badness:
                return 1, new_badness
            elif random() < exp(beta * (old_badness - new_badness)):
                return 1, new_badness
            else:
                pair[index_to_replace] = experiment_to_replace
                return 0, old_badness
#        if experiments["POL"] in pair and experiments["POL*"] in pair:
#            old_badness = unpleasant_badness(pairs)
#            indices = [i for i, j in enumerate(pair)
#                       if j in polarimeters]
#            index_to_replace = choice(indices)
#            experiment_to_replace = pair[index_to_replace]
#            pair[index_to_replace] = choice(experiment_list)
#            new_badness = unpleasant_badness(pairs)
#
#            if new_badness <= old_badness:
#                return 1, new_badness
#            elif random() < exp(beta * (old_badness - new_badness)):
#                return 1, new_badness
#            else:
#                pair[index_to_replace] = experiment_to_replace
#                return 0, old_badness

    raise ValueError("targeting duplicates but look OK")

def target_resources(pairs, beta):
    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))
    for week_index, week in enumerate(experiments_by_week):
        counter = Counter(week)
        for required_count, experiment in zip(counter.values(), counter.keys()):
            if required_count > experiment.count:
                old_badness = unpleasant_badness(pairs)
                indices = [i for i, j in enumerate(week)
                           if j == experiment]
                index_to_replace = choice(indices)
                pairs[index_to_replace][week_index] = choice(experiment_list)
                new_badness = unpleasant_badness(pairs)
                
                if new_badness <= old_badness:
                    return 1, new_badness
                elif random() < exp(beta * (old_badness - new_badness)):
                    return 1, new_badness
                else:
                    pairs[index_to_replace][week_index] = experiment
                    return 0, old_badness
    raise ValueError("targeting resources but look OK")

def target_labview(pairs, beta):
    for pair_index, pair in enumerate(pairs):
        if pair_index >= num_theory and experiments["LV"] not in pair:
            old_badness = unpleasant_badness(pairs)
            while True:
                index_to_replace = randint(teaching_length + 1, teaching_length * 2 - 1)
                old_expt = pair[index_to_replace]
                if not old_expt.fixed:
                    break
            pair[index_to_replace] = experiments["LV"]
            new_badness = unpleasant_badness(pairs)

            if new_badness <= old_badness:
                return 1, new_badness
            elif random() < exp(beta * (old_badness - new_badness)):
                return 1, new_badness
            else:
                pair[index_to_replace] = old_expt
                return 0, old_badness

        indices = [i for i, j in enumerate(pair)
                   if j == experiments["LV"]]
        if len(indices) > 1:
            old_badness = unpleasant_badness(pairs)
            index_to_replace = choice(indices)
            pair[index_to_replace] = choice(experiments)
            new_badness = unpleasant_badness(pairs)

            if new_badness <= old_badness:
                return 1, new_badness
            elif random() < exp(beta * (old_badness - new_badness)):
                return 1, new_badness
            else:
                pair[index_to_replace] = experiments["LV"]
                return 0, old_badness
    raise ValueError("targeting labview but looks OK")

#def shuffle_polarimeter(pairs):
#    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))
#    
#    for week_index, week in enumerate(experiments_by_week):
#        counter = Counter(week)
#        num_to_replace = experiments["POL*"].count - counter[experiments["POL*"]]
#        if num_to_replace > 0 and counter[experiments["POL"]] > 0:
#            pair_indices = [i for i, j in enumerate(week)
#                       if j == experiments["POL"]]
#            shuffle(pair_indices)
#            for _ in range(num_to_replace):
#                pairs[pair_indices.pop()][week_index] = experiments["POL*"]


def targetedupdate(pairs, beta):
    duplicate_badness, resource_badness, labview_badness = badness(pairs)
    if duplicate_badness > 0:
        return target_duplicates(pairs, beta)
    elif resource_badness > 0:
        return target_resources(pairs, beta)
    elif labview_badness > 0:
        return target_labview(pairs, beta)
    else:
        raise ValueError("Nothing to do!")


def tableform(pairs):
    for pair_index, pair in enumerate(pairs):
        print("{}\t{}".format(pair_index + 1,
                              "\t".join([ex.acronym for ex in pair])))

def schedule(start):
    pairs = start()
    current_badness = sum(badness(pairs))
    iterations = 0
    beta = 10
    accept = 0
    update = targetedupdate
    
    try:
        while True:
            iterations += 1
            if iterations % 1000 == 0:
                if iterations % 10000 == 0:
                    print('''Slow going, may have insufficient resources, or just an unlucky starting choice.
Current badness: {:.04}, acceptance {}%.
Ctrl+C stops and outputs current progress.'''.format(current_badness, accept / 10))
#                if accept < 750:
#                    update = targetedupdate
#                else:
#                    update = randomupdate
                accept = 0
                beta *= 1.01
                
            step_accept, current_badness = update(pairs, beta)
            current_badness = sum(badness(pairs))
            accept += step_accept
                
            if current_badness == 0:
                break

    except KeyboardInterrupt:
        print("Interrupted, returning current state")
        #tableform(pairs)
        return pairs, False

    iterations = 0
    while (iterations < 10000 or sum(badness(pairs)) > 0) and unpleasantness(pairs) > 0:
        if iterations % 1000 == 0:
            print(".", end="")
        iterations += 1
        beta *= 1.001
        pleasantupdate(pairs, beta)
        current_badness = sum(badness(pairs))
        if current_badness > 0:
            targetedupdate(pairs, beta)

#    shuffle_polarimeter(pairs)
    return pairs, True

if __name__ == "__main__":
    pairs = schedule(cold_start)
    tableform(pairs)
