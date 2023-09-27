import timeit
from logging import DEBUG, INFO, ERROR, WARNING
from typing import Dict, List, Optional, Tuple, Union, Callable, TypedDict

from daisyfl.common import (
    NUM_ROUNDS,
    ZONE_COMM_FREQUENCY,
    CURRENT_ROUND,
    CURRENT_ROUND_MASTER,
    CURRENT_ROUND_ZONE,
    EVALUATE,
    TIMEOUT,
    FIT_SAMPLES,
    EVALUATE_SAMPLES,
    LOSS,
    METRICS,
    decode_ndarrays,
    ndarrays_to_parameters,
    parameters_to_ndarrays,
    Code,
    DisconnectRes,
    EvaluateIns,
    EvaluateRes,
    FitIns,
    FitRes,
    Parameters,
    ReconnectIns,
    Scalar,
    Task,
    Report,
    MODEL_PATH,
    TID,
    SUBTASK,
    EVALUATE_INTERVAL,
    EVALUATE_INIT_MODEL_MASTER,
    REMOVE_OPERATOR,
    OPERATORS,
    MASTER_SERVER_OPERATOR,
    CLIENT_OPERATOR,
    ZONE_SERVER_OPERATOR,
    ZONE_CLIENT_OPERATOR,
    STRATEGIES,
    MASTER_STRATEGY,
    ZONE_STRATEGY,
    PERIOD,
    PERIOD_MASTER,
    PERIOD_ZONE,
    SUBTASK_RETURNS_SELECTED,
    SUBTASK_RETURNS_RESULTS,
    SUBTASK_RETURNS_FAILURES,
    SUBTASK_TIMER,
    TIMER_ROUND,
    INDIVIDUAL_CLIENT_METRICS,
    PARTICIPATION,
    SAVE_MODEL,
    ROAMING_TIMEOUT,
)
from daisyfl.common.logger import log
from daisyfl.common.typing import GetParametersIns
from daisyfl.server.server_operator_manager import ServerOperatorManager
from daisyfl.server.history import History
from daisyfl.common import Type

from daisyfl.client import ZoneClient
import threading
import numpy as np
from dataclasses import dataclass

@dataclass
class MetaTask:
    """local information."""
    tid: str
    parameters: Parameters
    start_time: float
    history: History
    subtask: Task
    subtask_returns: Dict
    individual_metrics: Dict

