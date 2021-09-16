import os
import json
import inspect
import uuid
import socket
import subprocess
import threading
import queue
import optuna

from easyopt.utils import log
from easyopt.src.heartbeat import HeartbeatMonitor, HeartbeatException
from easyopt.src.socketserver import SocketServer

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
        log(f"[optimize] socket file {socket_file}")
        
        q = queue.Queue()
        server = SocketServer(q, socket_file)
        heartbeat_monitor = HeartbeatMonitor(q)

        server.listen()

        env = os.environ.copy()
        env["EASYOPT_SOCKET"] = socket_file

        process = subprocess.Popen(command.split(" "), env=env)
        log(f"[optimize] running process {command}")
        global_step = 1
        results = []
        while True:
            data = q.get()
            log(f"[optimize] received {data}")
            if data["command"] == "objective":
                results.append(data["value"])
                log(f"[optimize] result {data['value']} added, len(results)={len(results)}")
                process.wait()
                log(f"[optimize] process terminated")
                if len(results) >= config["replicas"]:
                    server.stop()
                    os.remove(socket_file)
                    log(f"[optimize] finished runs")
                    return sum(results)/len(results)
                else:
                    log(f"[optimize] running process {command}")
                    process = subprocess.Popen(command.split(" "), env=env)
            
            elif data["command"] == "report":
                trial.report(data["value"], step=global_step)
                global_step += 1
            
            elif data["command"] == "should_prune":
                reply = int(trial.should_prune())
                server.send(dict(reply=reply))
            
            elif data["command"] == "heartbeat":
                heartbeat_monitor.beat()
            
            elif data["command"] == "heartbeat_fail":
                raise HeartbeatException

                

    study.optimize(objective, n_trials=1)