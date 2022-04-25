"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
from pathlib import Path
import sys
from typing import Callable, Dict

from instance import Instance
from solution import Solution

# import point
from point import Point

from file_wrappers import StdinFileWrapper, StdoutFileWrapper


def solve_naive(instance: Instance) -> Solution:
    return Solution(
        instance=instance,
        towers=instance.cities,
    )

# Description
# 1. Loop through all possible tower positions. Find the tower that covers as many cities as possible.
# 2. Add tower to towerslist and remove the cities it covered.
    # Optimziation: remove that tower position from possible tower positions since we won't place two towers in the same place
# 3. Repeat until all cities are covered.
def solve_set_cover(instance: Instance) -> Solution:
    gsl = instance.grid_side_length
    cr = instance.coverage_radius
    pr = instance.penalty_radius
    citiesList = instance.cities
    towersList = []

    possibleTowerPositions = []
    # original
    # for x in range(0, gsl):
    #     for y in range(0, gsl):
    #         possibleTowerPositions.append(Point(x,y))

    # spiral
    layers = pr
    currLayer = 0
    while currLayer != layers:
        for x in range(currLayer, gsl - currLayer - 1):
            possibleTowerPositions.append(Point(x, currLayer))
        for y in range(currLayer, gsl - currLayer - 1):
            possibleTowerPositions.append(Point(gsl - currLayer - 1, y))
        for x in range(gsl - currLayer - 1, currLayer, -1):
            possibleTowerPositions.append(Point(x, gsl - currLayer - 1))
        for y in range(gsl - currLayer - 1, currLayer, - 1):
            possibleTowerPositions.append(Point(currLayer, y))
        currLayer += 1

    for x in range(layers, gsl - layers):
        for y in range(layers, gsl - layers):
            possibleTowerPositions.append(Point(x,y))

    def numCitiesCovered(point):
        count = 0
        for city in citiesList:
            if Point.distance_obj(tower, city) <= cr: # point.py for examples
                count += 1
        return count

    def getCitiesCovered(point):
        cList = []
        for city in citiesList:
            if Point.distance_obj(tower, city) <= cr:
                cList.append(city)
        return cList

    while len(citiesList) > 0:
        max_coverage = 0
        max_tower = Point(0, 0)
        coveredByMax = []
        for tower in possibleTowerPositions:
            coverageCount = numCitiesCovered(tower)
            coveredList = getCitiesCovered(tower) # list of cities that the tower covers
            if coverageCount > max_coverage:
                max_tower = tower
                max_coverage = coverageCount
                coveredByMax = coveredList

        towersList.append(max_tower)
        citiesList = list(set(citiesList) - set(coveredByMax))

    return Solution(
        instance = instance,
        towers = towersList
    )

# https://stackoverflow.com/questions/127704/algorithm-to-return-all-combinations-of-k-elements-from-n
# Was gonna use this to brute force but it'd probably take waayyy to long
def combinations(list, length, startPosition, result, combinationList):
    if length == 0:
        combinationList.append(result)
        return
    for i in range(startPosition, (len(list) - length) + 1 ):
        result[len(result) - length] = list[i]
        combinations(list, length - 1, i + 1, result, combinationList)


def solve_dp(instance: Instance) -> Solution:
    return Solution(
        instance = instance,
        towers = towersList
    )

SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive,
    "sc" : solve_set_cover,
    "dp" : solve_dp,

}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")

def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")

def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str,
                        help="The output file. Use - for stdout.",
                        default="-")
    main(parser.parse_args())
