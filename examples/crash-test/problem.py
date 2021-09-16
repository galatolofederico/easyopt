import argparse
import random
import easyopt

parser = argparse.ArgumentParser()

parser.add_argument("--x", type=float, required=True)
parser.add_argument("--y", type=float, required=True)

args = parser.parse_args()

def objective(x, y):
    if random.random() <= 0.5:
        raise Exception("Crash")
    return x**2 + y**2

F = objective(args.x ,args.y)
easyopt.objective(F)