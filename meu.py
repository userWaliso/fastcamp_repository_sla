import os
import re
from dotenv import load_dotenv 
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_complatation = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

# print(chat_complatation.choices[0].message.content)

class Agent:
    def __init__(self, client, system=""):
        self.client = client
        self. system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system","content": system})
        
    def __call__(self,message=""):
            if message:
                self.messages.append({"role": "user", "content": message})
            result = self.execute()
            self.messages.append({"role": "assistant", "content": result})
            return result

    def execute(self):
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=self.messages
        )
        return completion.choices[0].message.content

def obter_clima(cidade):
    if cidade.lower() == "paris":
        return "15°C e chuvoso"
    elif cidade.lower() == "toquio":
        return "22°C e ensolarado"
    else:
        return "Clima desconhecido"

def tempo_de_voo(destino):
    if destino.lower() == "paris":
        return "11 horas"
    elif destino.lower() == "toquio":
        return "24 horas"
    else:
        return "Tempo de voo desconhecido"
    
system_prompt = """
Você é um agente de viagens e roda em um ciclo de Thought, Action, PAUSE, Observation.
No final, você deve fornecer uma Answer (Resposta).

Use Thought (Pensamento) para descrever o que você precisa fazer.
Use Action (Ação) para rodar uma das ferramentas disponíveis e retorne PAUSE.
Observation (Observação) será o resultado da sua ação.

Suas ferramentas disponíveis são:

obter_clima:
exemplo: obter_clima: Paris
Retorna como está o tempo na cidade.

tempo_de_voo:
exemplo: tempo_de_voo: Toquio
Retorna o tempo de voo saindo do Brasil.

Exemplo de uso:
Question: Como está o clima em Paris e quanto tempo demora para chegar?
Thought: Preciso primeiro descobrir o clima em Paris.
Action: obter_clima: Paris
PAUSE

Você será chamado novamente com:
Observation: 15°C e chuvoso

Thought: Agora preciso saber o tempo de voo para Paris.
Action: tempo_de_voo: Paris
PAUSE

Você será chamado novamente com:
Observation: 11 horas

Answer: O clima em Paris é de 15°C e chuvoso, e o voo saindo do Brasil demora cerca de 11 horas.

Agora é a sua vez:
"""

def exec (question):
    agente = Agent(client=client, system=system_prompt)
    tools = ["obter_clima", "tempo_de_voo"]

    next_prompt = question

    for i in range(10):
        result = agente(next_prompt)
        print(result)

        if "PAUSE" in result and "Action" in result:
            bora = re.search(r"Action: ([a-z_]+): (.*)",result, re.IGNORECASE)

            if bora:
                tool = bora.group(1);
                platao = bora.group(2).strip()

                if tool in tools:
                    result_ferramenta = eval(f"{tool}('{platao}')")
                    next_prompt = f"Observation: {result_ferramenta}"
                    # print(next_prompt)
                    continue

        if "Answer" in result:
            break

pergunta = "qual a temperatura de toquio? E quanto tempo demoro pra chegar em paris?"
print(pergunta)
exec(pergunta)
