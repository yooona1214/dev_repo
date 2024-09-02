from langchain.chains import MultiPromptChain
from langchain_openai import ChatOpenAI
from operator import itemgetter

from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser

OPENAI_API_KEY='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'

model = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)
promptNames = ["physics", "math", "history"]
promptDescriptions = [
  "Good for answering questions about physics",
  "Good for answering math questions",
  "Good for answering questions about history",
]



physicsTemplate ='''You are a very smart physics professor. You are great at answering questions about physics in a concise and easy to understand manner. When you don't know the answer to a question you admit that you don't know.

Here is a question:
{input}
'''
mathTemplate = '''You are a very good mathematician. You are great at answering math questions. You are so good because you are able to break down hard problems into their component parts, answer the component parts, and then put them together to answer the broader question.

Here is a question:
{input}'''

historyTemplate = '''You are a very smart history professor. You are great at answering questions about history in a concise and easy to understand manner. When you don't know the answer to a question you admit that you don't know.

Here is a question:
{input}'''

# promptTemplates = [physicsTemplate, mathTemplate, historyTemplate]

# multiPromptChain = MultiPromptChain.from_prompts(
#     llm = model,
#     prompt_infos=
    
#     prompt_infos={
#     promptNames,
#     promptDescriptions,
#     promptTemplates,
# }
# )
prompt_infos = [
    {"name": "physics", "description": "Good for answering questions about physics", "prompt_template": physicsTemplate},
    {"name": "math", "description": "Good for answering math questions", "prompt_template": mathTemplate},
    {"name": "history", "description": "Good for answering questions about history", "prompt_template": historyTemplate},
]

multiPromptChain = MultiPromptChain.from_prompts(
    llm=model,
    prompt_infos=prompt_infos
)

testPromise1 = multiPromptChain.invoke({
  "input": "빛의 속도는?",
})

# testPromise2 = multiPromptChain.invoke({
#   "input": "What is the derivative of x^2?",
# })

# testPromise3 = multiPromptChain.invoke({
#   "input": "Who was the first president of the United States?",
# })

print(testPromise1)

# print(testPromise2)

# print(testPromise3)