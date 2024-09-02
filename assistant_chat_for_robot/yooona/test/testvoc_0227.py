import os 
from chatbot_tools.issue_rag import create_vector_store_as_retriever
from chatbot_tools.create_react_agent_w_history import create_react_agent_w_history
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent, create_react_agent
from langchain_openai import ChatOpenAI

OPENAI_API_KEY='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'


import pika

HOST_NAME = "localhost"
QUEUE_NAME = "Chat"
QUEUE_NAME2 = "Chat2"




print("필요한 파일을 불러오는중...")
loader1 = CSVLoader('./data/엘지_0226.csv')
loader2 = CSVLoader('./data/베어_0226.csv')

data1 = loader1.load()
#data2 = loader2.load()

issue_data = data1

# tool 선언
rag_symptom = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
                                       str2="Please search for and return the most relevant symptom name based on {user_input}.")

rag_cause = create_vector_store_as_retriever(data= issue_data, str1="KT_Robot_Customer_Issue_Guide", 
                                       str2="Please search for and return all the most relevant cause names based on {user_input}.")


# Choose the LLM that will drive the agent
llm_4 = ChatOpenAI(model="gpt-4-0613", api_key=OPENAI_API_KEY)
llm_4_t = ChatOpenAI(model="gpt-4-0125-preview", api_key=OPENAI_API_KEY)
llm_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)


from langchain import hub 
from langchain import hub

tools = [rag_symptom]

prompt = hub.pull("hwchase17/react-chat")
prompt1 = prompt


prompt1.template = '''

Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.


TOOLS:
------

Assistant has access to the following tools:

{tools}



To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```
When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Please kindly ask customers what inconveniences they have when using the KT service robot.

Simply have the client describe their specific symptoms. If the customer says something unrelated, just respond and encourage them to talk about their symptoms again.

If you think that you have described the symptom, please use the search tool below to answer the symptom in one word and include the word "step1_finished" before the sentence.

All response must be answered in korean.
Begin!

Previous conversation history:
{chat_history}


New input: {input}
{agent_scratchpad}
'''



#print('P1',prompt1)


chat_history = []


#step1. 증상 매핑(파악)을 위한 chat
agent = create_react_agent_w_history(llm_4_t, tools, prompt1)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

from langchain_core.messages import AIMessage, HumanMessage

step_flag = 0



def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)


    if step_flag !=1:
        #step1. 증상 매핑(파악)을 위한 chat
        def callback1(ch, method, properties, body):
            message = body.decode('utf-8')  # 바이트를 문자열로 디코딩
            #print("Received message:", message)

            response= agent_executor.invoke({"input": message, "chat_history": chat_history})
            chat_history.extend(
                [
                    HumanMessage(content=message),
                    AIMessage(content=response["output"]),
                ]
            )
            
            res = '\nAI: '+response["output"]        
            
            
            if "step1_finished" in response["output"]:
                step_flag = 1
            
            send_message(res)
            
    elif step_flag ==1:
        
        def callback1(ch, method, properties, body):
            message = body.decode('utf-8')  # 바이트를 문자열로 디코딩

            cause_list = ['주행 관련 설정 오류', '로봇 센서 이물질 묻음', '금지구역 진입']
            print('고객님의 증상에 대한 원인을 분석중입니다....' )
            prompt2 = prompt
            prompt2.input_variables = ['cause_list','chat_history', 'input']
            prompt2.template = '''

            Check the list of causes: {cause_list} given. And ask if the customer has ever done anything related to these causes. 
            Please ask questions one by one, as if playing Twenty Questions.
            Ask questions one by one, and if the customer says the cause is correct, end the conversation.
            All response must be answered in korean.
            Begin!

            Previous conversation history:
            {chat_history}


            New input: {input}
            '''

            #print(prompt2)
            #step2. 원인 매핑(파악)을 위한 스무고개
            chain = (
                prompt2
                | llm_4_t
            )
            
            response = chain.invoke({"input": '내 증상에 대한 원인을 맞추고, 그에 맞는 조치를 알려주세요. 당신의 질문으로 스무고개 놀이를 시작해주세요. 질문을 하나씩 해주세요.', "chat_history": chat_history, "cause_list": cause_list})
            
            step_flag =2
            send_message(response.content)

    elif step_flag ==2:
        #step2. 원인 매핑(파악)을 위한 스무고개
        def callback1(ch, method, properties, body):
            message = body.decode('utf-8')  # 바이트를 문자열로 디코딩

            cause_list = ['주행 관련 설정 오류', '로봇 센서 이물질 묻음', '금지구역 진입']
            print('고객님의 증상에 대한 원인을 분석중입니다....' )
            prompt2 = prompt
            prompt2.input_variables = ['cause_list','chat_history', 'input']
            prompt2.template = '''

            Check the list of causes: {cause_list} given. And ask if the customer has ever done anything related to these causes. 
            Please ask questions one by one, as if playing Twenty Questions.
            Ask questions one by one, and if the customer says the cause is correct, end the conversation.
            All response must be answered in korean.
            Begin!

            Previous conversation history:
            {chat_history}


            New input: {input}
            '''

            chain = (
                prompt2
                | llm_4_t
            )


            response = chain.invoke({"input": message, "chat_history": chat_history, "cause_list": cause_list})
            
            #print(response.content)    
            chat_history.extend(
                [
                    HumanMessage(content=message),
                    AIMessage(content=response.content),
                ]
            )
            
            send_message(response.content)
    
    channel.basic_consume(queue=QUEUE_NAME,
                          on_message_callback=callback1,
                          auto_ack=True)

    
   

    try:
        print("Waiting for messages.")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        print('Ctrl+C is Pressed.')


def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST_NAME))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME2)

    channel.basic_publish(exchange='', routing_key=QUEUE_NAME2, body=message)
    #print(f"Sent message.\n{message}")

    connection.close()


if __name__ == '__main__':
    main()