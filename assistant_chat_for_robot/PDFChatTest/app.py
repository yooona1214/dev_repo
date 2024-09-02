# importing dependencies
from dotenv import load_dotenv
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import faiss
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from htmlTemplates import css, bot_template, user_template

# creating custom template to guide llm model
custom_template = """
        너의 역할은 로봇의 상태나 문제를 파악할 수 있는 로봇 제조사의 관련 문서들을 읽었고, 이를 검색하여 정보를 친절하게 제공하는 챗봇 서비스야.
        만일 정확한 문제를 파악 할 수 없더라도 고객이 문제를 해결 할 수 있도록 다음 질문을 해줘

        고객은 무작정 '어떤 부분이 동작하지 않습니다.' 처럼 범위가 넓은 질문을 할 가능성이 높다는 것을 인지하자.
        너가 한번에 정확한 답변을 하기에 범위가 넓은 질문을 받았을 경우, 고객에게 다시 질문을 해서 어떤 문제인지 유추하는 거야. 이 때, 가능한 답변의 범주를 개조식으로 나열해서 고객이 다음 질문을 구체화하기 쉽도록 하자.

        
        너가 답변한걸 챗봇 서비스 앱의 UI를 통해 고객에게 보여줄거고, 이를 통해 고객은 이전 보다 구체화된 질문을 다시 할 거야. 
        
Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""

CUSTOM_QUESTION_PROMPT = PromptTemplate.from_template(custom_template)

# extracting text from pdf
def get_pdf_text(docs):
    text=""
    for pdf in docs:
        pdf_reader=PdfReader(pdf)
        for page in pdf_reader.pages:
            text+=page.extract_text()
    return text

# converting text to chunks
def get_chunks(raw_text):
    text_splitter=CharacterTextSplitter(separator="\n",
                                        chunk_size=1000,
                                        chunk_overlap=200,
                                        length_function=len)   
    chunks=text_splitter.split_text(raw_text)
    return chunks

# using all-MiniLm embeddings model and faiss to get vectorstore
def get_vectorstore(chunks):
    embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                     model_kwargs={'device':'cpu'})
    vectorstore=faiss.FAISS.from_texts(texts=chunks,embedding=embeddings)
    return vectorstore

# generating conversation chain  
def get_conversationchain(vectorstore):
    llm=ChatOpenAI(temperature=0.2,               # 창의성 (0.0 ~ 2.0) 
                   
                   model_name='gpt-3.5-turbo',  # 모델명
                  )

    memory = ConversationBufferMemory(memory_key='chat_history', 
                                      return_messages=True,
                                      output_key='answer') # using conversation buffer memory to hold past information
    conversation_chain = ConversationalRetrievalChain.from_llm(
                                llm=llm,
                                retriever=vectorstore.as_retriever(),
                                condense_question_prompt=CUSTOM_QUESTION_PROMPT,
                                memory=memory,
                                verbose=True)
    return conversation_chain

# generating response from user queries and displaying them accordingly
def handle_question(question):
    response=st.session_state.conversation({'question': question})
    st.session_state.chat_history=response["chat_history"]
    for i,msg in enumerate(st.session_state.chat_history):
        if i%2==0:
            st.write(user_template.replace("{{MSG}}",msg.content,),unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}",msg.content),unsafe_allow_html=True)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",page_icon=":books:")
    st.write(css,unsafe_allow_html=True)
    if "conversation" not in st.session_state:
        st.session_state.conversation=None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history=None
    
    st.header("서비스 로봇 챗봇 TEST v240102 :books:")
    question=st.text_input("Ask question from your document:")
    if question:
        handle_question(question)
        print(handle_question(question))
    with st.sidebar:
        st.subheader("Your documents")
        docs=st.file_uploader("Upload your PDF here and click on 'Process'",accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                
                #get the pdf
                raw_text=get_pdf_text(docs)
                
                #get the text chunks
                text_chunks=get_chunks(raw_text)
                
                #create vectorstore
                vectorstore=get_vectorstore(text_chunks)
                
                #create conversation chain
                print(get_conversationchain(vectorstore))
                st.session_state.conversation=get_conversationchain(vectorstore)
                #print(text_chunks)

if __name__ == '__main__':
    main()