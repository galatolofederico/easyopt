import argparse
import os
import uuid
import sys

import yaml
import optuna
import colorama

def print_color(str, color):
    print(getattr(colorama.Fore, color)+str+colorama.Style.RESET_ALL)

def die(str):
    print_color(str, "RED")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("command", metavar="command", type=str, choices=["create", "agent"], help="Command to execute")
    parser.add_argument("name", type=str, nargs="?", help="Study name ")
    parser.add_argument("--config", type=str, default="./easyopt.yml")

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

def create(args):
    if not os.path.exists(args.config):
        die(f"Config file {args.config} do not exists. Create a easyopt.yml file or specify a config file using --config")

    config = yaml.load(open(args.config, "r"), Loader=yaml.CLoader)
    
    if "storage" not in config:
        die("You have to specify a 'storage'. You can use any SQLAlchemy storage: https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine")

    if "direction" not in config:
        print_color("Optimization direction not specified, assuming 'minimize'", "YELLOW")
        config["direction"] = "minimize"

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
    

    study = optuna.create_study(
        study_name=args.name,
        direction=config["direction"],
        sampler=sampler,
        pruner=pruner,
        storage=config["storage"]
    )

    study.set_user_attr("config", config)

    print_color(f"Optuna study created with name {args.name}", "GREEN")
