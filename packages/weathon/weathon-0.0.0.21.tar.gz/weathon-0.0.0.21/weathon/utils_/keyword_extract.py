# -*- coding: utf-8 -*-
# @Time    : 2023/1/14 09:33
# @Author  : LiZhen
# @FileName: keyword_extract.py
# @github  : https://github.com/Lizhen0628
# @Description:


from collections import defaultdict
from operator import itemgetter
from typing import List, Set, Dict

import jieba.analyse
import jieba.posseg
import networkx as nx
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from weathon.dl.utils.dictionary import Dictionary
from weathon.dl.utils.string_utils import StringUtils


class KeywordExtractor:

    def __init__(self, stop_words: Set[str] = None, delim_words: Set[str] = None,
                 allow_pos: Set[str] = frozenset({'n', 'ns', 'nr', 'nt', 'nz', 'vn', 'v', 'an', 'a', 'i'}),
                 with_flag=False, with_weight=False, graph_weight=False):
        """
        关键词提取 基类
        Args:
            stop_words: 停用词表
            allow_pos: 允许的词性
            with_flag: 是否返回关键词的词性
            with_weight: 是否返回关键词的权重
            graph_weight: （textrank）构建图权重
        """

        self.tokenizer = jieba.posseg.dt
        self.stop_words = self._init_stop_words(stop_words)
        self.delim_words = self._init_delim_words(delim_words)

        self.allow_pos = allow_pos
        self.with_flag = with_flag
        self.with_weight = with_weight
        self.graph_weight = graph_weight

    def _init_stop_words(self, stop_words: Set[str]) -> Set[str]:
        """
        初始化停用词表
        Args:
            stop_words: 用户新增停用词
        Returns:
        """
        stop_words_dic = Dictionary.stopwords()
        if isinstance(stop_words, set):
            stop_words_dic |= stop_words
        return stop_words_dic

    def _init_delim_words(self, delim_words: Set[str]) -> Set[str]:
        delim_words_dic = Dictionary.delim_words()
        if isinstance(delim_words, set):
            delim_words_dic |= delim_words
        return delim_words_dic

    def _sentence_process(self, sentence: str) -> List:
        """
        根据词性、停用词对分词后的结果进行过滤
        Args:
            sentence: 原始句子
        Returns:
        """
        words = self.tokenizer.cut(sentence)
        words = [w for w in words if w.flag in self.allow_pos]
        words = [w for w in words if len(w.word) > 1 and w.word not in self.stop_words] if self.allow_pos else words
        return words

    def extract(self, **kwargs):
        pass


