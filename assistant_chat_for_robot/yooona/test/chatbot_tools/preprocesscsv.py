from langchain.tools import BaseTool
from typing import Optional, Type
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
import pandas as pd
from langchain.pydantic_v1 import BaseModel, Field



class CSVProcessInput(BaseModel):
    issue_value: list = Field(description="이슈 분류를 입력")
class PreProcessCSV(BaseTool):
    """Convert CSV file to pandas dataframe."""
    name = "Classifier"
    description = "useful for when you need to find the cause about issues"
    args_schema: Type[BaseModel] = CSVProcessInput
    return_direct: bool = False

    def _run(
        self, issue_value :list, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        for issue in issue_value:
            csv_path= './data/주행관련VOC테스트_이슈-원인0123.csv'

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
            print('--------------')
            print(result_df)
            print('--------------')
            cause_list = list(result_df['원인'])
            print('cause_list:',cause_list)
            
        return cause_list