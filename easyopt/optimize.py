import os
import json
import inspect
import uuid
import socket
import subprocess
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

def build_parameters_strings(parameters):
    args = " ".join([f"--{k}={v}" for k, v in parameters.items()])

    return dict(
        args = args
    )

def optimize(study):
    def objective(trial):
        config = study.user_attrs["config"]
        parameters = sample_parameters(trial, config)
        command_variables = build_parameters_strings(parameters)
        
        command = config["command"].format(**command_variables)
        socket_file = f"/tmp/{uuid.uuid4()}"
        
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(socket_file)

        env = os.environ.copy()
        env["EASYOPT_SOCKET"] = socket_file

        process = subprocess.Popen(command.split(" "), env=env)
        
        global_step = 1
        while True:
            server.listen(1)
            conn, addr = server.accept()
            datagram = conn.recv(10*1024)
            data = json.loads(datagram)
            
            if data["command"] == "objective":
                return data["value"]
            if data["command"] == "report":
                trial.report(data["value"], step=global_step)
                global_step += 1
            

    study.optimize(objective, n_trials=1)