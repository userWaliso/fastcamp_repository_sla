import os
from groq import Groq

os.environ["GROQ_API_KEY"] = "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"



client = Groq(
    api_key=os.environ.get("GROK_API_KEY"),
)

chat_complatation = client.chat_completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_complatation.choices[0].message.content)

class Agent:
    def __init__(self, client, system=""):
        self.client = client
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=self.messages
        )
        return completion.choices[0].message.content

system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.

Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

get_planet_mass:
e.g. get_planet_mass: Earth
returns weight of the planet in kg

Example session:

Question: What is the mass of Earth times 2?
Thought: I need to find the mass of the Earth
Action: get_planet_mass: Earth
PAUSE 

You will be called again with this:

Observation: 5.972e24

Thought: I need to multiply this by 2
Action: calculate: 5.972e24 * 2
PAUSE

You will be called again with this: 

Observation: 1.1944e25

If you have the answer, output it as the Answer.

Answer: The mass of Earth times 2 is 1.1944e25.

Now it's your turn:
"""

def calculate(operation):
    return eval(operation)

def get_planet_mass(planet):
    match planet.lower():
        case "earth":
            return 5.972e24
        case "jupiter":
            return 1.898e27
        case "mars":
            return 6.39e23
        case "mercury":
            return 3.285e23
        case "neptune":
            return 1.024e26
        case "saturn":
            return 5.683e26
        case "uranus":
            return 8.681e25
        case "venus":
            return 4.867e24
        case "pluto":
            return 1.309e22
        case _:
            return 0.0

import re

def agent_loop(max_iterations=10, query=""):
    agent = Agent(client=client, system=system_prompt)
    tools = ["calculate", "get_planet_mass"]
    
    next_prompt = query
    i = 0
    
    while i < max_iterations:
        i += 1
        result = agent(next_prompt)
        print(result)
        
        if "PAUSE" in result and "Action" in result:
            action = re.search(r"Action: ([a-z_]+): (.*)", result, re.IGNORECASE)
            
            if action:
                chosen_tool = action.group(1)
                argument = action.group(2)
                
                if chosen_tool in tools:
                    result_tool = eval(f"{chosen_tool}('{argument}')")
                    next_prompt = f"Observation: {result_tool}"
                else:
                    next_prompt = "Observation: Tool not found"
                
                print(next_prompt)
                continue
        
        if "Answer" in result:
            break

query = "What is the mass of the Earth plus the mass of Mercury and all of it times 5?"

agent_loop(max_iterations=10, query=query)