"""
Date: 2023/2/19 19:00
Desc: 股票基本信息
"""
import json
import warnings
from io import BytesIO
from functools import lru_cache

import pandas as pd
import requests
from tqdm import tqdm




class StockInfo:

    def sz_name_code(self,symbol: str = "A股列表") -> pd.DataFrame:
        """
        深圳证券交易所-股票列表
        http://www.szse.cn/market/product/stock/list/index.html
        :param symbol: choice of {"A股列表", "B股列表", "CDR列表", "AB股列表"}
        :type symbol: str
        :return: 指定 indicator 的数据
        :rtype: pandas.DataFrame
        """
        url = "http://www.szse.cn/api/report/ShowReport"
        indicator_map = {
            "A股列表": "tab1",
            "B股列表": "tab2",
            "CDR列表": "tab3",
            "AB股列表": "tab4",
        }
        
        assert symbol in indicator_map, f"{symbol} not in [{indicator_map.keys()}]"
        params = {
            "SHOWTYPE": "xlsx",
            "CATALOGID": "1110",
            "TABKEY": indicator_map[symbol],
            "random": "0.6935816432433362",
        }
        response = requests.get(url, params=params)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            temp_df = pd.read_excel(BytesIO(response.content))
        if len(temp_df) > 10:
            if symbol == "A股列表":
                temp_df["A股代码"] = (temp_df["A股代码"].astype(str).str.split(".", expand=True)
                    .iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
                temp_df = temp_df[["板块","A股代码","A股简称","A股上市日期","A股总股本","A股流通股本","所属行业", ]]
            elif symbol == "B股列表":
                temp_df["B股代码"] = (
                    temp_df["B股代码"].astype(str).str.split(".", expand=True)
                    .iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
                temp_df = temp_df[["板块","B股代码","B股简称","B股上市日期","B股总股本","B股流通股本","所属行业",]]
            elif symbol == "AB股列表":
                temp_df["A股代码"] = (temp_df["A股代码"].astype(str).str.split(".", expand=True)
                    .iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
                temp_df["B股代码"] = (temp_df["B股代码"].astype(str).str.split(".", expand=True)
                    .iloc[:, 0].str.zfill(6).str.replace("000nan", ""))
                temp_df = temp_df[["板块","A股代码","A股简称","A股上市日期","B股代码","B股简称", "B股上市日期","所属行业",]]
        
        return temp_df

    def sh_name_code(self,symbol: str = "主板A股") -> pd.DataFrame:
        """
        上海证券交易所-股票列表
        http://www.sse.com.cn/assortment/stock/list/share/
        :param symbol: choice of {"主板A股": "1", "主板B股": "2", "科创板": "8"}
        :type symbol: str
        :return: 指定 indicator 的数据
        :rtype: pandas.DataFrame
        """
        indicator_map = {"主板A股": "1", "主板B股": "2", "科创板": "8"}
        url = "http://query.sse.com.cn/sseQuery/commonQuery.do"
        headers = {
            "Host": "query.sse.com.cn",
            "Pragma": "no-cache",
            "Referer": "http://www.sse.com.cn/assortment/stock/list/share/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        }
        params = {
            "STOCK_TYPE": indicator_map[symbol],
            "REG_PROVINCE": "",
            "CSRC_CODE": "",
            "STOCK_CODE": "",
            "sqlId": "COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L",
            "COMPANY_STATUS": "2,4,5,7,8",
            "type": "inParams",
            "isPagination": "true",
            "pageHelp.cacheSize": "1",
            "pageHelp.beginPage": "1",
            "pageHelp.pageSize": "10000",
            "pageHelp.pageNo": "1",
            "pageHelp.endPage": "1",
            "_": "1653291270045",
        }
        r = requests.get(url, params=params, headers=headers)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["result"])
        col_stock_code = "B_STOCK_CODE" if symbol == "主板B股" else "A_STOCK_CODE"
        temp_df.rename(columns={
            col_stock_code: "证券代码",
            "COMPANY_ABBR": "证券简称",
            "FULL_NAME": "公司全称",
            "LIST_DATE": "上市日期",
        }, inplace=True)
        temp_df = temp_df[["证券代码","证券简称", "公司全称","上市日期",]]
        temp_df["上市日期"] = pd.to_datetime(temp_df["上市日期"]).dt.date
        return temp_df
    
    def bj_name_code(self) -> pd.DataFrame:
        """
        北京证券交易所-股票列表
        https://www.bse.cn/nq/listedcompany.html
        :return: 股票列表
        :rtype: pandas.DataFrame
        """
        url = "https://www.bse.cn/nqxxController/nqxxCnzq.do"
        payload = {
            "page": "0",
            "typejb": "T",
            "xxfcbj[]": "2",
            "xxzqdm": "",
            "sortfield": "xxzqdm",
            "sorttype": "asc",
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        r = requests.post(url, data=payload, headers=headers)
        data_text = r.text
        data_json = json.loads(data_text[data_text.find("[") : -1])
        total_page = data_json[0]["totalPages"]
        big_df = pd.DataFrame()
        for page in tqdm(range(total_page), leave=False):
            payload.update({"page": page})
            r = requests.post(url, data=payload, headers=headers)
            data_text = r.text
            data_json = json.loads(data_text[data_text.find("[") : -1])
            temp_df = data_json[0]["content"]
            temp_df = pd.DataFrame(temp_df)
            big_df = pd.concat([big_df, temp_df], ignore_index=True)
        big_df.columns = [
            "上市日期",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "流通股本",
            "-",
            "-",
            "-",
            "-",
            "-",
            "所属行业",
            "-",
            "-",
            "-",
            "-",
            "报告日期",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "地区",
            "-",
            "-",
            "-",
            "-",
            "-",
            "券商",
            "总股本",
            "-",
            "证券代码",
            "-",
            "证券简称",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
        ]
        big_df = big_df[
            [
                "证券代码",
                "证券简称",
                "总股本",
                "流通股本",
                "上市日期",
                "所属行业",
                "地区",
                "报告日期",
            ]
        ]
        big_df["报告日期"] = pd.to_datetime(big_df["报告日期"]).dt.date
        big_df["上市日期"] = pd.to_datetime(big_df["上市日期"]).dt.date
        return big_df

    def sh_delist(self) -> pd.DataFrame:
        """
        上海证券交易所-终止上市公司
        http://www.sse.com.cn/assortment/stock/list/delisting/
        :return: 终止上市公司
        :rtype: pandas.DataFrame
        """
        url = "http://query.sse.com.cn/commonQuery.do"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "query.sse.com.cn",
            "Pragma": "no-cache",
            "Referer": "http://www.sse.com.cn/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        }
        params = {
            "sqlId": "COMMON_SSE_CP_GPJCTPZ_GPLB_GP_L",
            "isPagination": "true",
            "STOCK_CODE": "",
            "CSRC_CODE": "",
            "REG_PROVINCE": "",
            "STOCK_TYPE": "1,2",
            "COMPANY_STATUS": "3",
            "type": "inParams",
            "pageHelp.cacheSize": "1",
            "pageHelp.beginPage": "1",
            "pageHelp.pageSize": "500",
            "pageHelp.pageNo": "1",
            "pageHelp.endPage": "1",
            "_": "1643035608183",
        }
        r = requests.get(url, params=params, headers=headers)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json["result"])
        temp_df.rename(columns={
            "COMPANY_ABBR": "公司简称",
            "DELIST_DATE": "暂停上市日期",
            "LIST_DATE": "上市日期",
            "COMPANY_CODE": "公司代码",
        }, inplace=True)
        temp_df = temp_df[
            [
                "公司代码",
                "公司简称",
                "上市日期",
                "暂停上市日期",
            ]
        ]
        temp_df["上市日期"] = pd.to_datetime(temp_df["上市日期"]).dt.date
        temp_df["暂停上市日期"] = pd.to_datetime(temp_df["暂停上市日期"]).dt.date
        return temp_df


    def sz_delist(self,symbol: str = "暂停上市公司") -> pd.DataFrame:
        """
        深证证券交易所-暂停上市公司-终止上市公司
        http://www.szse.cn/market/stock/suspend/index.html
        :param symbol: choice of {"暂停上市公司", "终止上市公司"}
        :type symbol: str
        :return: 暂停上市公司 or 终止上市公司 的数据
        :rtype: pandas.DataFrame
        """
        indicator_map = {"暂停上市公司": "tab1", "终止上市公司": "tab2"}
        url = "http://www.szse.cn/api/report/ShowReport"
        params = {
            "SHOWTYPE": "xlsx",
            "CATALOGID": "1793_ssgs",
            "TABKEY": indicator_map[symbol],
            "random": "0.6935816432433362",
        }
        r = requests.get(url, params=params)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            temp_df = pd.read_excel(BytesIO(r.content))
            if temp_df.empty:
                return pd.DataFrame()
            temp_df["证券代码"] = temp_df["证券代码"].astype("str").str.zfill(6)
            temp_df['上市日期'] = pd.to_datetime(temp_df['上市日期']).dt.date
            temp_df['终止上市日期'] = pd.to_datetime(temp_df['终止上市日期']).dt.date
            return temp_df

    def sz_name_change(self,symbol: str = "全称变更") -> pd.DataFrame:
        """
        深证证券交易所-市场数据-股票数据-名称变更
        http://www.szse.cn/www/market/stock/changename/index.html
        :param symbol: choice of {"全称变更": "tab1", "简称变更": "tab2"}
        :type symbol: str
        :return: 名称变更数据
        :rtype: pandas.DataFrame
        """
        indicator_map = {"全称变更": "tab1", "简称变更": "tab2"}
        url = "http://www.szse.cn/api/report/ShowReport"
        params = {
            "SHOWTYPE": "xlsx",
            "CATALOGID": "SSGSGMXX",
            "TABKEY": indicator_map[symbol],
            "random": "0.6935816432433362",
        }
        r = requests.get(url, params=params)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            temp_df = pd.read_excel(BytesIO(r.content))
            temp_df["证券代码"] = temp_df["证券代码"].astype("str").str.zfill(6)
            temp_df['变更日期'] = pd.to_datetime(temp_df['变更日期']).dt.date
            temp_df.sort_values(['变更日期'], inplace=True, ignore_index=True)
            return temp_df
    
    def name_used(self,symbol: str = "000503") -> pd.DataFrame:
        """
        新浪财经-股票曾用名
        http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/300378.phtml
        :param symbol: 股票代码
        :type symbol: str
        :return: 股票曾用名
        :rtype: list
        """
        url = f"http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{symbol}.phtml"
        r = requests.get(url)
        temp_df = pd.read_html(r.text)[3].iloc[:, :2]
        temp_df.dropna(inplace=True)
        temp_df.columns = ["item", "value"]
        temp_df["item"] = temp_df["item"].str.split("：", expand=True)[0]
        try:
            name_list = (
                temp_df[temp_df["item"] == "证券简称更名历史"].value.tolist()[0].split(" ")
            )
            big_df = pd.DataFrame(name_list)
            big_df.reset_index(inplace=True)
            big_df["index"] = big_df.index + 1
            big_df.columns = ["index", "name"]
            return big_df
        except IndexError as e:
            return pd.DataFrame()



    @lru_cache()
    def a_code_name(self) -> pd.DataFrame:
        """
        沪深京 A 股列表
        :return: 沪深京 A 股数据
        :rtype: pandas.DataFrame
        """
        big_df = pd.DataFrame()
        stock_sh = self.sh_name_code(symbol="主板A股")
        stock_sh = stock_sh[["证券代码", "证券简称"]]

        stock_sz = self.sz_name_code(symbol="A股列表")
        stock_sz["A股代码"] = stock_sz["A股代码"].astype(str).str.zfill(6)
        
        big_df = pd.concat([big_df, stock_sz[["A股代码", "A股简称"]]], ignore_index=True)
        big_df.columns = ["证券代码", "证券简称"]

        stock_kcb = self.sh_name_code(symbol="科创板")
        stock_kcb = stock_kcb[["证券代码", "证券简称"]]

        stock_bse = self.bj_name_code()
        stock_bse = stock_bse[["证券代码", "证券简称"]]
        stock_bse.columns = ["证券代码", "证券简称"]

        big_df = pd.concat([big_df, stock_sh], ignore_index=True)
        big_df = pd.concat([big_df, stock_kcb], ignore_index=True)
        big_df = pd.concat([big_df, stock_bse], ignore_index=True)
        big_df.columns = ["code", "name"]
        return big_df



    @lru_cache()
    def code_id_map_em(self) -> dict:
        """
        东方财富-股票和市场代码
        https://quote.eastmoney.com/center/gridlist.html#hs_a_board
        :return: 股票和市场代码
        :rtype: dict
        """
        url = "http://80.push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1",
            "pz": "50000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:1 t:2,m:1 t:23",
            "fields": "f12",
            "_": "1623833739532",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        if not data_json["data"]["diff"]:
            return dict()
        temp_df = pd.DataFrame(data_json["data"]["diff"])
        temp_df["market_id"] = 1
        temp_df.columns = ["sh_code", "sh_id"]
        code_id_dict = dict(zip(temp_df["sh_code"], temp_df["sh_id"]))
        params = {
            "pn": "1",
            "pz": "50000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0 t:6,m:0 t:80",
            "fields": "f12",
            "_": "1623833739532",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        if not data_json["data"]["diff"]:
            return dict()
        temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
        temp_df_sz["sz_id"] = 0
        code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["sz_id"])))
        params = {
            "pn": "1",
            "pz": "50000",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": "m:0 t:81 s:2048",
            "fields": "f12",
            "_": "1623833739532",
        }
        r = requests.get(url, params=params)
        data_json = r.json()
        if not data_json["data"]["diff"]:
            return dict()
        temp_df_sz = pd.DataFrame(data_json["data"]["diff"])
        temp_df_sz["bj_id"] = 0
        code_id_dict.update(dict(zip(temp_df_sz["f12"], temp_df_sz["bj_id"])))
        return code_id_dict


    def individual_stock_info(self,symbol: str = "603777", timeout: float = None) -> pd.DataFrame:
        """
        东方财富-个股-股票信息
        https://quote.eastmoney.com/concept/sh603777.html?from=classic
        :param symbol: 股票代码
        :type symbol: str
        :param timeout: choice of None or a positive float number
        :type timeout: float
        :return: 股票信息
        :rtype: pandas.DataFrame
        """
        code_id_dict = self.code_id_map_em()
        url = "http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "fltt": "2",
            "invt": "2",
            "fields": "f120,f121,f122,f174,f175,f59,f163,f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f262,f263,f264,f267,f268,f255,f256,f257,f258,f127,f199,f128,f198,f259,f260,f261,f171,f277,f278,f279,f288,f152,f250,f251,f252,f253,f254,f269,f270,f271,f272,f273,f274,f275,f276,f265,f266,f289,f290,f286,f285,f292,f293,f294,f295",
            "secid": f"{code_id_dict[symbol]}.{symbol}",
            "_": "1640157544804",
        }
        r = requests.get(url, params=params, timeout=timeout)
        data_json = r.json()
        temp_df = pd.DataFrame(data_json)
        temp_df.reset_index(inplace=True)
        del temp_df["rc"]
        del temp_df["rt"]
        del temp_df["svr"]
        del temp_df["lt"]
        del temp_df["full"]
        code_name_map = {
            "f57": "股票代码",
            "f58": "股票简称",
            "f84": "总股本",
            "f85": "流通股",
            "f127": "行业",
            "f116": "总市值",
            "f117": "流通市值",
            "f189": "上市时间",
        }
        temp_df["index"] = temp_df["index"].map(code_name_map)
        temp_df = temp_df[pd.notna(temp_df["index"])]
        if "dlmkts" in temp_df.columns:
            del temp_df["dlmkts"]
        temp_df.columns = [
            "item",
            "value",
        ]
        temp_df.reset_index(inplace=True, drop=True)
        return temp_df