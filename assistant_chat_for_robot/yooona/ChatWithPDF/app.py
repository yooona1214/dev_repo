import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from htmlTemplates import css, bot_template, user_template
import os


OPENAI_API_KEY = "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"

CONDENSEprompt = """

1. 너는 역할은 로봇 관련 챗봇 서비스를 제공하는 에이전트야
2. 첫 번째로 해야할 일은 로봇 메뉴얼에 고객의 질문에 답을 할 수 있는지 보는거야
만약, 답변을 할 수 없다면, 고객이 물어본 질문을 로봇 메뉴얼에 나올법한 단어로 치환해서 고객에게 이런 질문을 하고자 하시는게 맞냐고 물어보자
예를 들어, 로봇에 서랍이 몇개야?라고 고객이 물어보면, 로봇에 있는 트레이/선반을 의미하시는 건가요? 이렇게 역으로 고객에게 물어보는거지
3.절대 고객에게 직접 메뉴얼을 참조하라고 하지마
4. 내가 말하는 걸 기억해

Context: {context}
Chat history: {chat_history}
Follow Up Input: {chat_history}, {question}
Helpful Answer:


"""

QA_PROMPT = PromptTemplate.from_template(CONDENSEprompt)


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_text_chunks2(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_documents(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY)
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

from langchain.vectorstores import Chroma
def get_vectorstore2(docs):
    embedding=OpenAIEmbeddings(openai_api_key = OPENAI_API_KEY)
    vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo-0613",openai_api_key = OPENAI_API_KEY)

    # memory management for store chat history [return_messages=True]
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=vectorstore.as_retriever(), 
        memory=memory,
        condense_question_prompt = QA_PROMPT
        # combine_docs_chain_kwargs={"prompt": prompt}
    )
    # print(QA_PROMPT)
    return conversation_chain


# managing the interaction between a user and a chatbot 
def handle_user_input(user_question):

    # if st.session_state.conversation:
    #     response = st.session_state.conversation({'question': user_question})
    #     st.session_state.chat_history = response['chat_history']
    #     for i, message in enumerate(st.session_state.chat_history):
    #         if i % 2 == 0: # even: user
    #             st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
    #         else: # odd: bot
    #             st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

    # else:
    #     st.warning("Please press 'Add Data' before asking a question.")


    if st.session_state.conversation:
        
        # # Get the current conversation history from the session state
        chat_history = st.session_state.chat_history or []
        print("--------------------------")

        # Pass the updated conversation history to the conversation chain
        response = st.session_state.conversation({'chat_history': chat_history, 'question': user_question})
        st.session_state.chat_history = response['chat_history']


        # Display the conversation
        for i, message in enumerate(st.session_state.chat_history):
            if i % 2 == 0: # even: user
                print('==============chat turn============================')
                st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

                user_message = {"role": "user", "content": message.content}
                print(i, 'user: ', message.content)
                # chat_history.append(user_message)

            else: # odd: bot
                st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)

                chatbot_message = {"role": "chatbot", "content": message.content}
                # chat_history.append(chatbot_message)
                print(i, 'bot: ', message.content)
            
                # # Update the chat history in the session state
                # st.session_state.chat_history = response.chat_history
                print('-----------')
                print('st.session_state.chat_history: ', st.session_state.chat_history)
            
    else:
        st.warning("Wait")

from langchain.document_loaders import PyPDFLoader

def main():
    st.set_page_config(page_title="Chat with KT ROBOT AI AGENT :robot_face:", page_icon=":robot_face:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with KT ROBOT AI AGENT :robot_face:")
    user_question = st.text_input("Ask a question about your robot:")
    if user_question:
        handle_user_input(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Add Data'", accept_multiple_files=True
        )

        if st.button("Add Data"):
            with st.spinner("Adding Data..."):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore)
        # with st.spinner("adding data,,,?"):
        #     loader = PyPDFLoader("LG2.pdf")
        #     raw_text = loader.load()

        #     # get the text chunks
        #     text_chunks = get_text_chunks2(raw_text)

        #     # create vector store
        #     vectorstore = get_vectorstore2(text_chunks)

        #     # create conversation chain
        #     st.session_state.conversation = get_conversation_chain(vectorstore)

if __name__ == "__main__":
    main()            
