import os
import re # regex para a identificação das actions
from dotenv import load_dotenv 
from groq import Groq

# carrega as variáveis do arquivo .env
load_dotenv()

# inicializa o cliente do Groq buscando a chave de API correta nas variáveis de ambiente
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# teste inicial para verificar se a API está respondendo corretamente
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama-3.3-70b-versatile",
)

# definição do agente
class Agent:
    def __init__(self, client, system=""):
        # inicializa o agente com o cliente do LLM e o system prompt
        self.client = client
        self.system = system
        self.messages = [] # memória do agente: armazena o histórico da conversa
        
        # se houver um system prompt, ele é a primeira mensagem do contexto
        if self.system:
            self.messages.append({"role": "system","content": system})
        
    def __call__(self, message=""):
        # permite chamar a instância do agente como uma função.
        # adiciona a mensagem do usuário, executa o modelo e salva a resposta na memória.
        if message:
            self.messages.append({"role": "user", "content": message})
        
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        # faz a chamada para a API do modelo enviando todo o histórico de mensagens
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile", # modelo escolhido para executar o agente
            messages=self.messages
        )
        return completion.choices[0].message.content

# FERRAMENTAS

def obter_clima(cidade):
    # ferramenta 1 - retorna uma simulação de clima de uma cidade específica
    if cidade.lower() == "paris":
        return "15°C e chuvoso"
    elif cidade.lower() == "toquio":
        return "22°C e ensolarado"
    else:
        return "Clima desconhecido"

def tempo_de_voo(destino):
    # ferramenta 2 - retorna uma simulação de tempo de voo saindo do Brasil
    if destino.lower() == "paris":
        return "11 horas"
    elif destino.lower() == "toquio":
        return "24 horas"
    else:
        return "Tempo de voo desconhecido"
    
# SYSTEM PROMPT (a engenharia de prompt para o agente de viagens)
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

# LOOP DE EXECUÇÃO DO AGENTE

def executar_agente(question):
    
    # função principal que implementa o ciclo ReAct. A quantidade de iterações é limitada
    
    agente = Agent(client=client, system=system_prompt)
    tools = ["obter_clima", "tempo_de_voo"] # lista de ferramentas habilitadas

    next_prompt = question

    for i in range(10):
        # o agente raciocina sobre o prompt atual
        result = agente(next_prompt)
        print(result)

        # verifica se o agente decidiu tomar uma ação e pediu um PAUSE
        if "PAUSE" in result and "Action" in result:
            # usa Regex para extrair qual ferramenta foi chamada e qual o argumento passado
            bora = re.search(r"Action: ([a-z_]+): (.*)", result, re.IGNORECASE)

            if bora:
                tool = bora.group(1)
                platao = bora.group(2).strip()

                # executa a ferramenta escolhida no ambiente 
                if tool in tools:
                    result_ferramenta = eval(f"{tool}('{platao}')")
                    next_prompt = f"Observation: {result_ferramenta}" # devolve o resultado como Observation
                    continue

        # se o agente chegou a uma resposta final, encerra o loop
        if "Answer" in result:
            break

# teste
pergunta = "qual a temperatura de toquio? E quanto tempo demoro pra chegar em paris?"
print(pergunta)

# inicia o agente com a pergunta que exigirá as ferramentas
executar_agente(pergunta)