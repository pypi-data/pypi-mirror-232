
import pandas as pd
import requests
from datetime import datetime



class BaiduSearch:

    def __init__(self):
        self.stock_hot_url = "https://finance.pae.baidu.com/vapi/v1/hotrank"

    def stock_hot(self,symbol: str = "A股", dt: datetime = datetime(2023,4,28), time_type: str = "day") -> pd.DataFrame:
        """
            百度股市通-热搜股票
            https://gushitong.baidu.com/expressnews
            :param symbol: choice of {"全部", "A股", "港股", "美股"}
            :type symbol: str
            :param date: 日期
            :type date: datetime
            :param time: time_type="day"；choice of {"day", "hour"}
            :type time: str
            :return: 股东人数及持股集中度
            :rtype: pandas.DataFrame
        """
        hour_str = datetime.now().hour
        symbol_map = {
            "全部": "all",
            "A股": "ab",
            "港股": "hk",
            "美股": "us",
        }

        params = {
            "tn": "wisexmlnew",
            "dsp": "iphone",
            "product": "stock",
            "day": dt.strftime("%Y%m%d"),
            "hour": hour_str,
            "pn": "0",
            "rn": "1000",
            "market": symbol_map[symbol],
            "type": time_type,
            "finClientType": "pc",
        }
        response = requests.get(self.stock_hot_url, params=params)
        data_json = response.json()
        temp_df = pd.DataFrame(data_json["Result"]["body"], columns=data_json["Result"]["header"])
        temp_df["现价"] = pd.to_numeric(temp_df["现价"], errors="coerce")
        temp_df["排名变化"] = pd.to_numeric(temp_df["排名变化"], errors="coerce")
        return temp_df


if __name__ == "__main__":
    baidu = BaiDuSearch()
    stock_hot_search_baidu_df = baidu.stock_hot(symbol='A股',dt=datetime(2023,8,15),time_type='day')
    print(stock_hot_search_baidu_df)