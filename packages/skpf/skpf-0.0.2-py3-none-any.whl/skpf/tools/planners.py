import os
import sys
import inspect
import asyncio
import logging
from pathlib import Path
from promptflow import tool
from types import ModuleType

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planning.sequential_planner import SequentialPlanner
from semantic_kernel.planning.stepwise_planner import StepwisePlanner
from semantic_kernel.planning.action_planner.action_planner import ActionPlanner
from promptflow.connections import AzureOpenAIConnection
from promptflow._core.tool_meta_generator import load_python_module_from_file
from promptflow.contracts.types import FilePath


def get_logger(name: str) -> logging.Logger:
    logger = logging.Logger(name)
    format = logging.Formatter()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(format)
    logger.addHandler(stdout_handler)
    return logger


def load_classes(code_path: Path):
    module: ModuleType = load_python_module_from_file(code_path)
    target_classes = [m for m in dir(module) 
                      if inspect.isclass(getattr(module, m)) and 
                      inspect.getmodule(getattr(module, m)) == None]
    
    # TODO: assumption of parameterless constructors here....
    # perhaps should use **params as constructor params?
    return [getattr(module, o)() for o in target_classes]


def get_kernel(connection: AzureOpenAIConnection, deployment_name: str, file_path: FilePath):
    code_path = Path(file_path)
    if not code_path.is_absolute():
        code_path = Path(os.getcwd()) / code_path

    if not code_path.exists():
        raise Exception(f"Code file {file_path} does not exist.")
    
    target_classes = load_classes(code_path)
    if len(target_classes) == 0:
        raise Exception(f"No classes found in {code_path}")
    
    # create kernel
    kernel = sk.Kernel(log=get_logger("SEMANTIC_KERNEL"))
    kernel.add_chat_service(
            "chat_completion",
            AzureChatCompletion(
                deployment_name,
                connection.api_base,
                connection.api_key,
            ),
        )
    
    # import function skill definitions
    for c in target_classes:
        kernel.import_skill(c)

    return kernel


@tool
def stepwise(connection: AzureOpenAIConnection, deployment_name: str, file_path: FilePath, intent: str, **params) -> list:
    # get kernel
    kernel = get_kernel(connection, deployment_name, file_path)

    # create planner
    planner = StepwisePlanner(kernel=kernel)

     # create plan
    plan = planner.create_plan(intent)

    # execute plan
    answer = asyncio.run(kernel.run_async(plan)).result

    steps = [{"function": step.name,
              "description": step.description,
              "input": step.parameters.variables,
              "output": step._outputs} for _, step in 
              enumerate(plan._steps)]
    
    return {
        "answer": answer,
        "steps": steps
    }


@tool
def sequential(connection: AzureOpenAIConnection, deployment_name: str, file_path: FilePath, intent: str, **params) -> list:
    # get kernel
    kernel = get_kernel(connection, deployment_name, file_path)

    # create planner
    planner = SequentialPlanner(kernel=kernel)

     # create plan
    plan = asyncio.run(planner.create_plan_async(intent))

    # execute plan
    answer = asyncio.run(kernel.run_async(plan)).result

    steps = [{"function": step.name,
              "description": step.description,
              "input": step.parameters.variables,
              "output": step._outputs} for _, step in 
              enumerate(plan._steps)]
    
    return {
        "answer": answer,
        "steps": steps
    }


@tool
def action(connection: AzureOpenAIConnection, deployment_name: str, file_path: FilePath, intent: str, **params) -> list:
    # get kernel
    kernel = get_kernel(connection, deployment_name, file_path)

    # create planner
    planner = ActionPlanner(kernel=kernel, logger=get_logger("SEMANTIC_KERNEL"))

     # create plan
    plan = asyncio.run(planner.create_plan_async(intent))

    # execute plan
    answer = asyncio.run(kernel.run_async(plan)).result

    return {
        "answer": answer,
        "steps": plan.state
    }
