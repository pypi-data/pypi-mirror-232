"""
Date: 2023/2/20 14:38
Desc: 日出和日落数据
https://www.timeanddate.com
"""
import pandas as pd
import pypinyin
import requests
from datetime import datetime


class SunRise:

    def __init__(self):
        self.city_avaliable_url = "https://www.timeanddate.com/astronomy/china"
        self.daily_url = "https://www.timeanddate.com/sun/china/{}?month={}&year={}"
        self.monthly_url = "https://www.timeanddate.com/sun/china/{}?month={}&year={}"
        self._city_avaliable()

    def _city_avaliable(self) -> list:
        """
        查询日出与日落数据的城市列表
        https://www.timeanddate.com/astronomy/china
        :return: 所有可以获取的数据的城市列表
        :rtype: list
        """
        self.avaliable_citys = []
        response = requests.get(self.city_avaliable_url)
        data_pd = pd.read_html(response.text)
        self.avaliable_citys.extend([item.lower() for item in data_pd[1].iloc[:, 0].tolist()])
        self.avaliable_citys.extend([item.lower() for item in data_pd[1].iloc[:, 3].tolist()])
        self.avaliable_citys.extend([item.lower() for item in data_pd[1].iloc[:, 6].tolist()])

        self.avaliable_citys.extend([item.lower() for item in data_pd[2].iloc[:, 0].tolist()])
        self.avaliable_citys.extend([item.lower() for item in data_pd[2].iloc[:, 1].tolist()])
        self.avaliable_citys.extend([item.lower() for item in data_pd[2].iloc[:, 2].tolist()])
        self.avaliable_citys.extend([item.lower() for item in data_pd[2].iloc[:, 3].tolist()])
        self.avaliable_citys.extend([item.lower() for item in data_pd[2].iloc[:, 4].dropna().tolist()])


    def daily(self,dt: datetime = datetime(2023,8,14), city: str = "北京") -> pd.DataFrame:
        """
        每日日出日落数据
        https://www.timeanddate.com/astronomy/china/shaoxing

        :param dt: 需要查询的日期, e.g., datetime(2023,8,14)
        :type dt: datetime
        :param city: 需要查询的城市; 注意输入的格式, e.g., "北京", "上海"
        :type city: str
        :return: 返回指定日期指定地区的日出日落数据
        :rtype: pandas.DataFrame
        """
        if pypinyin.slug(city, separator='') in self.avaliable_citys:
            url = self.daily_url.format(pypinyin.slug(city, separator=''), dt.month, dt.year)
            response = requests.get(url)
            data_pd = pd.read_html(response.text, header=2)[1]
            month_df = data_pd.iloc[:-1, ]

            date = dt.strftime("%Y%m%d")
            day_df = month_df[month_df.iloc[:, 0].astype(str).str.zfill(2) == str(dt.day)].copy()
            day_df.index = pd.to_datetime([date] * len(day_df), format="%Y%m%d")
            day_df.reset_index(inplace=True)
            day_df.rename(columns={"index": "date"}, inplace=True)
            day_df['date'] = pd.to_datetime(day_df['date']).dt.date
            return day_df
        else:
            return "请输入正确的城市名称"


    def monthly(self,dt: datetime = datetime(2023,8,14), city: str = "北京") -> pd.DataFrame:
        """
        每个指定 date 所在月份的每日日出日落数据, 如果当前月份未到月底, 则以预测值填充
        https://www.timeanddate.com/astronomy/china/shaoxing
        :param dt: 需要查询的日期, 这里用来指定 date 所在的月份; e.g., datetime(2023,8,14)
        :type date: datetime
        :param city: 需要查询的城市; 注意输入的格式, e.g., "北京", "上海"
        :type city: str
        :return: 指定 date 所在月份的每日日出日落数据
        :rtype: pandas.DataFrame
        """
        if pypinyin.slug(city, separator='') in self.avaliable_citys:
            url = self.monthly_url.format(pypinyin.slug(city, separator=''),dt.month,dt.year)
            response = requests.get(url)
            data_pd = pd.read_html(response.text, header=2)[1]

            date = dt.strftime("%Y%m%d")
            month_df = data_pd.iloc[:-1, ].copy()
            month_df.index = [date[:-2]] * len(month_df)
            month_df.reset_index(inplace=True)
            month_df.rename(columns={"index": "date", }, inplace=True)
            return month_df
        else:
            return "请输入正确的城市名称"


if __name__ == "__main__":

    sunrise = SunRise()
    sunrise_daily_df = sunrise.daily( city="北京")
    print(sunrise_daily_df)

    sunrise_monthly_df = sunrise.monthly(city="北京")
    print(sunrise_monthly_df)