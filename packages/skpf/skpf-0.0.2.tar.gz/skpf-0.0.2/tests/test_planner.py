import os
from pathlib import Path
from skpf.tools.planners import sequential, action, stepwise
from promptflow.connections import AzureOpenAIConnection
from dotenv import load_dotenv
load_dotenv()

API_BASE = os.getenv("API_BASE")
API_KEY = os.getenv("API_KEY")
BASE_PATH = os.path.dirname(os.path.realpath(__file__))


def test_sequential():
    connection = AzureOpenAIConnection(api_key=API_KEY, api_base=API_BASE)
    deployment_name = "gpt-35-turbo"

    code =  (Path(BASE_PATH) / Path("./mathskills.py")).absolute()
    result = sequential(connection, deployment_name, str(code), 
                     "Solve this math problem: what is three plus five divided by eight?")
    assert float(result["answer"]) == 8.0


def test_action():
    connection = AzureOpenAIConnection(api_key=API_KEY, api_base=API_BASE)
    deployment_name = "gpt-35-turbo"

    code =  (Path(BASE_PATH) / Path("./mathskills.py")).absolute()
    result = action(connection, deployment_name, str(code), 
                     "Solve this math problem: what is three plus five divided by eight?")


def test_stepwise():
    connection = AzureOpenAIConnection(api_key=API_KEY, api_base=API_BASE)
    deployment_name = "gpt-35-turbo"

    code =  (Path(BASE_PATH) / Path("./mathskills.py")).absolute()
    result = stepwise(connection, deployment_name, str(code), 
                     "Solve this math problem: what is three plus five?")
    assert "8" in result["answer"]
