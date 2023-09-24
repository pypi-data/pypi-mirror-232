# 人气榜
import pandas as pd
import requests
from datetime import datetime
from weathon.utils.search.baidu import BaiduSearch

class StockHot:

    def __init__(self):
        self._init_url()
    
    def _init_url(self) -> None:
        self._soaring_stock_url = "https://emappdata.eastmoney.com/stockrank/getAllHisRcList"
        self._hot_rank_url = "https://emappdata.eastmoney.com/stockrank/getAllCurrentList"
        self._rank_history_url = "https://emappdata.eastmoney.com/stockrank/getHisList"
        self._rank_follow_url = "https://emappdata.eastmoney.com/stockrank/getHisProfileList"
        self._hot_keyword_url = "https://emappdata.eastmoney.com/stockrank/getHotStockRankList"
        self._rank_related_url = "https://emappdata.eastmoney.com/stockrank/getFollowStockRankList"
        self._rank_realtime_url = "https://emappdata.eastmoney.com/stockrank/getCurrentList"
        self._rand_latest_url = "https://emappdata.eastmoney.com/stockrank/getCurrentLatest"

    def baidu_search_hot(self,symbol='A股',dt=datetime(2023,8,15),time_type='day') -> pd.DataFrame:
        """百度股市通-热搜股票"""
        baidu_search = BaiduSearch()
        return baidu_search.stock_hot(symbol=symbol,dt=dt, time_type=time_type)


    def soaring_stocks(self) -> pd.DataFrame:
        """
        东方财富-个股人气榜-飙升榜
        https://guba.eastmoney.com/rank/
        :return: 飙升榜
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "",
            "pageNo": 1,
            "pageSize": 100,
        }
        response = requests.post(self._soaring_stock_url, json=payload)
        data_json = response.json()
        temp_rank_df = pd.DataFrame(data_json["data"])
        temp_rank_df["mark"] = [
            "0" + "." + item[2:] if "SZ" in item else "1" + "." + item[2:]
            for item in temp_rank_df["sc"]
        ]
        
        params = {
            "ut": "f057cbcbce2a86e2866ab8877db1d059",
            "fltt": "2",
            "invt": "2",
            "fields": "f14,f3,f12,f2",
            "secids": ",".join(temp_rank_df["mark"]) + ",?v=08926209912590994",
        }
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        r = requests.get(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_df.columns = ["最新价", "涨跌幅", "代码", "股票名称"]
        temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
        temp_df["涨跌额"] = temp_df["最新价"] * temp_df["涨跌幅"] / 100
        temp_df["当前排名"] = temp_rank_df["rk"]
        temp_df["代码"] = temp_rank_df["sc"]
        temp_df["排名较昨日变动"] = temp_rank_df["hrc"]
        temp_df = temp_df[
            [
                "排名较昨日变动",
                "当前排名",
                "代码",
                "股票名称",
                "最新价",
                "涨跌额",
                "涨跌幅",
            ]
        ]
        temp_df["排名较昨日变动"] = pd.to_numeric(temp_df["排名较昨日变动"], errors="coerce")
        temp_df["当前排名"] = pd.to_numeric(temp_df["当前排名"], errors="coerce")
        temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
        return temp_df

    def hot_rank(self) -> pd.DataFrame:
        """
        东方财富-个股人气榜-人气榜
        https://guba.eastmoney.com/rank/
        :return: 人气榜
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "",
            "pageNo": 1,
            "pageSize": 100,
        }
        response = requests.post(self.hot_rank_url, json=payload)
        data_json = response.json()
        temp_rank_df = pd.DataFrame(data_json["data"])

        temp_rank_df["mark"] = [
            "0" + "." + item[2:] if "SZ" in item else "1" + "." + item[2:]
            for item in temp_rank_df["sc"]
        ]
        ",".join(temp_rank_df["mark"]) + "?v=08926209912590994"
        params = {
            "ut": "f057cbcbce2a86e2866ab8877db1d059",
            "fltt": "2",
            "invt": "2",
            "fields": "f14,f3,f12,f2",
            "secids": ",".join(temp_rank_df["mark"]) + ",?v=08926209912590994",
        }
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        r = requests.get(url, params=params)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_df.columns = ["最新价", "涨跌幅", "代码", "股票名称"]
        temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
        temp_df["涨跌额"] = temp_df["最新价"] * temp_df["涨跌幅"] / 100
        temp_df["当前排名"] = temp_rank_df["rk"]
        temp_df["代码"] = temp_rank_df["sc"]
        temp_df = temp_df[
            [
                "当前排名",
                "代码",
                "股票名称",
                "最新价",
                "涨跌额",
                "涨跌幅",
            ]
        ]
        temp_df["当前排名"] = pd.to_numeric(temp_df["当前排名"], errors="coerce")
        return temp_df


    def rank_history(self,symbol: str = "SZ000665") -> pd.DataFrame:
        """
        东方财富-个股人气榜-历史趋势
        https://guba.eastmoney.com/rank/stock?code=000665
        :param symbol: 带市场表示的证券代码
        :type symbol: str
        :return: 个股的历史趋势
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "",
            "srcSecurityCode": symbol,
        }
        response = requests.post(self._rank_history_url, json=payload)
        data_json = response.json()
        temp_df = pd.DataFrame(data_json["data"])
        temp_df["证券代码"] = symbol
        temp_df.columns = ["时间", "排名", "证券代码"]
        temp_df = temp_df[["时间", "排名", "证券代码"]]
        return temp_df

    def rank_follows(self,symbol: str = "SZ000665") -> pd.DataFrame:
        """
        东方财富-个股人气榜-粉丝特征
        https://guba.eastmoney.com/rank/stock?code=000665
        :param symbol: 带市场表示的证券代码
        :type symbol: str
        :return: 个股的粉丝特征
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "",
            "srcSecurityCode": symbol,
        }
        response = requests.post(self._rank_follow_url, json=payload)
        data_json = response.json()
        temp_df = pd.DataFrame(data_json["data"])
        temp_df["证券代码"] = symbol
        temp_df["新晋粉丝"] = (pd.DataFrame(data_json["data"])["newUidRate"].str.strip("%").astype(float) / 100)
        temp_df["铁杆粉丝"] = (pd.DataFrame(data_json["data"])["oldUidRate"].str.strip("%").astype(float) / 100)
        temp_df = temp_df[["证券代码", "新晋粉丝", "铁杆粉丝"]]
        return temp_df

    def hot_keyword(self,symbol: str = "SZ000665")  -> pd.DataFrame:
        """
        东方财富-个股人气榜-热门关键词
        https://guba.eastmoney.com/rank/stock?code=000665
        :param symbol: 带市场表示的证券代码
        :type symbol: str
        :return: 热门关键词
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "srcSecurityCode": symbol,
        }
        response = requests.post(self._hot_keyword_url, json=payload)
        data_json = response.json()
        temp_df = pd.DataFrame(data_json["data"])
        del temp_df["flag"]
        temp_df.columns = ["时间", "股票代码", "概念名称", "概念代码", "热度"]
        return temp_df
        

    def rank_related(self, symbol: str = "SZ000665") -> pd.DataFrame:
        """
        东方财富-个股人气榜-相关股票
        https://guba.eastmoney.com/rank/stock?code=000665
        :param symbol: 带市场表示的证券代码
        :type symbol: str
        :return: 相关股票
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "srcSecurityCode": symbol,
        }
        response = requests.post(self._rank_related_url, json=payload)
        data_json = response.json()
        temp_df = pd.DataFrame.from_dict(data_json["data"])
        temp_df.columns = ["时间", "-", "股票代码", "-", "相关股票代码", "涨跌幅", "-"]
        temp_df = temp_df[["时间", "股票代码", "相关股票代码", "涨跌幅"]]
        temp_df["涨跌幅"] = temp_df["涨跌幅"].str.strip("%")
        temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"])
        return temp_df

    def rank_realtime(self,symbol: str = "SZ000665") -> pd.DataFrame:
        """
        东方财富-个股人气榜-实时变动
        https://guba.eastmoney.com/rank/stock?code=000665
        :param symbol: 带市场表示的证券代码
        :type symbol: str
        :return: 实时变动
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "",
            "srcSecurityCode": symbol,
        }
        r = requests.post(self._rank_realtime_url, json=payload)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["data"])
        temp_df.columns = ["时间", "排名"]
        return temp_df


    def rank_latest(self,symbol: str = "SZ000665") -> pd.DataFrame:
        """
        东方财富-个股人气榜-最新排名
        https://guba.eastmoney.com/rank/stock?code=000665
        :param symbol: 带市场表示的证券代码
        :type symbol: str
        :return: 最新排名
        :rtype: pandas.DataFrame
        """
        payload = {
            "appId": "appId01",
            "globalId": "786e4c21-70dc-435a-93bb-38",
            "marketType": "",
            "srcSecurityCode": symbol,
        }
        response = requests.post(self._rand_latest_url, json=payload)
        data_json = response.json()
        temp_df = pd.DataFrame.from_dict(data_json["data"], orient="index")
        temp_df.reset_index(inplace=True)
        temp_df.columns = ["item", "value"]
        return temp_df


