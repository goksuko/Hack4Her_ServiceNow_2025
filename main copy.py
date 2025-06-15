import json

import os
from dotenv import load_dotenv

from tapeagents.llms import OpenrouterLLM
from tapeagents.agent import Agent
from tapeagents.nodes import StandardNode, Stop

from tapeagents.environment import ToolCollectionEnvironment
from tapeagents.dialog_tape import DialogTape, UserStep
from tapeagents.orchestrator import main_loop

from our_data import data_cleaned
from our_data import Application
from our_data import tabulate_result

import re
import tabulate


load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

llm = OpenrouterLLM(
    model_name="meta-llama/llama-3.3-70b-instruct:free",  # https://openrouter.ai/meta-llama/llama-3.3-70b-instruct:free
    api_token=api_key,
    parameters={"temperature": 0.1},
)   

# no tools for now
environment = ToolCollectionEnvironment(tools=[])
environment.initialize()

def applicant_check(applicant):
    
    print("Please insert the file path to your JSON file.")
    input_path = input()

    with open(input_path, 'r') as file:
         data = json.load(file)

    with open('instructions/regulations.md', 'r') as regulations:
         eligibility_criteria = regulations.read()
         
    with open('instructions/regulation-analysis.md', 'r') as analysis:
         analysis_instructions = analysis.read()
    
    with open('instructions/decision.md', 'r') as decision:
         decision_instructions = decision.read()
    
    # i will fix this
    safe_instructions = analysis_instructions.replace("{", "{{").replace("}", "}}")
    safe_rules = eligibility_criteria.replace("{", "{{").replace("}", "}}")

    agent = Agent.create(
        llms = llm,
        nodes = [
            # StandardNode(
            #     name="convert json to English",
            #     system_prompt="""Summarize the full contents of this JSON in plain English. 
            #     Describe every key and value, including all nested fields and array items. 
            #     Do not skip or omit any data. Preserve the original structure in your explanation,
            #     and avoid adding or assuming any information.""",
            # ),
            StandardNode(
                name="analyze regulations",
                system_prompt = f"Use this applicant: {applicant.prompt}. Analysis instructions:\n{safe_instructions}\n\nRegulation rules:\n{safe_rules}"
            ),
            StandardNode(
                name="make decision",
                system_prompt=f"{decision_instructions}",
            ),
            Stop()
        ],
        known_actions=environment.actions(),
        tools_description=environment.tools_description(),
    )

    tape = DialogTape(steps=[UserStep(content=json.dumps(data, indent=2))])

    for event in main_loop(agent, tape, environment):
        if event.agent_event and event.agent_event.step:
            step = event.agent_event.step
            print(f"Agent step ({step.metadata.node}):\n{step.llm_view()}\n---")
        elif event.observation:
            print(f"Tool call result:\n{event.observation.short_view()}\n---")
        elif event.agent_tape:
            tape = event.agent_tape

    # print("Agent final answer:", tape[-2].reasoning)\
    output = "Agent final answer:" + tape[-2].reasoning
    
    match = re.search(r'Agent final answer: Decision:\s*(.+?)\s*Reason:\s*(.+)', output, re.DOTALL)

    if match:
        decision = match.group(1).strip()
        reason = match.group(2).strip()
        applicant.decision = decision
        applicant.reason = reason
    else:
        print("Could not parse output.")
    
def main():
    for applicant in data_cleaned:
        if applicant.eligibility and not applicant.vulnerablility:
            applicant_check(applicant)
        print(tabulate_result(applicant))

        
if __name__ == "__main__":
    main()
    
