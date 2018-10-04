#!/usr/bin/env python

from copy import deepcopy
from math import ceil
from collections import Counter
from itertools import zip_longest
from random import randint, choice, random
from math import exp
from lab_defs import Experiment, teaching_length

num_pairs = 40
num_theory = 5
pairs_per_cohort = ceil(num_pairs / 4)

tutorials = {"NA": Experiment(201, "Numerical Analysis", "NA", count=75,
                              writeup=False, fixed=True),
             "LVT": Experiment(298, "LabVIEW Tutorial", "LVT", count=75,
                               writeup=False, fixed=True)}

experiments = {"CDP": Experiment(204, "Chaotic Double Pendulum", "CDP",
                                 writeup=False, undesirable=True),
               "ESR": Experiment(221, "Electron Spin Resonance", "ESR"),
               "BG": Experiment(222,
                                '<font face="AvenirNext">α</font>, '
                                '<font face="AvenirNext">β</font>, and '
                                '<font face="AvenirNext">γ</font>-radiation', 
                                "BG"),
               "FHz": Experiment(223, "Franck Hertz", "FHz"),
               "RS": Experiment(224, "Rutherford Scattering", "RS"),
               "HL": Experiment(238, "Hubble's Law", "HL", writeup=False,
                                undesirable=True),
               "BS": Experiment(241, "Balmer Series of the Hydrogen Atom",
                                "BS"),
               "VIS": Experiment(242, "Measurement of Viscosity", "VIS"),
               "POL": Experiment(244, "Polarimeter", "POL"),
               "MSD": Experiment(246, "Multiple Slit Diffraction", "MSD"),
               "EB": Experiment(247, "Edser Butler Method", "EB"),
               "BH": Experiment(261, "B/H Curve", "BH"),
               "LV": Experiment(299, "LabVIEW: Calibrating a Thermistor", "LV",
                                count=12, writeup=False, undesirable=True)}
experiment_list = list(experiments.values())

reserve_experiments = {"DoS": Experiment(202, "Density of States", "DoS",
                                         writeup=False, undesirable=True),
                       "SE": Experiment(248, "Diffraction at a Straight Edge",
                                        "SE", 4, True, True),
                       "EM": Experiment(204, "e/m", "EM", 2, True, True),
                       "GYR": Experiment(252, "Gyroscope", "GYR", 4, True,
                                         True), 
                       "MSA": Experiment(271, "More Spectroscopic Analysis",
                                         "MSA", 50, False, True),
                       "SA": Experiment(270, "Spectroscopic Analysis", "SA",
                                        writeup=False, undesirable=True)}

GP = ([Experiment("", "Group Project – Week {}".format(i+1), "", count=20,
                  fixed=True) for i in range(4)]
      + [Experiment("", "Group Project – Presentations /100", "", count=40,
                    fixed=True)])

writeup1 = Experiment("", "Report write-up time", "", count=75, fixed=True)
writeup2 = Experiment(" ", "Report write-up time", "", count=75, fixed=True)

null_experiment = Experiment("", "", "", count=1000)
bad_null = Experiment("", "", "—", count=0)

all_experiments = {**experiments, **reserve_experiments, **tutorials}


def cohort(pair_number):
    '''Identify which cohort a pair is in. Must be edited to match this year's
    pair count.'''
    if 0 <= pair_number <= 9:
        return 0
    elif 10 <= pair_number <= 19:
        return 1
    elif 20 <= pair_number <= 29:
        return 2
    elif 30 <= pair_number <= 39:
        return 3
    else:
        raise ValueError("Pair is not in a cohort")


def null_start():
    '''Start with an empty timetable.'''
    pairs = [[tutorials["NA"]] + [bad_null] * 10 for _ in range(num_pairs)]

    for pair_idx, pair in enumerate(pairs):
        if pair_idx not in (list(range(num_theory))):
            pair.extend([tutorials["LVT"]] + [bad_null] * 10)

        gp_semester = cohort(pair_idx) // 2
        semester_cohort = cohort(pair_idx) % 2
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

def cold_start():
    '''Start with a prepopulated timetable based on cycling through a list.
    Unfortunately doesn't tend to give a perfect timetable straight off
    because of group projects skewing things. If it did then the Monte Carlo
    would have been somewhat superfluous'''
    canonical_ordering = ["POL", "EB", "MSD", "RS", "BH", "CDP",
                          "HL", "VIS", "BG", "LV", "BS", "ESR", "FHz"]
    assert len(canonical_ordering) == len(set(canonical_ordering))

    pairs = null_start()
    num_experiments = len(canonical_ordering)

    for pair_index, pair in enumerate(pairs):
        # The pre-this-code timetable made pairs run in quadruplets to
        # simplify scheduling. This initial condition replicates that.
        quad_offset = pair_index // 4
        pair_experiments = (
            canonical_ordering[num_experiments - quad_offset:]
            + canonical_ordering[:num_experiments - quad_offset]
        )
        if cohort(pair_index) <= 1:
            lv_offset = 4
        else:
            lv_offset = 10

        lv_index = pair_experiments.index("LV")
        if lv_index < lv_offset:
            pair_experiments.pop(lv_index)
            if cohort(pair_index) == 0:
                lv_index += 9
            elif cohort(pair_index) == 1:
                lv_index += 4
            elif lv_index < 5:
                lv_index += 9
            else:
                lv_index += 4

            pair_experiments.insert(lv_index, "LV")
        
        for experiment_index, experiment in enumerate(pair):
            if experiment == bad_null:
                pair[experiment_index] = experiments[pair_experiments.pop(0)]
    tableform(pairs)
    return pairs