class TFIDF(KeywordExtractor):
    """
    TF-IDF算法思想:
        词频（Term Frequency，TF）指某一给定词语在当前文件中出现的频率。由于同一个词语在长文件中可能比短文件有更高的词频，因此根据文件的长度，需要对给定词语进行归一化，即用给定词语的次数除以当前文件的总词数。
        逆向文件频率（Inverse Document Frequency，IDF）是一个词语普遍重要性的度量。即如果一个词语只在很少的文件中出现，表示更能代表文件的主旨，它的权重也就越大；如果一个词在大量文件中都出现，表示不清楚代表什么内容，它的权重就应该小。
        TF-IDF的主要思想是，如果某个词语在一篇文章中出现的频率高，并且在其他文章中较少出现，则认为该词语能较好的代表当前文章的含义。即一个词语的重要性与它在文档中出现的次数成正比，与它在语料库中文档出现的频率成反比。

    由以上可知，TF-IDF是对文本所有候选关键词进行加权处理，根据权值对关键词进行排序。假设D_n为测试语料的大小，该算法的关键词抽取步骤如下所示：
        （1） 对于给定的文本D进行分词、词性标注和去除停用词等数据预处理操作。本分采用结巴分词，保留'n','nz','v','vd','vn','l','a','d'这几个词性的词语，最终得到n个候选关键词，即D=[t1,t2,…,tn]  ；
        （2） 计算词语t_i 在文本D中的词频；
        （3） 计算词语t_i 在整个语料的IDF=log (D_n /(D_t +1))，D_t 为语料库中词语t_i 出现的文档个数；
        （4） 计算得到词语t_i的TF-IDF=TF*IDF，并重复（2）—（4）得到所有候选关键词的TF-IDF数值；
        （5） 对候选关键词计算结果进行倒序排列，得到排名前TopN个词汇作为文本关键词。
    """

    def _load_idf(self):
        idf_freq = Dictionary.jieba_idf()
        median_idf = sorted(idf_freq.values())[len(idf_freq) // 2]
        return idf_freq, median_idf

    def multi_documents_extract_keywords(self, documents, top_k=5) -> List:
        word_pos_dic = defaultdict()
        corpus = []
        for document in documents:
            doc_words = self._sentence_process(document)
            words = []
            for w in doc_words:
                word_pos_dic[w.word] = w.flag
                words.append(w.word)
            corpus.append(" ".join(words))

        # 1、构建词频矩阵，将文本中的词语转换成词频矩阵
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(corpus)  # 词频矩阵, a[i][j]:表示第i个document中第j个词的词频

        # 2、统计每个词频的tf-idf权值
        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(X)

        # 3、获取词袋模型中的关键词
        word = vectorizer.get_feature_names_out()

        # 4、获取tf-idf矩阵,a[i][j]表示在第i个document中第j个词的tf-idf权值
        weight = tfidf.toarray()

        # 5、获取结果
        result = []
        for i in range(len(weight)):
            datas = []
            for j in range(len(word)):
                datas.append({
                    "word": word[j],
                    "weight": weight[i][j]
                })
            word_weight = pd.DataFrame(datas)  # 词汇和权重列表
            word_weight.sort_values(by="weight", ascending=False, inplace=True)  # 按照权重降序排序
            word_weight = word_weight.iloc[:top_k]
            if self.with_weight and self.with_weight:
                result.append(
                    [((row["word"], word_pos_dic[row["word"]]), row["weight"]) for _, row in word_weight.iterrows()])
            elif not self.with_flag and self.with_weight:
                result.append([(row["word"], row["weight"]) for _, row in word_weight.iterrows()])
            elif self.with_flag and self.with_weight:
                result.append([(row["word"], word_pos_dic[row["word"]]) for _, row in word_weight.iterrows()])
            else:
                result.append([row["word"] for _, row in word_weight.iterrows()])
            return result

    def single_document_extract_keywords(self, document, top_k=5) -> List:
        # 1. calculate tf : word freq
        freq = defaultdict(float)
        words = self._sentence_process(document)
        for w in words:
            freq[w] = freq.get(w, 0.) + 1.
        total = sum(freq.values())

        # 2. load idf
        idf_freq, median_idf = self._load_idf()

        # 3. calculate tfidf
        tfidf = defaultdict(float)
        for k in freq:
            kw = k.word if self.allow_pos else k
            tfidf[k] = freq[k] * idf_freq.get(kw, median_idf) / total

        # 4. result
        keywords = sorted(tfidf.items(), key=itemgetter(1), reverse=True)

        if self.with_flag and self.with_weight:
            return keywords[:top_k]
        elif not self.with_flag and self.with_weight:
            return [(kw[0].word, kw[1]) for kw in keywords[:top_k]]
        elif self.with_flag and not self.with_weight:
            return [kw[0] for kw in keywords[:top_k]]
        else:
            return [kw[0].word for kw in keywords[:top_k]]

    def extract(self, documents, top_k=5):
        return self.single_document_extract_keywords(documents, top_k) if isinstance(documents,
                                                                                     str) else self.multi_documents_extract_keywords(
            documents, top_k)


class TextRank(KeywordExtractor):
    """
    TextRank算法是Mihalcea和Tarau于2004年在研究自动摘要提取过程中所提出来的，在PageRank算法的思路上做了改进。该算法把文本拆分成词汇作为网络节点，组成词汇网络图模型，将词语间的相似关系看成是一种推荐或投票关系，使其可以计算每一个词语的重要性。
    基于TextRank的文本关键词抽取是利用局部词汇关系，即共现窗口，对候选关键词进行排序，该方法的步骤如下：
    （1） 对于给定的文本D进行分词、词性标注和去除停用词等数据预处理操作。本分采用结巴分词，保留'n','nz','v','vd','vn','l','a','d'这几个词性的词语，最终得到n个候选关键词，即D=[t1,t2,…,tn] ；
    （2） 构建候选关键词图G=(V,E)，其中V为节点集，由候选关键词组成，并采用共现关系构造任两点之间的边，两个节点之间仅当它们对应的词汇在长度为K的窗口中共现则存在边，K表示窗口大小即最多共现K个词汇；
    （3） 根据公式迭代计算各节点的权重，直至收敛；
    （4） 对节点权重进行倒序排列，得到排名前TopN个词汇作为文本关键词。
    """

    def combine(self, word_list: List[str], window: int = 2):
        """
        构造在window下的单词组合， 用来构造单词之间的边
        Args:
            word_list: 由单词组成的列表
            window: 窗口大小
        Returns:
        """
        window = 2 if window < 2 else window
        for x in range(1, window):
            if x >= len(word_list):
                break
            word_list2 = word_list[x:]
            for r in zip(word_list, word_list2):
                yield r

    def _build_graph(self, u, v, G: nx.Graph):
        if not self.graph_weight:
            G.add_edge(u, v)
        else:
            if G.has_edge(u, v):
                G[u][v]['weight'] += 1
            else:
                G.add_edge(u, v, weight=1)

    def extract(self, document, top_k, window: int = 2):
        """

        Args:
            document:
            top_k:
            window:
        Returns:
        """
        G = nx.Graph()
        doc_words = self._sentence_process(document)
        for u, v in self.combine(doc_words, window):
            self._build_graph(u, v, G)

        nodes = nx.pagerank(G)
        node_sorted = sorted(nodes.items(), key=itemgetter(1), reverse=True)
        if self.with_flag and self.with_weight:
            return node_sorted[:top_k]
        elif not self.with_flag and self.with_weight:
            return [(node[0].word, node[1]) for node in node_sorted[:top_k]]
        elif self.with_flag and not self.with_weight:
            return [node[0] for node in node_sorted[:top_k]]
        else:
            return [node[0].word for node in node_sorted[:top_k]]


class Word():
    def __init__(self, char, freq=0, deg=0):
        self.freq = freq
        self.deg = deg
        self.char = char

    def returnScore(self):
        return self.deg / self.freq

    def updateOccur(self, phraseLength):
        self.freq += 1
        self.deg += phraseLength

    def getChar(self):
        return self.char

    def updateFreq(self):
        self.freq += 1

    def getFreq(self):
        return self.freq


class Rake(KeywordExtractor):

    def extract(self, text: str, top_k: int = 5):
        # 1. tokenize words
        raw_word_list = self.tokenizer.cut(text)
        # 2. Construct List of Phrases and Preliminary textList
        last_word = ''
        text_list = []
        meaning_count = 0
        single_word_list = dict()
        for word, pos in raw_word_list:
            if word in self.delim_words or pos in ['m', 'x', 'uj', 'ul', 'mq', 'u', 'v',
                                                   'f'] or StringUtils.is_number_string(word) or word == '\n':
                if last_word != '|':
                    text_list.append('|')
                    last_word = '|'
            elif word not in self.stop_words and word != '\n':
                text_list.append(word)
                meaning_count += 1
                if word not in single_word_list:
                    single_word_list[word] = Word(word)
                last_word = ''

        # 3. Construct List of list that has phrases as wrds
        newList = []
        tempList = []

        news = []
        temp = []
        for word in text_list:
            if word != '|':
                temp.append(word)
            else:
                news.append(temp)
                temp = []

        temp_str = ''
        for word in text_list:
            if word != '|':
                temp_str += word + '|'
            else:
                if temp_str[:-1] not in single_word_list:
                    single_word_list[temp_str[:-1]] = Word(temp_str[:-1])
                    temp_str = ''

        # 4. Update the entire List
        for phrase in news:
            res = ''
            for word in phrase:
                single_word_list[word].updateOccur(len(phrase))
                res += word + '|'
            phrase_key = res[:-1]
            if phrase_key not in single_word_list:
                single_word_list[phrase_key] = Word(phrase_key)
            else:
                single_word_list[phrase_key].updateFreq()

        # 5. Get score for entire Set
        result = dict()
        for phrase in news:
            if len(phrase) > 5:
                continue
            score = 0
            phrase_str = ''
            out_str = ''
            for word in phrase:
                score += single_word_list[word].returnScore()
                phrase_str += word + '|'
                out_str += word
            phrase_key = phrase_str[:-1]
            freq = single_word_list[phrase_key].getFreq()
            if freq / meaning_count < 0.01 and freq < 3:
                continue
            result[out_str] = score
        sorted_list = sorted(result.items(), key=itemgetter(1), reverse=True)[:top_k]

        if self.with_weight:
            return sorted_list
        else:
            return [item[0] for item in sorted_list]


if __name__ == '__main__':
    docs = [
        "永磁电机驱动的纯电动大巴车坡道起步防溜策略,本发明公开了一种永磁电机驱动的纯电动大巴车坡道起步防溜策略，即本策略当制动踏板已踩下、永磁电机转速小于设定值并持续一定时间，整车控制单元产生一个刹车触发信号，当油门踏板开度小于设定值，且档位装置为非空档时，电机控制单元产生一个防溜功能使能信号并自动进入防溜控制使永磁电机进入转速闭环控制于某个目标转速，若整车控制单元检测到制动踏板仍然踩下，则限制永磁电机输出力矩，否则，恢复永磁电机输出力矩；当整车控制单元检测到油门踏板开度大于设置值、档位装置为空档或手刹装置处于驻车位置，则退出防溜控制，同时切换到力矩控制。本策略无需更改现有车辆结构或添加辅助传感器等硬件设备，实现车辆防溜目的。",
        "机动车辆车门的肘靠,一种溃缩结构是作为内部支撑件而被提供在机动车辆的车门衬板上的肘靠中，所述溃缩结构具有多个以交叉形方式设计的凹陷，其中被一个装饰层覆盖的一个泡沫元件安排在所述溃缩结构上方。该溃缩结构特别用于吸收侧面碰撞事件中的负荷，以便防止车辆乘车者免受增加的力峰值。",
        "仪表板支撑结构,本发明公开了一种支撑结构，其配置用于在车辆的乘客车厢内定位仪表板。所述支撑结构包括支撑支架和端部支架。所述支撑支架附接到所述车辆的车身面板。所述支撑支架包括横向偏压导引件。所述端部支架附接到所述仪表板的一端。所述端部支架具有第一侧面。所述第一侧面邻接所述支撑支架的横向偏压导引件，以使得所述横向偏压导引件沿横向方向偏压所述仪表板，直到所述端部支架邻接所述第一车身面板的横向基准表面。",
        "铰接的头枕总成,一种车辆座椅总成，包括座椅靠背、头枕和支承结构，支承结构在头枕和座椅靠背之间延伸。支承结构包括主要构件、次要构件和包围主要和次要构件的装饰件。主要构件与头枕和座椅靠背枢转地联接。次要构件具有上端和下端。上端围绕着横轴线与头枕枢转地联接并且与主要构件间隔开。第一驱动器在主要构件和座椅靠背之间与二者联接，以在后部位置和前部位置之间旋转头枕。第二驱动器联接在次要构件的下端和座椅靠背之间，以在第一角度和第二角度之间移动头枕。",
        "用于评估和控制电池系统的系统和方法,本发明涉及用于评估和控制电池系统的系统和方法。介绍了用于估计电池系统中的各独立电池分部的相对容量的系统和方法。在一些实施例中，系统可包括构造成分析电参数的计算系统，以产生在一段时间期间的参数的导数值。计算系统还可基于导数值计算与独立的电池分部相关联的总和值。电池控制系统可利用总和值，以产生构造成利用总和值控制电池组的操作的一个方面的一个或多个命令。根据一些实施例，与电池分部相关联的总和值可用于确定用于存储电能的相对容量。相对容量的确定可由控制系统使用，以防止具有最低储能容量的电池分部的过放电。",
        "侧气囊装置,本发明公开了一种侧气囊装置，其中，横向分隔件由一对结构织物部形成，各结构织物部具有第一周边部和第二周边部。结构织物部的第一周边部各自与主体织物部之一结合。由沿第二周边部设置的结合部，使结构织物部的第二周边部互相结合。内管延伸越过上膨胀室和下膨胀室，同时与横向分隔件相交。由周边结合部的一部分，使内管一部分的后周边部与主体织物部结合，以及，由结合部使该部分的前周边部与结构织物部结合。",
        "制造气囊的方法,本发明公开了以下方式制造气囊。在第一结合步骤中，使各结构织物部中安装时被引到更靠近于主体织物部的周边部与摊开状态下的主体织物部结合。在第二结合步骤中，使没有重叠到结构织物部上的部分与主体织物部结合，以及，使重叠到结构织物部上的部分只与结构织物部结合。在第三结合步骤中，使结构织物部中在安装时远离主体织物部的周边部互相结合。",
        "上部椅背枢轴系统,一种车辆座椅总成，其包括第一和第二侧支承部，该第一和第二侧支承部限定了椅背结构，该椅背结构在竖直和斜倚位置之间可操作。一机动化的驱动总成被设置在第一和第二侧支承部之间并可操作地耦接至枢轴杆，该枢轴杆与椅背结构可旋转地耦接。一上部椅背悬挂组件被耦接至枢轴杆。当椅背结构处在竖直位置时，该上部椅背悬挂组件相对于枢轴杆自动地向后部向位置枢转，且当该椅背结构处在斜倚位置时，该上部椅背悬挂组件相对于枢轴杆自动地向前部向位置枢转。一种外周间隙被限定在上部椅背悬挂组件和椅背结构之间。",
        "用于在机动车的行驶过程中关闭和启动内燃机的方法,本发明描述了一种用于在具有手动变速器(33)的机动车(32)的行驶过程中关闭和开启内燃机(31)的方法，该方法具有以下方法步骤：首先在机动车速度&gt;0且满足在手动变速器中的空挡条件时开始所述方法。随后关闭机动车(32)的内燃机(31)。之后在内燃机停转状态下的无驱动运行模式下继续行驶。在内燃机的停转状态下监测启动发生器(34)，并在启动信号发生器(34)被操作时开始重启内燃机(31)。",
        "半倾斜货箱卸载系统,本发明涉及半倾斜货箱卸载系统。一变型可包括一种产品，包括：运输工具，其包括具有倾斜部分和非倾斜部分的货箱，该运输工具具有第一纵向侧和相对的第二纵向侧，倾斜部分被构造和布置成使其最靠近第二纵向侧的一侧可相对于其最靠近第一纵向侧的相对侧降低。一变型可包括一种方法，包括：提供包括具有倾斜部分和非倾斜部分的货箱的运输工具，该运输工具具有第一纵向侧和相对的第二纵向侧，倾斜部分被构造和布置成使其最靠近第二纵向侧的一侧可相对于其最靠近第一纵向侧的相对侧降低，货箱具有前部和后部，倾斜部分最靠近货箱的前部，非倾斜部分邻近倾斜部分；将货物从货箱的后部装载到货箱上；以及将货物从货箱卸载，包括使货箱的倾斜部分倾斜。"
    ]
    tr = TextRank()
    tfidf = TFIDF()
    rake = Rake()
    for doc in docs:
        print(tr.extract(doc, top_k=3, window=3), tfidf.extract(doc, top_k=3),rake.extract(doc, top_k=3))
