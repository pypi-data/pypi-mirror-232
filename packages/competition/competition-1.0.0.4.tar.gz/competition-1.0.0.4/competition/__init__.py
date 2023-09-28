import kquant as kq
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler
minmax_scalor = MinMaxScaler()

id = 'KRX2308037'
api = 'oqGu3tsY1WdAx4HpGIDIIr0rtEwsu62X'
kq.set_api(id, api)

def UNIVERSE(gubun) :
    '''
    분석 대상 유니버스 정의하는 함수
    : 한국거래소(유가증권시장 및 코스닥시장) 종목 중 시가총액이 1,000억원 이상인 종목 스크리닝

    :return : 분석대상 유니버스
    :rtype : dataframe
    '''
    code = kq.symbol_stock()
    code_tgt = code[(code.SEC_TYPE == 'ST') & (~code.ADMIN_ISSUE.isin([20, 21, 22, 30, 40, 50, 60, 61, 70])) & \
                    (~code.NAME_EN.str.contains('(1P)|(2PB)')) & (~code.SYMBOL.str.contains('K'))]
    mkt = kq.rank_stocks('MARKETCAP')
    code_tgt = code_tgt.merge(mkt[['SYMBOL','MARKETCAP']], on ='SYMBOL', how = 'inner')
    if gubun == 'mix' :
        universe = code_tgt[code_tgt.MARKETCAP >= 140000000000].reset_index(drop=True)
        universe = universe[code_tgt.MARKETCAP <= 10000000000000].reset_index(drop=True)
        universe = universe[~(code_tgt.NAME.str.contains('은행|금융|증권|보험|전력|가스|에너지|난방'))]
    elif gubun == 'dur' :
        universe = code_tgt[code_tgt.MARKETCAP >= 200000000000].reset_index(drop=True)
    elif gubun == 'all':
        universe = code_tgt[code_tgt.MARKETCAP >= 100000000000].reset_index(drop=True)
    return universe

def DATAS(TARGET, TICKERS, PERIOD, STDDATE) :
    '''
    종목별 일별 시장 정보 호출하는 함수
    : 분석 대상 유니버스의 일간 종가, 거래량, 거래대금 등 시장데이터를 호출

    :param TARGET: 호출하고자 하는 타깃 변수
                    (ex, 종가: 'CLOSE', 거래량 : 'VOLUME' 등)               (str)
    :param TICKERS: 분석 대상 종목의 티커                                    (list)
    :param PERIOD:  분석 대상 기간 (ex, 6개월: 6)                            (int)
    :param STDDATE: 기준일                                                 (str)

    :return : 종목별 일간 시장정보
    :rtype : dataframe
    '''
    ago = (datetime.strptime(STDDATE, '%Y%m%d') - relativedelta(months=PERIOD)).strftime('%Y%m%d')
    datas = pd.DataFrame()
    for i in range(0,len(TICKERS)) :
        try :
            temp = kq.daily_stock(TICKERS[i],ago, STDDATE)[['DATE',TARGET]].set_index('DATE').rename(columns = {TARGET:TICKERS[i]})
            datas = pd.concat([datas,temp], axis= 1)
            print(i, TICKERS[i])
        except :
            pass
    return datas

import datetime as dt
import logging
import pandas as pd


def trade_func(
    date: dt.date,
    dict_df_result: dict[str, pd.DataFrame],
    dict_df_position: dict[str, pd.DataFrame],
    logger: logging.Logger,
) -> list[tuple[str, int]]:
    r"""주식매매 지시함수

    주식매매 지시함수에 대한 설명

    :param dt.date date: 매매일 날짜
    :param dict[str, pd.DataFrame] dict_df_result: 매매일까지의 주문 및 체결 정보
    :param dict[str, pd.DataFrame] dict_df_position: 매매일의 주식 보유 정보
    :param logging.Logger logger: 로거
    :return list[tuple[str, int]]: 주식매매 지시
    """

    # 본 예제코드는 코드가 실제로 실행되는 것을 보여주기 위해
    # 심사 투자기간이 2023년 1월 2일부터 시작된다고 가정하고 있습니다.
    # 실제 제출코드에서는 실제 심사 투자기간을 사용해야 합니다.

    # 시가총액 상위 5개 주식
    symbols = [
        "005930",
        "373220",
        "000660",
        "207940",
        "005490",
    ]

    if date == dt.date(2023, 1, 2):  # 투자 시작일
        # 각 종목을 10주씩 매수
        symbols_and_orders = [
            (symbols[0], 10),
            (symbols[1], 10),
            (symbols[2], 10),
            (symbols[3], 10),
            (symbols[4], 10),
        ]
    elif date.weekday() == 1:  # 매주 화요일마다
        # 각 종목을 추가적으로 1주씩 매수
        symbols_and_orders = [
            (symbols[0], 1),
            (symbols[1], 1),
            (symbols[2], 1),
            (symbols[3], 1),
            (symbols[4], 1),
        ]
    else:
        symbols_and_orders = []

    return symbols_and_orders