def badness(pairs):
    '''Badness: The distance we are from a timetable that could in principle
    operate (with no regard to student complaints). I.e. meets the criteria:

     * No pair does any experiment more than once
     * No week has more pairs doing an experiment than there is kit available
     * All students doing PH-211 have LabView scheduled in TB2.
     * No student has LabView scheduled in TB1.

    Three separate distances are returned, for the first, second, and
    (third+fourth) constraints.'''

    duplicate_badness = 0
    resource_badness = 0
    labview_badness = 0

    experiments_by_week = list(zip_longest(*pairs, fillvalue=null_experiment))

    for pair_index, pair in enumerate(pairs):
        duplicate_badness += 5 * (1 - len(set(pair)) / len(pair))
        if len(pair) > teaching_length and experiments["LV"] not in pair:
            labview_badness += 1
        elif (experiments["LV"] in pair
              and pair.index(experiments["LV"]) < teaching_length):
            labview_badness += 3
# Previously there was an option to have two slightly different
# versions of the Polarimeter experiment. Yes, this was hard-coded. Sorry.
#        if experiments["POL"] in pair and experiments["POL*"] in pair:
#            duplicate_badness += 1

    for week in experiments_by_week:
        counter = Counter(week)
        for required_count, experiment in zip(counter.values(),
                                              counter.keys()):
            if required_count > experiment.count:
                resource_badness += 1

    return duplicate_badness, resource_badness, labview_badness


def unpleasantness(pairs):
    '''Unpleasantness: The degree to which a timetable will inflict pain on
    students. The main pain point is not having enough experiments to write up
    in the semester with group projects. Only 4 experiment slots are available,
    and in PH-211 one of those is LabView which can't be written up. As such
    we try to make the scheduler avoid putting CDP or HL in the same block.

    There is also an IOP constraint that every student must do Edser Butler.
    This was added at the last minute so has been hacked into this function.
    In principle it should be added to badness, but that would require
    defining a new class of badness and a targeted update for it.
    Would benefit from refactoring.'''
    undesirable_count = sum(1
                            for pair in pairs
                            for experiment in pair 
                            if experiment.undesirable)

    very_undesirable_count = 0
    for pair_index, pair in enumerate(pairs):
        local_count = max(sum(1 for experiment in pair[1:11]
                              if experiment.undesirable
                              or experiment.writeup == False
                              or "Group Project" in experiment.title
                              or experiment.title == "LabVIEW") - 5,
                          0)
        if local_count > 0:
            very_undesirable_count += local_count ** 3

        if len(pair) > 11:
            local_count = max(sum(1 for experiment in pair[12:]
                                  if experiment.undesirable
                                  or experiment.writeup == False
                                  or "Group Project" in experiment.title
                                  or experiment.title == "LabVIEW") - 5,
                              0)
            if local_count > 0:
                very_undesirable_count += local_count ** 3

        # IOP constraint
        if experiments["EB"] not in pair:
            very_undesirable_count += 1000

    return undesirable_count + very_undesirable_count


def unpleasant_badness(pairs):
    # Add a weighting to the unpleasantness relative to badness for the update
    return sum(badness(pairs)) + 0.2 * unpleasantness(pairs)


def randomupdate(pairs, beta):
    '''Try placing a random experiment into a random slot, with constraints.
    Do a Metropolis-style accept/reject test.'''
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
    '''Target unpleasant experiments, replace them with pleasant ones.
    This would be better if it tried swapping them for pleasant ones in the
    opposing semester.'''
    unpleasant_experiments = [(pair_index, experiment_index)
                              for pair_index, pair in enumerate(pairs)
                              for experiment_index, experiment
                              in enumerate(pair)
                              if experiment.undesirable]

    if unpleasant_experiments == []:
        tableform(pairs)
        raise ValueError("No unpleasant experiments??")

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
    '''Try to fix pairs doing the same experiment twice.'''

    for pair_index, pair in enumerate(pairs):
        if len(set(pair)) < len(pair):
            old_badness = unpleasant_badness(pairs)
            counter = Counter(pair)
            experiment_to_replace, n = counter.most_common(1)[0]
            index_to_replace = randint(0, n)
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

