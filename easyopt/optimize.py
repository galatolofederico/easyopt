import inspect

import optuna

def sample_parameters(trial, config):
    parameters = dict()
    for parameter, parameter_args in config["parameters"].items():
        distribution = parameter_args.pop("distribution")
        optuna_func = "suggest_"+distribution
        optuna_func_types = inspect.getfullargspec(getattr(optuna.Trial, optuna_func)).annotations
        
        args = dict()
        for parameter_name, parameter_value in parameter_args.items():
            args[parameter_name] = optuna_func_types[parameter_name](parameter_value)
        
        parameters[parameter] = getattr(trial, optuna_func)(parameter, **args)
        
    return parameters
    

def optimize(study):
    def objective(trial):
        parameters = sample_parameters(trial, study.user_attrs["config"])
        print(parameters)

    study.optimize(objective, n_trials=1)