class TaskManager():
    """Task manager."""

    def __init__(
        self,
        server_operator_manager: ServerOperatorManager,
        manager_type: Type,
    ) -> None:
        self.start_times: List[(int, float)] = []
        self.server_operator_manager: ServerOperatorManager = server_operator_manager
        self.type: Type = manager_type
        if self.type == Type.MASTER:
            operator_key = [MASTER_SERVER_OPERATOR, MASTER_STRATEGY] 
        else:
            operator_key = [ZONE_SERVER_OPERATOR, ZONE_STRATEGY]
        self.server_operator_manager.set_operator_key(operator_key)

        # MetaTask
        self.meta_tasks: List[MetaTask] = []

    def receive_task(
        self, task_config: TypedDict, parameters: Optional[Parameters] = None
    )-> Tuple[Parameters, Report]:
        """Task gateway"""
        # MetaTask
        if parameters is None:
            parameters: Parameters = _initialize_parameters(model_path=task_config[MODEL_PATH])
        start_time = timeit.default_timer()
        meta_task = MetaTask(
            tid=task_config[TID],
            parameters=parameters,
            start_time=start_time,
            history=History(),
            subtask=Task(config={}),
            subtask_returns={},
            individual_metrics={},
        )
        _append_meta_task(task_manager=self, meta_task=meta_task)
        if self.type == Type.MASTER:
            task_config = self.parse_task_spec(task_config=task_config)
        
        # assign task
        parameters, report = self.assign_task(
            task_config=task_config,
            meta_task=meta_task,
        )

        # history & report
        log(INFO, "app_fit: losses_distributed %s", str(meta_task.history.losses_distributed))
        log(INFO, "app_fit: metrics_distributed %s", str(meta_task.history.metrics_distributed))
        log(INFO, "app_fit: losses_centralized %s", str(meta_task.history.losses_centralized))
        log(INFO, "app_fit: metrics_centralized %s", str(meta_task.history.metrics_centralized))
        

        # housekeeping
        if self.type == Type.MASTER and task_config[SAVE_MODEL]:
            np.save(task_config[MODEL_PATH], np.array(parameters_to_ndarrays(parameters), dtype=object))
        end_time = timeit.default_timer()
        elapsed = end_time - meta_task.start_time
        log(INFO, "FL finished in %s", elapsed)
        # NOTE: keep main task in master to export metrics
        if self.type == Type.ZONE:
            self.task_complete(tid=task_config[TID])

        return parameters, report

    def parse_task_spec(
        self,
        task_config: TypedDict,
    ) -> TypedDict:
        if not (task_config.__contains__(NUM_ROUNDS)):
            log(WARNING, "Use default num_rounds")
            task_config[NUM_ROUNDS] = 1
        
        if not (task_config.__contains__(ZONE_COMM_FREQUENCY)):
            log(WARNING, "Use default zone_comm_frequecy")
            task_config[ZONE_COMM_FREQUENCY] = 1    
        
        if not (task_config.__contains__(TIMEOUT)):
            log(WARNING, "Use default timeout")
            task_config[TIMEOUT] = None

        if not (task_config.__contains__(ROAMING_TIMEOUT)):
            log(WARNING, "Use default roaming_timeout")
            task_config[ROAMING_TIMEOUT] = 600

        if not (task_config.__contains__(PERIOD_ZONE)):
            log(WARNING, "Use default period_zone")
            task_config[PERIOD_ZONE] = 10
        
        if not (task_config.__contains__(PERIOD_MASTER)):
            log(WARNING, "Use default period_master")
            task_config[PERIOD_MASTER] = task_config[PERIOD_ZONE] * task_config[ZONE_COMM_FREQUENCY]
        
        if not (task_config.__contains__(CURRENT_ROUND_MASTER)):
            log(WARNING, "Use default current_round_master")
            task_config[CURRENT_ROUND_MASTER] = 0

        if not (task_config.__contains__(CURRENT_ROUND_ZONE)):
            log(WARNING, "Use default current_round_zone")
            task_config[CURRENT_ROUND_ZONE] = 0
            
        task_config[CURRENT_ROUND] = task_config[CURRENT_ROUND_MASTER] * task_config[ZONE_COMM_FREQUENCY] + task_config[CURRENT_ROUND_ZONE]

        if not (task_config.__contains__(EVALUATE_INTERVAL)):
            log(WARNING, "Use default evaluate_interval_master")
            task_config[EVALUATE_INTERVAL] = task_config[NUM_ROUNDS]
        
        if not (task_config.__contains__(EVALUATE_INIT_MODEL_MASTER)):
            log(WARNING, "Use default evaluate_init_model_master")
            task_config[EVALUATE_INIT_MODEL_MASTER] = False

        if not (task_config.__contains__(OPERATORS)):
            log(WARNING, "No operator was specified. Use base operators.")
            task_config[OPERATORS] = {
		        MASTER_SERVER_OPERATOR: ["daisyfl.operator.base.server_logic", "ServerLogic"],
		        CLIENT_OPERATOR: ["daisyfl.operator.base.client_logic", "ClientLogic"],
		        ZONE_SERVER_OPERATOR: ["daisyfl.operator.base.server_logic", "ServerLogic"],
		        ZONE_CLIENT_OPERATOR: ["daisyfl.operator.base.client_logic", "ClientLogic"],
	        }            
        if not (task_config.__contains__(STRATEGIES)):
            log(WARNING, "No strategy was specified. Use FedAvg.")
            task_config[STRATEGIES] = {
		        MASTER_STRATEGY: ["daisyfl.operator.strategy", "FedAvg"],
		        ZONE_STRATEGY: ["daisyfl.operator.strategy", "FedAvg"],
	        }
        
        return task_config
    
    def assign_task(
        self,
        task_config: TypedDict,
        meta_task: MetaTask,
    )-> Tuple[Parameters, Report]:
        if self.type == Type.MASTER:
            # MASTER
            ## Before the first round
            if task_config[EVALUATE_INIT_MODEL_MASTER]:
                task: Task = Task(config={
                    **task_config,
                    **{
                        EVALUATE: True,
                        PERIOD: task_config[PERIOD_MASTER],
                    }
                })
                parameters, report = self.assign_subtask(parameters=meta_task.parameters, task=task, meta_task=meta_task)
            ## Fit and Evaluate
            for i in range(task_config[CURRENT_ROUND_MASTER], task_config[NUM_ROUNDS]):
                task: Task = Task(config={
                    **task_config,
                    **{
                        EVALUATE: False,
                        PERIOD: task_config[PERIOD_MASTER],
                    }
                })
                parameters, report = self.assign_subtask(parameters=meta_task.parameters, task=task, meta_task=meta_task)
                task_config[CURRENT_ROUND_MASTER] = i + 1
                task_config[CURRENT_ROUND_ZONE] = 0
                task_config[CURRENT_ROUND] = task_config[CURRENT_ROUND_MASTER] * task_config[ZONE_COMM_FREQUENCY]
                if ((i + 1) != task_config[NUM_ROUNDS]) and ((i + 1) % task_config[EVALUATE_INTERVAL] == 0):
                    task: Task = Task(config={
                        **task_config,
                        **{
                            EVALUATE: True,
                            PERIOD: task_config[PERIOD_MASTER],
                        }
                    })
                    parameters, report = self.assign_subtask(parameters=meta_task.parameters, task=task, meta_task=meta_task)
            ## After the last round
            task: Task = Task(config={
                **task_config,
                **{
                    EVALUATE: True,
                    PERIOD: task_config[PERIOD_MASTER],
                    REMOVE_OPERATOR: True,
                }
            })
            parameters, report = self.assign_subtask(parameters=meta_task.parameters, task=task, meta_task=meta_task)
            return parameters, report
        else:
            # ZONE
            if task_config[EVALUATE]:
                # Evaluate global model
                task: Task = Task(config={
                    **task_config,
                    **{
                        PERIOD: task_config[PERIOD_ZONE],
                    }
                })
                parameters, report = self.assign_subtask(parameters=meta_task.parameters, task=task, meta_task=meta_task)
            else:
                # Fit zone model
                for i in range(task_config[CURRENT_ROUND_ZONE], task_config[ZONE_COMM_FREQUENCY]):
                    task: Task = Task(config={
                        **task_config,
                        **{
                            EVALUATE: False,
                            PERIOD: task_config[PERIOD_ZONE],
                        }
                    })
                    parameters, report = self.assign_subtask(parameters=meta_task.parameters, task=task, meta_task=meta_task)
                    task_config[CURRENT_ROUND_ZONE] = i + 1
            if (not ("parameters" in locals())) or (not ("report" in locals())):
                log(ERROR, "Zone receive a reduncdant subtask. Please check the task configuration. {}".format(task_config))
                return Parameters(tensors=[], tensor_type=""), Report(config={})
            return parameters, report

    def assign_subtask(
        self,
        parameters: Parameters,
        task: Task,
        meta_task: MetaTask,
    ) -> Tuple[Parameters, Report]:
        meta_task.subtask = task

        if task.config[EVALUATE]:
            # evaluating task
            report: Report = self.server_operator_manager.evaluate_round(parameters, task)
            # update history
            if self.type == Type.MASTER:
                meta_task.history.add_loss_distributed(
                    server_round=report.config[CURRENT_ROUND_MASTER], loss=report.config[LOSS]
                )
                meta_task.history.add_metrics_distributed(
                    server_round=report.config[CURRENT_ROUND_MASTER], metrics=report.config[METRICS]
                )
            else:
                meta_task.history.add_loss_distributed(
                    server_round=report.config[CURRENT_ROUND_ZONE], loss=report.config[LOSS]
                )
                meta_task.history.add_metrics_distributed(
                    server_round=report.config[CURRENT_ROUND_ZONE], metrics=report.config[METRICS]
                )
        else:
            # fitting task
            subtask_start_time = timeit.default_timer()
            parameters, report = self.server_operator_manager.fit_round(parameters, task)
            meta_task.parameters = parameters
            meta_task.subtask_returns[SUBTASK_TIMER] = timeit.default_timer() - subtask_start_time
            meta_task.subtask_returns[TIMER_ROUND] = report.config[CURRENT_ROUND_MASTER] if self.type == Type.MASTER else report.config[CURRENT_ROUND_ZONE]
            
        # update subtask returns
        if report.config[METRICS].__contains__(PARTICIPATION):
            meta_task.subtask_returns[CURRENT_ROUND] = task.config[CURRENT_ROUND]
            meta_task.subtask_returns[PARTICIPATION] = report.config[METRICS][PARTICIPATION]
            if self.type == Type.MASTER:
                del report.config[METRICS][PARTICIPATION]

        # individual client metrics
        if report.config[METRICS].__contains__(INDIVIDUAL_CLIENT_METRICS):
            meta_task.individual_metrics = report.config[METRICS][INDIVIDUAL_CLIENT_METRICS]
            if self.type == Type.MASTER:
                del report.config[METRICS][INDIVIDUAL_CLIENT_METRICS]

        
        return parameters, report

    def get_parameters(self, tid: str) -> Parameters:
        meta_task = _get_meta_task(task_manager=self, tid=tid)
        if meta_task is not None:
            return meta_task.parameters
        log(WARNING, "Can't get parameters from MetaTask")
        return Parameters(tensors=[], tensor_type="")

    def task_complete(self, tid: str) -> bool:
        if not _pop_meta_task(task_manager=self, tid=tid):
            log(WARNING, "Can't delete MetaTask")
            return False
        return True

    # API_Handler
    def get_metrics(self,) -> List[MetaTask]:
        meta_tasks = []
        for mt in self.meta_tasks:
            if len(mt.subtask.config) == 0:
                # unparsed meta_tasks
                continue
            meta_tasks.append(mt)
        return meta_tasks

# initial parameters
def _initialize_parameters(model_path: str) -> Parameters:
    # FL Starting
    log(INFO, "Initializing global parameters")
    return ndarrays_to_parameters(list(np.load(model_path, allow_pickle=True)))

def _get_meta_task(task_manager: TaskManager, tid: str) -> MetaTask:
    for i in range(len(task_manager.meta_tasks)):
        if task_manager.meta_tasks[i].tid == tid:
            return task_manager.meta_tasks[i]
    log(WARNING, "MetaTask not found")
    return None

def _append_meta_task(task_manager: TaskManager, meta_task: MetaTask) -> None:
    if _get_meta_task(task_manager=task_manager, tid=meta_task.tid) is not None:
        log(ERROR, "tid conflicts")
        raise RuntimeError
    task_manager.meta_tasks.append(meta_task)

def _pop_meta_task(task_manager: TaskManager, tid: str) -> bool:
    for i in range(len(task_manager.meta_tasks)):
        if task_manager.meta_tasks[i].tid == tid:
            task_manager.meta_tasks.pop(i)
            return True
    return False
