# Import things that are needed generically
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
import pandas as pd

@tool
def preprocess_csv(issue_value: list, csv_path:str) -> pd.DataFrame:
    """preprocess csv file to pandas dataframe."""
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


    return result_df