# With two different polarimeter scripts/types, it would have been
# necessary to handle this by hand.
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
    '''Try and fix not having enough copies of an experiment to run in a
    given week.'''

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
    '''Try and fix problems with LabView'''

    dbg_indices = []
    for pair_index, pair in enumerate(pairs):
        if pair_index >= num_theory and experiments["LV"] not in pair:
            old_badness = unpleasant_badness(pairs)
            while True:
                index_to_replace = randint(teaching_length + 1,
                                           teaching_length * 2 - 1)
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
        if len(indices) == 0:
            continue
        if len(indices) > 1 or indices[0] < teaching_length:
            old_badness = unpleasant_badness(pairs)
            index_to_replace = choice(indices)
            pair[index_to_replace] = choice(experiment_list)
            new_badness = unpleasant_badness(pairs)

            if new_badness <= old_badness:
                return 1, new_badness
            elif random() < exp(beta * (old_badness - new_badness)):
                return 1, new_badness
            else:
                pair[index_to_replace] = experiments["LV"]
                return 0, old_badness
        dbg_indices.append(indices)
    tableform(pairs)
    print(dbg_indices)
    raise ValueError("targeting labview but looks OK")

# def shuffle_polarimeter(pairs):
#     experiments_by_week = list(zip_longest(*pairs,
#                                            fillvalue=null_experiment))
#
#     for week_index, week in enumerate(experiments_by_week):
#         counter = Counter(week)
#         num_to_replace = (experiments["POL*"].count -
#                           counter[experiments["POL*"]])
#         if num_to_replace > 0 and counter[experiments["POL"]] > 0:
#             pair_indices = [i for i, j in enumerate(week)
#                        if j == experiments["POL"]]
#             shuffle(pair_indices)
#             for _ in range(num_to_replace):
#                 pairs[pair_indices.pop()][week_index] = experiments["POL*"]


def targetedupdate(pairs, beta):
    '''Work out where the badness problem is, and run the appropriate
    targeted update.'''
    duplicate_badness, resource_badness, labview_badness = badness(pairs)
    if duplicate_badness > 0:
        return target_duplicates(pairs, beta)
    elif resource_badness > 0:
        return target_resources(pairs, beta)
    elif labview_badness > 0:
        try:
            return target_labview(pairs, beta)
        except ValueError as ex:
            print(duplicate_badness, resource_badness, labview_badness)
            raise ex
    else:
        raise ValueError("Nothing to do!")


def tableform(pairs):
    '''Format a list of pairs (in turn a list of experiments) into a neat
    table that just fits in a wide terminal window.'''

    for pair_index, pair in enumerate(pairs):
        print("{}\t{}".format(pair_index + 1,
                              "\t".join([ex.acronym for ex in pair])))


def schedule(start):
    '''Try to organise a schedule for a given starting condition.

    Uses a simulated annealing-style process to allow large changes
    initially so as not to get stuck in a metastability but gradually try 
    to head towards a minimum.'''

    pairs = start()
    current_badness = sum(badness(pairs))
    iterations = 0
    beta = 1
    accept = 0
    update = targetedupdate

    try:
        while True:
            iterations += 1
            if iterations % 1000 == 0:
                if iterations % 10000 == 0:
                    print('Slow going, may have insufficient resources, or '
                          'just an unlucky starting choice.\n'
                          'Current badness: {:.04}, acceptance {}%.\n'
                          'Ctrl+C stops and outputs current progress.'.format(
                              current_badness, accept / 10
                          ))
#                if accept < 750:
#                    update = targetedupdate
#                else:
#                    update = randomupdate
                accept = 0
                beta *= 1.05

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
    acc = 0
    terminating = False
    min_unpleasantness = unpleasantness(pairs)
    minimally_unpleasant_state = deepcopy(pairs)
    while ((iterations < 1000000 and
            unpleasantness(pairs) > 0 and
            not terminating)
           or sum(badness(pairs)) > 0):
        try:
            if iterations % 1000 == 0:
                print(
                    "Unpleasantness: {}\tCurrent acceptance: {}\t"
                    "Lowest unpleasantness seen: {}\tCurrent beta: {}".format(
                        unpleasantness(pairs), acc/1000,
                        min_unpleasantness, beta
                    )
                )
                acc = 0
            iterations += 1
            beta *= 1.0001
            if sum(badness(pairs)) > 0:
                acc += targetedupdate(pairs, beta)[0]
            else:
                acc += pleasantupdate(pairs, beta)[0]
            current_unpleasantness = unpleasantness(pairs)
            if current_unpleasantness < min_unpleasantness:
                min_unpleasantness = current_unpleasantness
                minimally_unpleasant_state = deepcopy(pairs)

        except KeyboardInterrupt as ki:
            if terminating:
                tableform(pairs)
                raise ki
            else:
                terminating = True
                print("OK, will get badness to zero and give a result")

#    shuffle_polarimeter(pairs)
    print(badness(pairs))
    print(unpleasantness(pairs))
    return minimally_unpleasant_state, True


if __name__ == "__main__":
    # Just a way to test by eye that the initial condition generator works
    pairs = schedule(null_start)
    tableform(pairs)
