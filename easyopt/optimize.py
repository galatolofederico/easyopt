import os
import json
import inspect
import uuid
import socket
import subprocess
import optuna

from easyopt.utils import recv_object, send_object

def sample_parameters(trial, config):
    parameters = dict()
    for parameter, parameter_args in config["parameters"].items():
        distribution = parameter_args.pop("distribution")
        optuna_func = "suggest_"+distribution
        
        args = dict()
        for parameter_name, parameter_value in parameter_args.items():
            if isinstance(parameter_value, str): parameter_value = float(parameter_value)
            args[parameter_name] = parameter_value
        
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
        results = []
        server.listen(1)
        conn, addr = server.accept()
        while True:
            data = recv_object(conn)
            if data["command"] == "objective":
                results.append(data["value"])
                process.wait()
                if len(results) >= config["replicas"]:
                    conn.close()
                    os.remove(socket_file)
                    return sum(results)/len(results)
                else:
                    process = subprocess.Popen(command.split(" "), env=env)
                    conn, addr = server.accept()
            if data["command"] == "report":
                trial.report(data["value"], step=global_step)
                global_step += 1
            if data["command"] == "should_prune":
                reply = int(trial.should_prune())
                send_object(dict(reply=reply), conn)

    study.optimize(objective, n_trials=1)