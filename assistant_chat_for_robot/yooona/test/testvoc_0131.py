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

def preprocess_csv(issue_value, csv_path):

    import pandas as pd
    for issue in issue_value:

        df = pd.read_csv(csv_path)

        selected_rows = df[df['이슈분류'] == issue]

        # 원인을 탐색하고 각 원인이 얼마나 발생했는지 정규화하여 저장
        issue_counts = selected_rows['원인(원인별명)'].value_counts(normalize=True)

        # 각 원인에 대한 '고객조치가능여부' 값 가져오기
        customer_actions = selected_rows.groupby('원인(원인별명)')['고객조치가능여부'].first()
        detail_actions = selected_rows.groupby('원인(원인별명)')['조치 방법'].first()

        # DataFrame으로 변환
        result_df = pd.DataFrame({
            '원인': issue_counts.index,
            '고객조치가능여부': customer_actions.loc[issue_counts.index].values,
            '빈도': issue_counts.values,
            '조치 방법': detail_actions.loc[issue_counts.index].values
        })

        result_df = result_df.sort_values(by=['고객조치가능여부', '빈도'], ascending=[False, False])
        # result_df = result_df.sort_values(by=['빈도'], ascending=[False])
        print('--------------')
        print(result_df)
        print('--------------')

    print(type(result_df))
    return result_df

def main():
    model = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)
    prompt1 = ChatPromptTemplate.from_messages(
        [
            ("system", "당신은 로봇 사용 고객의 VOC를 처리하는 챗봇입니다. 고객님의 이슈가 어떤 이슈 분류에 해당하는지 검색해주세요."),
            ("user", "{input}"),
        ]
    )


    prompt2 = ChatPromptTemplate.from_messages(
        [
            ("system", "당신은 로봇 사용 고객의 VOC를 처리하는 챗봇입니다. 사용자의 이슈가 어떤 이슈 분류에 해당하는지 검색해주세요.{검색결과}를 기반으로 해당되는 이슈분류 하나를 찾아서 한 단어로 답하세요."),
        ]        
        
    )



    print("필요한 파일을 불러오는중...")
    loader1 = CSVLoader('./data/주행관련VOC테스트_입력_이슈.csv')
    # loader2 = CSVLoader('./data/주행관련VOC테스트_이슈_원인.csv')


    data1 = loader1.load()
    #data2 = loader2.load()
    issue_data1 = data1
    #issue_data2 = data2



    #print(data)

    def create_vector_store_as_retriever(data, str1, str2):

        text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
        docs = text_splitter.split_documents(data)


        embedding=OpenAIEmbeddings(openai_api_key =OPENAI_API_KEY)
        vectorstore = Chroma.from_documents(documents=docs,embedding=embedding)

        retriever = vectorstore.as_retriever()
        
        tool = create_retriever_tool(
            retriever,
            str1,
            str2,
        )
        
        return tool

    tool = create_vector_store_as_retriever(data= issue_data1, str1="KT_Robot_Customer_Issue_Guide", str2="Find appropriate issue categories from user input")




    #초기 메모리 선언
    memory = ConversationBufferMemory(return_messages=True)
    print(memory.load_memory_variables({}))


    chain1 = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt1
        | model
        | StrOutputParser()
        | tool
    )

    chain2 = (
        { "검색결과": chain1}
        | prompt2
        | model
        | StrOutputParser()
    )

    user_input = input("\n대화를 입력해주세요:")
    inputs = {"input": user_input,}

    #대답
    response = chain2.invoke(inputs)
    print(response)
    memory.save_context(inputs, {"output": response}) #response.content


    issue_val = []
    issue_val.append(str(response))

    path = './data/주행관련VOC테스트_이슈-원인0123.csv'
    
    Cause_list = preprocess_csv(issue_val, path)
    cause_list_to_string = str(Cause_list)

    prompt3 = ChatPromptTemplate.from_messages(
        [
            ("system", '''
                    
                    {이슈리스트}를 참고하여 1번째 부터 n번 째까지 행의 원인을 발생시키는 행동을 최근에 한 적 있는지 고객에게 친절하게 한문장으로 물어봐주세요.
                    n은 {이슈리스트}의 colomn의 개수입니다.
                    if 고객이 n번째 행의 원인이 맞거나, 맞는것 같다고 대답하면 :
                        if 조치 가능여부 == True
                            조치방법을 안내해주세요.
                        if 조치 가능여부 ==False라면, 
                            감사합니다. A/S기사를 출동 시켜드리겠습니다. 라고 말해주세요.
                    elif 고객이 n번째 행의 원인이 아닌 것 같다고 하거나 잘모르겠다고 대답하면:
                        n+1 행의 원인을 다시 물어봐주세요.
                    
                    대화가 한턴 반복됨에 따라 n은 1부터 시작해서 n까지 증가한다.
                    n번째 행을 물어보면 
                    감사합니다. 대화를 종료하겠다고 말해주세요.
             '''),
            ("user", "{input}"),
        ]
    )

            # 그 원인이 맞다고 답하면, 그에 맞는 조치방법을 안내해주세요. 조치 방법이 없으면 A/S 기사를 출동시키겠다고 하세요. 
            # 그 원인이 아니거나 모르겠다고 한다면, {이슈리스트}에서 다음 row의 원인을 물어봐주세요.
            # 질문과 대답은 한 문장 이내로 해주세요.  


    chain3 = (
            RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt3 
        | model
        | StrOutputParser()
    )
    inputs = {"input": '', "이슈리스트": cause_list_to_string}

    #대답
    response = chain3.invoke(inputs)
    print('\nAI:',response)  
    memory.save_context({"input": ''}, {"output": response}) #response.content

    while True:
        user_input = input('대화를 입력해주세요:')
        inputs = {"input": user_input, "이슈리스트": cause_list_to_string}

        #대답
        response = chain3.invoke(inputs)
        print(response)
        memory.save_context({"input":user_input}, {"output": response}) #response.content

        #print('\n\n\n',memory.load_memory_variables({}))







    # while True:
        
        
    #     user_input = input("\n대화를 입력해주세요:")
    #     inputs = {"input": user_input}

    #     #대답
    #     response = chain3.invoke(inputs)
    #     print(response)

    #     #대화 저장
    #     memory.save_context(inputs, {"output": response.content}) #response.content
    #     print('\n\n\n대화기록:',memory.load_memory_variables({}))











if __name__ == '__main__':
    main()
    