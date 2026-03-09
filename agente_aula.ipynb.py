import os
import re # regex para a identificação das actions
from groq import Groq

# configuração da chave de API (idealmente isso deve vir do arquivo .env)
os.environ["GROQ_API_KEY"] = "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"

# inicializa o cliente do Groq buscando a chave de API correta nas variáveis de ambiente
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Teste inicial para verificar se a API está respondendo corretamente
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

# Imprime o resultado do teste inicial
print(chat_completion.choices[0].message.content)

# definição do agente
class Agent:
    def __init__(self, client, system=""):
        
        # Inicializa o Agente com o cliente do LLM e o System Prompt. O System Prompt é crucial pois define as regras e quais ferramentas o modelo tem à disposição.
        
        self.client = client
        self.system = system
        self.messages = [] # Memória do agente: armazena o histórico da conversa
        
        # Se houver um system prompt, ele é a primeira mensagem do contexto
        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message=""):
        # Permite chamar a instância do agente como uma função. Adiciona a mensagem do usuário, executa o modelo e salva a resposta na memória.
        if message:
            self.messages.append({"role": "user", "content": message})
        
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        # Faz a chamada para a API do modelo enviando todo o histórico de mensagens.
        
        completion = self.client.chat.completions.create(
            model="llama3-70b-8192", # modelo escolhido para executar o agente
            messages=self.messages
        )
        return completion.choices[0].message.content

# SYSTEM PROMPT (a engenharia de prompt majoritariamente responsável por fazer o ReAct funcionar)
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

# FERRAMENTAS

def calculate(operation):
    # ferramenta 1 -  avalia uma expressão matemática passada como string, ou seja, é uma calculadora
    return eval(operation)

def get_planet_mass(planet):
    # ferramenta 2 - retorna a massa de um planeta específico utilizando de match/case
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

# LOOP DE EXECUÇÃO DO AGENTE 

def agent_loop(max_iterations=10, query=""):
    
    # função principal que implementa o ciclo ReAct. A quantidade de iterações é limitada para evitar ciclos infinitos.
    
    agent = Agent(client=client, system=system_prompt)
    tools = ["calculate", "get_planet_mass"] # lista de ferramentas habilitadas
    
    next_prompt = query
    i = 0
    
    while i < max_iterations:
        i += 1
        # o agente raciocina sobre o prompt atual
        result = agent(next_prompt)
        print(result)
        
        # verifica se o agente decidiu tomar uma ação e pediu um PAUSE
        if "PAUSE" in result and "Action" in result:
            # usa Regex para extrair qual ferramenta foi chamada e qual o argumento passado
            action = re.search(r"Action: ([a-z_]+): (.*)", result, re.IGNORECASE)
            
            if action:
                chosen_tool = action.group(1) # Ex: get_planet_mass
                argument = action.group(2)    # Ex: Earth
                
                # executa a ferramenta escolhida no ambiente Python real
                if chosen_tool in tools:
                    result_tool = eval(f"{chosen_tool}('{argument}')")
                    next_prompt = f"Observation: {result_tool}" # devolve o resultado como Observation
                else:
                    next_prompt = "Observation: Tool not found"
                
                print(next_prompt)
                continue # pula para a próxima iteração para o agente continuar pensando
        
        # se o agente chegou a uma resposta final, encerra o loop
        if "Answer" in result:
            break

# teste 
query = "What is the mass of the Earth plus the mass of Mercury and all of it times 5?"

# inicia o agente com uma pergunta que exigirá o uso de ambas as ferramentas
agent_loop(max_iterations=10, query=query)