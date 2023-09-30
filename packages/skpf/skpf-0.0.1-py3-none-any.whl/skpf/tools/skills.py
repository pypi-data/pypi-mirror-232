from promptflow import tool
from promptflow.connections import AzureOpenAIConnection


@tool
def planner(connection: AzureOpenAIConnection, **params) -> list:
    return [{ "item": True }]
