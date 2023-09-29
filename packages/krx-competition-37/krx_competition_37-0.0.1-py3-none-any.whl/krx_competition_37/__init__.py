import kquant as kq
import pandas as pd
import datetime as dt
import math
from dateutil.relativedelta import relativedelta
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler
import logging
minmax_scalor = MinMaxScaler()

def trade_func(
        date: dt.date,
        dict_df_result: dict[str, pd.DataFrame],
        dict_df_position: dict[str, pd.DataFrame],
        logger: logging.Logger,
    ) -> list[tuple[str, int]]:
    """
    주식매매 지시함수
    : 일자별 매수대상종목 선택하는 함수
     1) 종목별 주식 듀레이션을 산출하여 가치/성장/혼합주를 구분한다.
     2) 그룹별 재무제표 데이터를 이용하여 피쳐 스코어를 생성한다.
     3) 그룹별 5분위 Long-Short 포트폴리오의 수익률에 기반해 핵심 피쳐를 선정한다.
     4) 핵심 피쳐 가중 스코어를 바탕으로 그룹별 최종 투자종목을 선정한다.

    :param dt.date date: 매매일 날짜
    :param dict[str, pd.DataFrame] dict_df_result: 매매일까지의 주문 및 체결 정보
    :param dict[str, pd.DataFrame] dict_df_position: 매매일의 주식 보유 정보
    :param logging.Logger logger: 로거
    :return list[tuple[str, int]]: 주식매매 지시
    """

    def UNIVERSE(GUBUN):
        '''
        분석 대상 유니버스 정의하는 함수
        : 한국거래소(유가증권시장 및 코스닥시장) 종목 중 다음 조건을 만족하는 종목을 스크리닝 한다.
         1) 성장/가치주 : 시가총액이 2000억원 이상 포함
         2) 혼합주 : 시가총액이 1000억원 이상, 10조 이하 포함 & 금융/유틸리티 제외

        :return : 분석대상 유니버스
        :rtype : dataframe
        '''
        code = kq.symbol_stock()
        code_tgt = code[(code.SEC_TYPE == 'ST') & (~code.ADMIN_ISSUE.isin([20, 21, 22, 30, 40, 50, 60, 61, 70])) & \
                        (~code.NAME_EN.str.contains('(1P)|(2PB)')) & (~code.SYMBOL.str.contains('K'))]
        mkt = kq.rank_stocks('MARKETCAP')
        code_tgt = code_tgt.merge(mkt[['SYMBOL','MARKETCAP']], on ='SYMBOL', how = 'inner')
        if GUBUN == 'mix' :
            universe = code_tgt[code_tgt.MARKETCAP >= 140000000000].reset_index(drop=True)
            universe = universe[code_tgt.MARKETCAP <= 10000000000000].reset_index(drop=True)
            universe = universe[~(code_tgt.NAME.str.contains('은행|금융|증권|보험|전력|가스|에너지|난방'))]
        elif GUBUN == 'dur' :
            universe = code_tgt[code_tgt.MARKETCAP >= 200000000000].reset_index(drop=True)
        elif GUBUN == 'all':
            universe = code_tgt
        return universe

    def DATAS(TARGET, TICKERS, PERIOD, STDDATE) :
        '''
        기간별 시장 데이터 호출하는 함수
        : 분석 대상 종목의 기간별 종가, 거래량, 거래대금 등 시장데이터 호출

        :param TARGET: 호출하고자 하는 타깃 변수
                        (ex, 종가: 'CLOSE', 거래량 : 'VOLUME' 등)               (str)
        :param TICKERS: 분석 대상 종목의 티커리스트                               (list)
        :param PERIOD:  분석 대상 기간 (ex, 6개월: 6)                            (int)
        :param STDDATE: 기준일자                                                (str)

        :return : 기간별 시장 데이터
        :rtype : dataframe
        '''
        ago = (dt.date(int(STDDATE[0:4]), int(STDDATE[4:6]), int(STDDATE[6:8])) - relativedelta(months=PERIOD)).strftime('%Y%m%d')
        datas = pd.DataFrame()
        for i in range(0,len(TICKERS)) :
            try :
                temp = kq.daily_stock(TICKERS[i],ago, STDDATE)[['DATE',TARGET]].set_index('DATE').rename(columns = {TARGET:TICKERS[i]})
                datas = pd.concat([datas,temp], axis= 1)
                print(i, TICKERS[i])
            except :
                pass
        return datas

    def BETAS(TICKERS, PERIOD, STDDATE) :
        '''
        종목별 베타 산출하는 함수
        : 기간 내 종목별 일별수익률과 시장지수(KOSPI) 일별수익률간 회귀 분석으로 베타 산출

        :param TICKERS: 분석 대상 종목의 티커리스트                               (list)
        :param PERIOD: 분석 대상 기간 (ex, 6개월: 6)                            (int)
        :param STDDATE: 기준일                                                (str)
        :return: 종목별 베타
        :rtype: dataframe
        '''
        ago = (dt.date(int(STDDATE[0:4]), int(STDDATE[4:6]), int(STDDATE[6:8])) - relativedelta(months=PERIOD)).strftime('%Y%m%d')
        kospi = kq.daily_kospi_index("1",ago, STDDATE)[['DATE','CLOSE']].set_index('DATE').rename(columns = {'CLOSE':'KOSPI'})
        kospi = pd.DataFrame(kospi['KOSPI'].pct_change().dropna())
        kospi['INTERCEPT'] = 1
        prc = DATAS("CLOSE", TICKERS, PERIOD, STDDATE)
        prc = prc.pct_change()[1:].fillna(0).replace([np.inf, -np.inf], 0)
        betas = pd.DataFrame()
        for i in range(0,len(prc.columns)) :
            try :
                reg = sm.OLS(prc[prc.columns[i]], kospi[['KOSPI','INTERCEPT']]).fit()
                temp = pd.DataFrame({'SYMBOL' : prc.columns[i], 'BETA' : reg.params[0]}, index = [0])
                betas = pd.concat([betas, temp])
                print(i, prc.columns[i])
            except :
                pass
        betas = betas.reset_index(drop=True)
        return betas

    def STATS_FOR_DUR(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE) :
        '''
        주식 듀레이션 산출을 위한 기초 데이터 산출하는 함수
        : 종목의 베타, 시가총액, 전기현금흐름, 당기현금흐름, 성장률, 할인율 산출

        :param RISK_FREE: 무위험 수익률 (ex, 4%: 0.04)                        (float)
        :param MARKET_RATE: 시장 수익률 (ex, 7.5%, 0.075)                     (float)
        :param TICKERS: 분석 대상 종목의 티커리스트                              (list)
        :param PERIOD: 분석 대상 기간 (ex, 6개월: 6)                           (int)
        :param STDDATE: 조회종료일                                            (str)
        :return: 듀레이션 산출을 위한 기초 데이터
        :rtype : dataframe
        '''
        beta = BETAS(TICKERS, PERIOD, STDDATE)
        mkt = kq.rank_stocks('MARKETCAP')
        mktcap = mkt[mkt.SYMBOL.isin(mkt.SYMBOL)][['SYMBOL','NAME','MARKETCAP']]
        df = pd.DataFrame()
        for i in range(0, len(TICKERS)):
            try:
                temp_ni = kq.account_history(TICKERS[i], account_code="122700", period='q')  # 당기순이익
                temp_eq = kq.account_history(TICKERS[i], account_code="115000", period='q')  # 자본총계
                df = df.append({'SYMBOL': TICKERS[i]
                                , "NI_NOW" : temp_ni.VALUE[0:4].sum() * 1000
                                , "NI_PREV" : temp_ni.VALUE[1:5].sum() * 1000
                                , "CAP_NOW": temp_eq.VALUE[0:4].mean() * 1000
                                , "CAP_PREV": temp_eq.VALUE[1:5].mean() * 1000
                                , "CAP_PPREV": temp_eq.VALUE[2:6].mean() * 1000 }, ignore_index=True)
                print(i, TICKERS[i])
            except :
                pass
        df = df.dropna().merge(mktcap, on='SYMBOL', how='inner')
        df = df.merge(beta, on='SYMBOL', how='inner')
        df['CF_PREV'] = df['NI_PREV'] - (df['CAP_PREV'] - df['CAP_PPREV'])
        df['CF_NOW'] = df['NI_NOW'] - (df['CAP_NOW'] - df['CAP_PREV'])
        df['MARKETRATE'] = MARKET_RATE
        df['RATE'] = RISK_FREE + df['BETA'] * (df['MARKETRATE'] - RISK_FREE)
        df['GROWTH'] = df['RATE'] - ((df['CF_NOW'] / df['MARKETCAP']) / (1 + df['RATE'] - df['CF_PREV'] / df['MARKETCAP']))
        return df

    def STATS_FOR_MIX(TICKERS):
        '''
        혼합주의 기초 데이터 호출하는 함수
        : 혼합주의 순이익, 영업이익 호출

        :param TICKERS: 분석 대상 종목의 티커리스트                              (list)
        :return: 혼합주의 이익 데이터
        :rtype: dataframe
        '''
        df = pd.DataFrame()
        for i in range(0, len(TICKERS)):
            try :
                temp_ni = kq.account_history(TICKERS[i], account_code="140600", period='q')  # 당기순이익
                temp_ni_y = kq.account_history(TICKERS[i], account_code="140600", period='y')  # 당기순이익
                temp_oi = kq.account_history(TICKERS[i], account_code="121500", period='q')  # 영업이익
                temp_oi_y = kq.account_history(TICKERS[i], account_code="121500", period='y')  # 영업이익
                df = df.append({'SYMBOL': TICKERS[i]
                               , "NI_PREV_1Y": temp_ni_y.VALUE[0:1].sum() * 1000
                               , "NI_PREV_2Y": temp_ni_y.VALUE[0:1].sum() * 1000
                               , "NI_NOW": temp_ni.VALUE[0:4].sum() * 1000
                               , "NI_PREV": temp_ni.VALUE[1:5].sum() * 1000
                               , "OI_PREV_1Y": temp_oi_y.VALUE[0:1].sum() * 1000
                               , "OI_PREV_2Y":  temp_oi_y.VALUE[1:2].sum() * 1000
                               , "OI_NOW": temp_oi.VALUE[0:4].sum() * 1000
                               , "OI_PREV": temp_oi.VALUE[1:5].sum() * 1000}, ignore_index=True)
                print(i, TICKERS[i])
            except :
                pass
        return df

    def FEATURES(TICKERS):
        '''
        분석 대상 종목의 피쳐 산출하는 함수
        : 1)종목별 재무제표를 바탕으로 피쳐 데이터 산출
          2) Outlier 제거 후 MinMaxScaling 재실시

        :param TICKERS: 분석 대상 종목의 티커리스트                               (list)
        :return: 종목별 피쳐스코어
        :rtype : dataframe
        '''
        df = pd.DataFrame()
        for i in range(0, len(TICKERS)):
            try :
                temp_ni = kq.account_history(TICKERS[i], account_code="140600", period='q')  # 당기순이익
                temp_oi = kq.account_history(TICKERS[i], account_code="121500", period='q')  # 영업이익
                temp_rev = kq.account_history(TICKERS[i], account_code="121000", period='q')  # 매출액
                temp_fcf = kq.account_history(TICKERS[i], account_code="124150", period='q')  # FCF
                temp_ocf = kq.account_history(TICKERS[i], account_code="131000", period='q')  # 영업현금흐름
                temp_eq = kq.account_history(TICKERS[i], account_code="115000", period='q')  # 자본총계
                temp_lass = kq.account_history(TICKERS[i], account_code="111100", period='q')  # 유동자산
                temp_lia = kq.account_history(TICKERS[i], account_code="113000", period='q')  # 부채총계
                temp_gp = kq.account_history(TICKERS[i], account_code="121200", period='q')  # 매출총이익
                temp_ass = kq.account_history(TICKERS[i], account_code="111000", period='q')  # 자산총계
                temp_qty = kq.account_history(TICKERS[i], account_code="702200", period='q')  # 주식수
                temp_dps = kq.account_history(TICKERS[i], account_code="423200", period='q')  # 수정DPS
                df = df.append({'SYMBOL': TICKERS[i]
                               , "NI_NOW": temp_ni.VALUE[0:4].sum() * 1000
                               , "NI_PREV": temp_ni.VALUE[1:5].sum() * 1000
                               , "OI_NOW": temp_oi.VALUE[0:4].sum() * 1000
                               , "OI_PREV": temp_oi.VALUE[1:5].sum() * 1000
                               , "REV_NOW": temp_rev.VALUE[0:4].sum() * 1000
                               , "REV_PREV": temp_rev.VALUE[1:5].sum() * 1000
                               , "FCF_NOW": temp_fcf.VALUE[0:4].sum() * 1000
                               , "FCF_PREV": temp_fcf.VALUE[1:5].sum() * 1000
                               , "OCF_NOW": temp_ocf.VALUE[0:4].sum() * 1000
                               , "EQ_NOW": temp_eq.VALUE[0:4].mean() * 1000
                               , "LASS_NOW": temp_lass.VALUE[0:4].mean() * 1000
                               , "LIA_NOW": temp_lia.VALUE[0:4].mean() * 1000
                               , "GP_NOW": temp_gp.VALUE[0:4].sum() * 1000
                               , "ASS_NOW": temp_ass.VALUE[0:4].mean() * 1000
                               , "QTY_NOW": temp_qty.VALUE[0:1].sum()
                               , "QTY_PREV": temp_qty.VALUE[1:2].sum()
                               , "DPS_NOW": temp_dps.VALUE[0:4].sum()
                                }, ignore_index=True)
                print(i, TICKERS[i])
            except :
                pass
        mkt = kq.rank_stocks('MARKETCAP')
        mktcap = mkt[mkt.SYMBOL.isin(mkt.SYMBOL)][['SYMBOL','NAME','MARKETCAP','CLOSE']]
        df = df.merge(mktcap, on = 'SYMBOL', how = 'inner').replace(0, np.NaN).dropna()
        df['NI'] = (df['NI_NOW'] - df['NI_PREV']) / abs(df['NI_PREV'])
        df['OI'] = (df['OI_NOW'] - df['OI_PREV']) / abs(df['OI_PREV'])
        df['REV'] = (df['REV_NOW'] - df['REV_PREV']) / abs(df['REV_PREV'])
        df['FCF'] = (df['FCF_NOW'] - df['FCF_PREV']) / abs(df['FCF_PREV'])
        df['BP'] = df['EQ_NOW'] / df['MARKETCAP']
        df['EP'] = df['OI_NOW'] / df['MARKETCAP']
        df['CP'] = df['OCF_NOW'] / df['MARKETCAP']
        df['GPA'] = df['GP_NOW'] / df['LASS_NOW']
        df['NCV'] = (df['LASS_NOW'] - df['LIA_NOW']) / df['MARKETCAP']
        df['EPS'] = (df['NI_NOW']/df['QTY_NOW'] - df['NI_PREV']/df['QTY_PREV']) / abs(df['NI_PREV']/df['QTY_PREV'])
        df['DIV'] = df['DPS_NOW'] / df['CLOSE']
        feature = ['NI', 'OI', 'REV', 'FCF', 'BP', 'EP', 'CP', 'GPA', 'NCV', 'EPS', 'DIV']
        i = 1
        while i == 2 :
            df[feature] = minmax_scalor.fit_transform(df[feature])
            df[feature] = np.where((df[feature] > 0.98), 0.7, df[feature])
            df[feature] = np.where((df[feature] < 0.02), 0.3, df[feature])
            i += 1
        df[feature] = minmax_scalor.fit_transform(df[feature])
        return df

    def GET_DUR(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE):
        '''
        주식 듀레이션 산출하는 함수
        : 1) ROE와 자본증가율이 수렴하는 기간을 10년으로 가정, 이후 성장률은 고정된 것으로 가정함
          2) 무위험수익률 4%, 시장수익률 8% 가정하여 Discount Cash Flow Valuation 기반으로 듀레이션 산출함
             이때 듀레이션의 의미는 현 시가총액을 바탕으로 미래현금흐름 회수하는 데 소요되는 가중평균기간

        :param RISK_FREE: 무위험 수익률 (ex, 4%: 0.04)                        (float)
        :param MARKET_RATE: 시장 수익률 (ex, 7.5%, 0.075)                     (float)
        :param TICKERS: 분석 대상 종목의 티커리스트                              (list)
        :param PERIOD: 분석 대상 기간 (ex, 6개월: 6)                           (int)
        :param STDDATE: 기준일자                                             (str)
        :return: 종목별 듀레이션
        :rtype: dataframe
        '''
        stat = STATS_FOR_DUR(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE)
        df_dur = []
        for j in range(0, len(TICKERS)):
            cf_data = []
            t_date = dt.date(int(STDDATE[0:4]), int(STDDATE[4:6]), int(STDDATE[6:8]))
            temp = str((t_date - relativedelta(years=1)).year) + "1231"
            cf_date = dt.date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))
            try:
                temp = stat[stat.SYMBOL == TICKERS[j]]
                cf_prev = float(temp['CF_PREV'])
                cf_now = float(temp['CF_NOW'])
                mkt_cap = float(temp['MARKETCAP'])
                rate = float(temp['RATE'])
                growth = float(temp['GROWTH'])
                beta = float(temp['BETA'])
                i = 1
                if (cf_prev > 0) & (cf_now > 0) :
                    while i <= 10:
                        if i == 1:
                            cf_date += relativedelta(years=1)
                            cf_time = (cf_date - t_date).days / 365
                            cf_data.append([cf_date, cf_time, cf_prev])
                        elif i == 2:
                            cf_date += relativedelta(years=1)
                            cf_time = (cf_date - t_date).days / 365
                            cf_data.append([cf_date, cf_time, cf_now])
                        elif i > 1:
                            cf_date += relativedelta(years=1)
                            cf_time = (cf_date - t_date).days / 365
                            cf_amt_over = cf_now * (1 + growth)
                            cf_data.append([cf_date, cf_time, cf_amt_over])
                        i += 1
                    cf = pd.DataFrame(cf_data, columns=['cf_date', 'cf_time', 'cf_amt'])
                    cf['pv'] = cf['cf_amt'] / ((1 + rate) ** cf['cf_time'])
                    cf['pvt'] = cf['pv'] * cf['cf_time']
                    dur = (cf['pv'].sum() / mkt_cap) * (cf['pvt'].sum() / cf['pv'].sum()) + (1 - (cf['pv'].sum() / mkt_cap)) * (10 + (1 + rate) / rate)
                    df_dur.append([TICKERS[j], mkt_cap, beta, growth, rate, cf_now, cf_prev, dur])
                else:
                    pass
            except:
                pass
        df_dur = pd.DataFrame(df_dur, columns=['SYMBOL','MARKETCAP','BETA','GROWTH','RATE','CF','CF_PREV','DUR']).dropna()
        df_dur = df_dur[df_dur.DUR > 0]
        code = kq.symbol_stock()
        code_tgt = code[(code.SEC_TYPE == 'ST') & (~code.ADMIN_ISSUE.isin([20, 21, 22, 30, 40, 50, 60, 61, 70])) & \
                        (~code.NAME_EN.str.contains('(1P)|(2PB)')) & (~code.SYMBOL.str.contains('K'))]
        df_dur = df_dur.merge(code_tgt[['SYMBOL','NAME','MARKET']], on='SYMBOL', how='inner').sort_values('DUR', ascending=True).reset_index(drop=True)
        return df_dur

    def GET_TICKERS(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE) :
        '''
        투자가능 대상종목 산출하는 함수
        : 1) 가치주 : 주식 듀레이션 작은 순서로 100개 종목
          2) 성장주 : 주식 듀레이션 큰 순서로 100개 종목
          3) 혼합주 : 1), 2)에 속하지 않는 유니버스 종목 중 이익 모멘텀 큰 순서로 150개 종목

        :param RISK_FREE: 무위험 수익률 (ex, 4%: 0.04)                        (float)
        :param MARKET_RATE: 시장 수익률 (ex, 8%, 0.08)                       (float)
        :param TICKERS: 분석 대상 종목의 티커리스트                              (list)
        :param PERIOD: 분석 대상 기간 (ex, 6개월: 6)                           (int)
        :param STDDATE: 기준일자                                              (str)
        :return: 듀레이션, 가치, 성장, 혼합주 종목 리스트
        :rtype : dataframe, list, list, list
        '''
        mix_univ = UNIVERSE('mix')
        dur = GET_DUR(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE)
        val_list = dur[0:100].SYMBOL.tolist()
        gro_list = dur[len(dur)-100 : len(dur)].SYMBOL.tolist()
        temp_list = []
        for value in mix_univ.SYMBOL.tolist():
            if value not in val_list + gro_list: temp_list.append(value)
        df = STATS_FOR_MIX(temp_list)
        df = df[(df.NI_PREV_2Y<0)|(df.NI_PREV_1Y<0)|(df.NI_PREV<0)|(df.OI_PREV_2Y<0)|(df.OI_PREV_1Y<0)|(df.OI_PREV<0)].replace(0, np.NaN).dropna()
        df['NI'] = (df['NI_NOW'] - df['NI_PREV']) / abs(df['NI_PREV'])
        df['OI'] = (df['OI_NOW'] - df['OI_PREV']) / abs(df['OI_PREV'])

        feature = ['NI', 'OI']
        df[feature] = minmax_scalor.fit_transform(df[feature])
        df[feature] = np.where((df[feature] > 0.98), 0.7, df[feature])
        df[feature] = np.where((df[feature] < 0.02), 0.3, df[feature])
        df[feature] = minmax_scalor.fit_transform(df[feature])

        df['MIXSCORE'] = 1/2 * df['NI'] + 1/2 * df['OI']
        df = df.sort_values('MIXSCORE', ascending= False).reset_index(drop=True)
        mix_list = df[0:150].SYMBOL.tolist()
        return dur, val_list, gro_list, mix_list

    def GET_FEATURED_SCORE(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE) :
        '''
        그룹별 피쳐 가중스코어 산출하는 함수
        : 1) 그룹별 개별종목의 최근 1달 수익률을 산출
          2) 피쳐별로 1달 수익률 기준 5분위 롱숏 포트폴리오 수익률을 산출
          3) 그룹별로 롱숏 포트폴리오 수익률이 큰 순서로 나열
          4) 그룰별 롱숏 포트폴리오 수익률 기준 상위 3개 피쳐를 핵심피처로 정의
          4) 핵심피처를 0.5 0.3 0.2 순서로 가중치를 적용한 피쳐가중스코어 산출

        :param PERIOD: 분석 대상 기간 (ex, 1개월: 1)                            (int)
        :param TICKERS: 분석 대상 종목의 티커리스트                              (list)
        :param STDDATE: 기준일자                                              (str)
        :return: 각 그룹별 개별종목의 피쳐가중스코어
        :rtype: dataframe
        '''
        lists = GET_TICKERS(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE)
        dur = lists[0]
        val_tickers = lists[1]
        gro_tickers = lists[2]
        mix_tickers = lists[3]
        df_all = pd.DataFrame()
        grp = ['value','growth','mix']
        for i in range(0,len(grp)) :
            tgt_grp = grp[i]
            if tgt_grp == 'value' : grp_tickers = val_tickers
            elif  tgt_grp == 'growth' : grp_tickers = gro_tickers
            elif  tgt_grp == 'mix' : grp_tickers = mix_tickers

            feature = FEATURES(grp_tickers)
            prc = DATAS("CLOSE", grp_tickers, 1, STDDATE)
            # ago = (datetime.strptime(STDDATE, '%Y%m%d') - relativedelta(months=1))
            ago = (dt.date(int(STDDATE[0:4]), int(STDDATE[4:6]), int(STDDATE[6:8])) - relativedelta(months=1)).strftime('%Y%m%d')
            prc = prc[prc.index>=ago]
            ret = prc / prc.shift(len(prc)-1) - 1
            ret_tgt = pd.DataFrame(ret.iloc[len(ret) - 1])
            ret_tgt.columns = ['RET']
            ret_tgt = ret_tgt.reset_index(drop=False).rename(columns={'index': 'SYMBOL'}).sort_values('RET', ascending = False)
            df = feature.merge(ret_tgt[['SYMBOL','RET']], on ='SYMBOL', how = 'left')

            ls_srp = pd.DataFrame({'NI' : df.sort_values('NI', ascending = False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('NI', ascending = True)[0:int(len(df) / 5)].RET.mean()
               ,'OI' : df.sort_values('OI', ascending = False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('OI', ascending = True)[0:int(len(df) / 5)].RET.mean()
               ,'REV' : df.sort_values('REV', ascending = False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('REV', ascending = True)[0:int(len(df) / 5)].RET.mean()
               ,'FCF' : df.sort_values('FCF', ascending = False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('FCF', ascending = True)[0:int(len(df) / 5)].RET.mean()
               ,'BP' : df.sort_values('BP', ascending = False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('BP', ascending = True)[0:int(len(df) / 5)].RET.mean()
               ,'EP': df.sort_values('EP', ascending=False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('EP', ascending=True)[0:int(len(df) / 5)].RET.mean()
               ,'CP': df.sort_values('CP', ascending=False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('CP', ascending=True)[0:int(len(df) / 5)].RET.mean()
               ,'GPA': df.sort_values('GPA', ascending=False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('GPA', ascending=True)[0:int(len(df) / 5)].RET.mean()
               ,'NCV': df.sort_values('NCV', ascending=False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('NCV', ascending=True)[0:int(len(df) / 5)].RET.mean()
               ,'EPS': df.sort_values('EPS', ascending=False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('EPS', ascending=True)[0:int(len(df) / 5)].RET.mean()
               ,'DIV': df.sort_values('DIV', ascending=False).reset_index(drop=True)[0:int(len(df) / 5)].RET.mean() - df.sort_values('DIV', ascending=True)[0:int(len(df) / 5)].RET.mean()
               }, index = [0]).T

            ls_srp = ls_srp.sort_values(0,ascending = False)
            tgt_factor = ls_srp.index[0:3].tolist()
            df['FTSCORE'] = 0.5 * df[tgt_factor[0]] + 0.3 * df[tgt_factor[1]]  + 0.2 * df[tgt_factor[2]]
            df['FEAT1'] = tgt_factor[0]
            df['FEAT2'] = tgt_factor[1]
            df['FEAT3'] = tgt_factor[2]
            df['GUBUN'] = grp[i]
            df = df.sort_values('FTSCORE', ascending = False).reset_index(drop=True)
            df_all = pd.concat([df_all, df])
        df_all = df_all.merge(dur[['SYMBOL', 'BETA', 'GROWTH', 'RATE', 'CF', 'CF_PREV', 'DUR']], on='SYMBOL', how='left')
        df_all = df_all.merge(UNIVERSE('all')[['SYMBOL', 'MARKET']], on='SYMBOL', how='left').fillna(0)
        # df_all['STDDATE'] = datetime.strptime(STDDATE, '%Y%m%d')
        df_all['STDDATE'] = dt.date(int(STDDATE[0:4]), int(STDDATE[4:6]), int(STDDATE[6:8])).strftime('%Y%m%d')

        return df_all

    def GET_FINAL_TICKERS(DF) :
        '''
        최종 투자대상 종목을 산출하는 함수
         1) 가치/성장주 : 피처가중스코어 상위 10개씩
         2) 혼합주 : 피처가중스코어 상위 15개
         3) 10억원 기준 동일가중 적용하는 포트폴리오 구성

        :param df: 그룹별 피처가중스코어 데이터프레임
        :return: 최종투자대상 종목 관련 데이터
        '''
        df = DF[['STDDATE', 'SYMBOL', 'NAME', 'MARKET', 'CLOSE', 'MARKETCAP', 'GUBUN', 'FEAT1', 'FEAT2', 'FEAT3', 'FTSCORE', \
                 'BETA', 'DUR', 'CF', 'CF_PREV', 'RATE', 'GROWTH', 'NI', 'OI', 'REV', 'FCF', 'BP', 'EP', 'CP', 'GPA', 'NCV',
                 'EPS', 'DIV', 'RET']]
        grp = ['value', 'growth', 'mix']
        df_all = pd.DataFrame()
        for i in range(0, len(grp)):
            if grp[i] == 'mix':
                temp = df[df.GUBUN == grp[i]][0:15]
            else:
                temp = df[df.GUBUN == grp[i]][0:10]
            df_all = pd.concat([df_all, temp])
        df_all['WGT'] = 1 / len(df_all)
        df_all['AMT'] = 1000000000 * df_all['WGT']
        df_all['QTY'] = (df_all['AMT'] / df_all['CLOSE']).round()
        return df_all

    if date == dt.date(2023,10,4):  # 투자시작일

        PERIOD = 6
        RISK_FREE = 0.04
        MARKET_RATE = 0.08

        TICKERS = UNIVERSE('dur').SYMBOL.unique().tolist()
        STDDATE = date.strftime('%Y%m%d')

        feat_wgt = GET_FEATURED_SCORE(RISK_FREE, MARKET_RATE, TICKERS, PERIOD, STDDATE) # 피처가중스코어
        final = GET_FINAL_TICKERS(feat_wgt) # 최종투자대상

        symbols = final.SYMBOL.tolist()
        qty = final.QTY.tolist()

        # 가치, 성장, 혼합주 각 10, 10, 15주 매수
        symbols_and_orders = [
            (symbols[0], qty[0]),
            (symbols[1], qty[1]),
            (symbols[2], qty[2]),
            (symbols[3], qty[3]),
            (symbols[4], qty[4]),
            (symbols[5], qty[5]),
            (symbols[6], qty[6]),
            (symbols[7], qty[7]),
            (symbols[8], qty[8]),
            (symbols[9], qty[9]),
            (symbols[10], qty[10]),
            (symbols[11], qty[11]),
            (symbols[12], qty[12]),
            (symbols[13], qty[13]),
            (symbols[14], qty[14]),
            (symbols[15], qty[15]),
            (symbols[16], qty[16]),
            (symbols[17], qty[17]),
            (symbols[18], qty[18]),
            (symbols[19], qty[19]),
            (symbols[20], qty[20]),
            (symbols[21], qty[21]),
            (symbols[22], qty[22]),
            (symbols[23], qty[23]),
            (symbols[24], qty[24]),
            (symbols[25], qty[25]),
            (symbols[26], qty[26]),
            (symbols[27], qty[27]),
            (symbols[28], qty[28]),
            (symbols[29], qty[29]),
            (symbols[30], qty[30]),
            (symbols[31], qty[31]),
            (symbols[32], qty[32]),
            (symbols[33], qty[33]),
            (symbols[34], qty[34])
             ]
    else:
        symbols_and_orders = []

    return symbols_and_orders