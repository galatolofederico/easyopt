import argparse
import os
import uuid
import sys
import inspect

import yaml
import optuna
import colorama

from easyopt.optimize import optimize

def print_color(str, color):
    print(getattr(colorama.Fore, color)+str+colorama.Style.RESET_ALL)

def die(str):
    print_color(str, "RED")
    sys.exit(1)

def agent(args):
    storage = None
    if args.storage != "":
        storage = args.storage
    else:
        if not os.path.exists(args.config):
            die(f"Config file {args.config} do not exists. Create a config file or specify a storage using --storage")
        else:
            config = yaml.load(open(args.config, "r"), Loader=yaml.CLoader)
            if "storage" not in config and args.storage == "":
                die("You have to specify a 'storage' using the config file or using --storage. You can use any SQLAlchemy storage: https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine")
            else:
                storage = config["storage"]
    
    assert storage is not None
    
    study = optuna.load_study(study_name=args.name, storage=storage)
    while True:
        optimize(study)

def create(args):
    if not os.path.exists(args.config):
        die(f"Config file {args.config} do not exists. Create a easyopt.yml file or specify a config file using --config")

    config = yaml.load(open(args.config, "r"), Loader=yaml.CLoader)

    if "storage" not in config and args.storage == "":
        die("You have to specify a 'storage' using the config file or using --storage. You can use any SQLAlchemy storage: https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine")
    if args.storage != "" and "storage" in config:
        print_color("Overriding storage using CLI argument", "YELLOW")
        config["storage"] = args.storage

    if "direction" not in config:
        print_color("Optimization direction ('direction') not specified, assuming 'minimize'", "YELLOW")
        config["direction"] = "minimize"

    if "replicas" not in config:
        print_color("Number of replicas ('replicas') not specified, assuming 1", "YELLOW")
        config["replicas"] = "1"

    sampler = None
    if "sampler" in config:
        if config["sampler"] not in dir(optuna.samplers):
            die(f"Invalid sampler {config['sampler']}. Available optuna samplers here: https://optuna.readthedocs.io/en/stable/reference/samplers.html")
        else:
            sampler = getattr(optuna.samplers, config["sampler"])()
        
    pruner = None
    if "pruner" in config:
        if config["pruner"] not in dir(optuna.pruners):
            die(f"Invalid pruner {config['pruner']}. Available optuna pruners here: https://optuna.readthedocs.io/en/stable/reference/pruners.html")
        else:
            pruner = getattr(optuna.pruners, config["pruner"])()
    
    if "parameters" not in config:
        die("You have to specify parameters to optimze in the config file")
    else:
        for parameter, parameters_args in config["parameters"].items():
            if "distribution" not in parameters_args:
                die("Every parameter must have a 'distribution'")
            parameters_args_copy = parameters_args.copy()
            distribution = parameters_args_copy.pop("distribution")
            optuna_func = "suggest_"+distribution
            if optuna_func not in dir(optuna.Trial):
                die(f"Unknown distribution {distribution}. Available distribution are the suggest_ functions here: https://optuna.readthedocs.io/en/stable/reference/generated/optuna.trial.Trial.html#optuna.trial.Trial")
            optuna_func_args = inspect.getfullargspec(getattr(optuna.Trial, optuna_func)).args
            
            for parameters_arg in parameters_args_copy:
                if parameters_arg not in optuna_func_args:
                    die(f"Unknown argument {parameters_arg} for function {optuna_func}. Check documentation here: https://optuna.readthedocs.io/en/stable/reference/generated/optuna.trial.Trial.html#optuna.trial.Trial")


    study = optuna.create_study(
        study_name=args.name,
        direction=config["direction"],
        sampler=sampler,
        pruner=pruner,
        storage=config["storage"]
    )

    study.set_user_attr("config", config)

    print_color(f"Optuna study created with name {args.name}", "GREEN")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("command", metavar="command", type=str, choices=["create", "agent"], help="Command to execute")
    parser.add_argument("name", type=str, nargs="?", help="Study name")

    parser.add_argument("--config", type=str, default="./easyopt.yml")
    parser.add_argument("--storage", type=str, default="")

    args = parser.parse_args()

    colorama.init()

    if args.command == "create" and args.name is None:
        args.name = str(uuid.uuid4())
    if args.command == "agent" and args.name is None:
        die("You must specify a study name to run the agent: easyopt agent <study_name>")

    if args.command == "create":
        create(args)
    elif args.command == "agent":
        agent(args)
