"""
Date: 2023/1/7 14:55
Desc: 历年世界 500 强榜单数据
https://www.fortunechina.com/fortune500/index.htm
特殊情况说明：
2010年由于网页端没有公布公司所属的国家, 故 2010 年数据没有国家这列
"""
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from functools import lru_cache
from tqdm import tqdm


