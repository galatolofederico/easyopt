# easyopt

`easyopt` is a **super simple** yet **super powerful** [optuna](https://optuna.org/)-based Hyperparameters Optimization Framework that requires **no coding**.

## Features

* YAML Configuration
* Distributed Parallel Optimization
* Experiments Monitoring and Crash Recovering
* Experiments Replicas
* Real Time Pruning
* A wide variety of sampling strategies
    * Tree-structured Parzen Estimator 
    * CMA-ES
    * Grid Search
    * Random Search
* A wide variety of pruning strategies
    * Asynchronous Successive Halving Pruning
    * Hyperband Pruning
    * Median Pruning
    * Threshold Pruning
* A wide variety of DBMSs
    * Redis
    * SQLite
    * PostgreSQL
    * MySQL
    * Oracle
    * And many [more](https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine)
  

## Installation

To install `easyopt` just type:

```
pip install easyopt
```

## Example

`easyopt` expects that hyperparameters are passed using the command line arguments. 

For example this problem has two hyperparameters `x` and `y`

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--x", type=float, required=True)
parser.add_argument("--y", type=float, required=True)

args = parser.parse_args()

def objective(x, y):
    return x**2 + y**2

F = objective(args.x ,args.y)
```

To integrate `easyopt` you just have to
* `import easyopt`
* Add `easyopt.objective(...)` to report the experiment objective function value

The above code becomes:

```python
import argparse
import easyopt

parser = argparse.ArgumentParser()

parser.add_argument("--x", type=float, required=True)
parser.add_argument("--y", type=float, required=True)

args = parser.parse_args()

def objective(x, y):
    return x**2 + y**2

F = objective(args.x ,args.y)
easyopt.objective(F)
```

Next you have to create the `easyopt.yml` to define the problem search space, sampler, pruner, storage, etc.

```yaml
command: python problem.py {args}
storage: sqlite:////tmp/easyopt-toy-problem.db
sampler: TPESampler
parameters:
  x:
    distribution: uniform
    low: -10
    high: 10
  y:
    distribution: uniform
    low: -10
    high: 10
```

You can find the compete list of distributions [here](https://optuna.readthedocs.io/en/v1.4.0/reference/trial.html) (all the `suggest_*` functions)

Finally you have to create a study

```
easyopt create test-study
```

And run as many agents as you want

```
easyopt agent test-study
```

After a while the hyperparameter optimization will finish

```
Trial 0 finished with value: 90.0401543850028 and parameters: {'x': 5.552902529323713, 'y': 7.694506344453366}. Best is trial 0 with value: 90.0401543850028.
Trial 1 finished with value: 53.38635524683359 and parameters: {'x': 0.26609756303111, 'y': 7.301749607716118}. Best is trial 1 with value: 53.38635524683359.
Trial 2 finished with value: 64.41207387363161 and parameters: {'x': 7.706366704967074, 'y': 2.2414250115064167}. Best is trial 1 with value: 53.38635524683359.
...
...
Trial 53 finished with value: 0.5326245807950265 and parameters: {'x': -0.26584110075742917, 'y': 0.6796713102251005}. Best is trial 35 with value: 0.11134607529340049.
Trial 54 finished with value: 8.570230212116037 and parameters: {'x': 2.8425893061307295, 'y': 0.6999401751487438}. Best is trial 35 with value: 0.11134607529340049.
Trial 55 finished with value: 96.69479467451664 and parameters: {'x': -0.3606041968175481, 'y': -9.826736960342137}. Best is trial 35 with value: 0.11134607529340049.
```

## YAML Structure

The `YAML` configuration file is structured as follows

```yaml
command: <command>
storage: <storage>
sampler: <sampler>
pruner: <pruner>
direction: <direction>
replicas: <replicas>
parameters:
  parameter-1:
    distribution: <distribution>
    <arg1>: <value1>
    <arg2>: <value2>
    ...
  ...
```

* `command`: the command to execute to run the experiment.
  * `{args}` will be expanded to `--parameter-1=value-1 --parameter-2=value-2`
* `storage`: the storage to use for the study. A full list of storages is available [here](https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine)
* `sampler`: the sampler to use. The full list of samplers is available [here](https://optuna.readthedocs.io/en/stable/reference/samplers.html)
* `pruner`: the pruner to use. The full list of pruners is available [here](https://optuna.readthedocs.io/en/stable/reference/pruners.html)
* `direction`: can be `minimize` or `maximize` (default: `minimize`)
* `replicas`: the number of replicas to run for the same experiment (the experiment result is the average). (default: `1`)
* `parameters`: the parameters to optimize
  * for each parameter have to specify
    * `distribution` the distribution to use. The full list of distributions is available [here](https://optuna.readthedocs.io/en/v1.4.0/reference/trial.html) (all the `suggest_*` functions)
    * `arg`: `value`
      * Arguments of the distribution. The arguments documentation is available [here](https://optuna.readthedocs.io/en/v1.4.0/reference/trial.html)

## CLI Interface

`easyopt` offer two CLI commands:

* `create` to create a study using the `easyopt.yml` file or the one specified with `--config`
* `agent <study_name>` to run the agent for `<study_name>`

## LIB Interface

When importing `easyopt` you can use three functions:

* `easyopt.objective(value)` to report the **final** objective function value of the experiment
* `easyopt.report(value)` to report the **current**  objective function value of the experiment (used by the pruner)
* `easyopt.should_prune()` it returns `True` if the pruner thinks that the run should be pruned

## Examples

You can find some examples [here](https://github.com/galatolofederico/easyopt/tree/main/examples)

## Contributions and license

The code is released as Free Software under the [GNU/GPLv3](https://choosealicense.com/licenses/gpl-3.0/) license. Copying, adapting and republishing it is not only allowed but also encouraged. 

For any further question feel free to reach me at  [federico.galatolo@ing.unipi.it](mailto:federico.galatolo@ing.unipi.it) or on Telegram  [@galatolo](https://t.me/galatolo)