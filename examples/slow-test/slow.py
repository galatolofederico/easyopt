import argparse
import easyopt
import time
import random

parser = argparse.ArgumentParser()

parser.add_argument("--x", type=float, required=True)
parser.add_argument("--y", type=float, required=True)

args = parser.parse_args()

def objective(x, y):
    return x**2 + y**2

F = objective(args.x ,args.y)

time.sleep(random.randint(10, 15))

easyopt.objective(F)