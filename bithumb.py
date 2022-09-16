import requests
import json
from urllib.parse import urlencode
import time
import hmac
import base64
import hashlib

"""
모든 반환 형식은 json 형식 입니다.
private api는 모두 딕셔너리형태의 파라미터를 요구합니다.
query = (dict) 형식을 지켜주세요
상세한 내용은 빗썸 공식 API Docs를 참조하세요
https://apidocs.bithumb.com/docs/api_info
"""

# API 키 할당
with open('../json/api.json', 'r') as f:
    api = json.load(f)
    accessKey = api['BITHUMB']['ACCESS']
    secretKey = api['BITHUMB']['SECRET']

# 실행 부분 (Public API)
def quotation(url, **kwargs):
    endpoint = 'https://api.bithumb.com/public/'
    headers = {'Accept': "application/json"}
    method = 'get'
    if 'query' in kwargs:
        query_string = urlencode(kwargs['query']).encode()
        res = requests.request(method, endpoint + url, headers=headers, params=query_string)
        return res.status_code, res.json()

    res = requests.request(method, endpoint + url, headers=headers)
    return res.status_code, res.json()

# 실행 부분 (Private API)
def execute(url, **kwargs):
    endpoint = 'https://api.bithumb.com'
    method = 'post'
    nonce = str(int(time.time() * 1000))
    item = {
        "endpoint": url
    }
    print('빗썸에 전송된 파라미터', kwargs['query'])

    uri_array = dict(item, **kwargs['query'])
    #print(uri_array)
    uri_array_encode = urlencode(uri_array)

    hmac_key = secretKey.encode('utf-8')
    hmac_data = (url + chr(0) + uri_array_encode + chr(0) + nonce).encode('utf-8')

    hmh = (hmac.new(bytes(hmac_key), hmac_data, hashlib.sha512)).hexdigest()
    hmac_hash = base64.b64encode(hmh.encode('utf-8'))

    api_sign = hmac_hash
    api_sign = api_sign.decode('utf-8')

    headers = {
        'Api-Key': accessKey,
        'Api-Sign': api_sign,
        'Api-Nonce': nonce
    }
    print(endpoint+url)
    res = requests.request(method, endpoint + url, headers=headers, data=uri_array)
    return res.status_code, res.json()

# 현재가 정보
def ticker(base, ticker):
    """
    [Require]
    * base                                      결제 통화
    * ticker                                    티커

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    opening_price	                            시가 00시 기준
    closing_price	                            종가 00시 기준
    min_price	                                저가 00시 기준
    max_price	                                고가 00시 기준
    units_traded	                            거래량 00시 기준
    acc_trade_value	                            거래금액 00시 기준
    prev_closing_price	                        전일종가
    units_traded_24H	                        최근 24시간 거래량
    acc_trade_value_24H	                        최근 24시간 거래금액
    fluctate_24H	                            최근 24시간 변동가
    fluctate_rate_24H	                        최근 24시간 변동률
    date	                                    타임 스탬프
    """
    url = f'ticker/{ticker.upper()}/{base.upper()}'
    return quotation(url=url)

# 호가 조회
def orderbook(base, ticker, **kwargs):
    """
    [Require]
    * base                                      결제 통화
    * ticker                                    티커
    count                                       1 ~ 30 (default : 30), 1 ~ 5(ALL, default : 5)

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    timestamp	                                타임 스탬프
    order_currency	                            주문 통화 (코인)
    payment_currency	                        결제 통화 (마켓)
    bids	                                    매수 요청 내역
    asks	                                    매도 요청 내역
    quantity	                                Currency 수량
    price	                                    Currency 거래가
    """

    url = f'orderbook/{ticker.upper()}_{base.upper()}'
    if 'query' in kwargs:
        query = kwargs['query']
        return quotation(url=url, query=query)

    return quotation(url=url)

# 체결 내역 조회
def transaction(base, ticker, **kwargs):
    """
    [Require]
    * base                                      결제 통화
    * ticker                                    티커
    count                                       1 ~ 100 (default : 100)

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    transaction_date	                        거래 체결 시간 타임 스탬프
                                                ㄴ (YYYY-MM-DD HH:MM:SS)
    type	                                    거래 유형
                                                ㄴ bid : 매수 ask : 매도
    units_traded	                            Currency 거래량
    price	                                    Currency 거래가
    total	                                    총 거래 금액
    """

    url = f'transaction_history/{ticker}_{base}'
    if 'query' in kwargs:
        query = kwargs['query']
        return quotation(url=url, query=query)
    return quotation(url=url)

# 입출금 현황 조회
def assetsstatus(ticker):
    """
    [Require]
    * ticker                                    티커

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    deposit status	                            입금 가능 여부(1:입금가능 / 0:입금불가)
    withdrawal_status	                        출금 가능 여부(1:출금가능 / 0:출금불가)
    """

    url = f'assetsstatus/{ticker}'
    return quotation(url=url)

# BTCI 정보 조회
def btci():
    """
    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    btai	                                    Bithumb Altcoin Market Index
    btmi	                                    Bithumb Market Index
    market_index	                            시장 기준 지수
    width	                                    등락폭
    rate	                                    등락률
    date	                                    타임 스탬프
    """
    url = 'btci'
    return quotation(url=url)

# Private API
# 계정 정보
def account(**kwargs):
    """
    [Require]
    order_currency                              주문 코인
    payment_currency                            결제 통화 (마켓)

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)	String
    created	                                    회원가입 일시 타임 스탬프	Integer
    account_id	                                회원 ID	String
    order_currency	                            주문 통화 (코인)	String
    payment_currency	                        결제 통화 (마켓)	String
    trade_fee	                                거래 수수료율	Number (String)
    balance	                                    주문 가능 수량	Number (String)
    """

    url = '/info/account'
    return execute(url=url, **kwargs)

# 잔고 조회
def balance(**kwargs):
    """
    [Require]
    currency                                    티커 (ALL 가능, default : BTC)

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    total_{currency}	                        전체 가상자산 수량
    total_krw	                                전체 원화(KRW) 금액
    in_use_{currency}	                        주문 중 묶여있는 가상자산 수량
    in_use_krw	                                주문 중 묶여있는 원화(KRW) 금액
    available_{currency}	                    주문 가능 가상자산 수량
    available_krw	                            주문 가능 원화(KRW) 금액
    xcoin_last_{currency}	                    마지막 체결된 거래 금액
                                                ㄴ ALL 호출 시 필드 명 – xcoin_last_{currency}
    """

    url = '/info/balance'
    return execute(url=url, **kwargs)

# 지갑 주소 조회
def wallet(**kwargs):
    """
    [Require]
    currency                                    티커 (default : BTC)

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    wallet_address	                            가상자산 지갑 주소
    currency	                                Request Parameters 데이터와 동일
    """

    url = '/info/wallet_address'
    return execute(url=url, **kwargs)

# 유저 거래 정보 조회
def ticker_user(**kwargs):
    """
    [Require]
    * order_currency                            티커
    payment_currency                            결제 통화

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_currency	                            주문 통화 (코인)
    payment_currency	                        결제 통화 (마켓)
    opening_price	                            회원 시작 거래가 (최근 24시간)
    closing_price	                            회원 마지막 거래가 (최근 24시간)
    min_price	                                회원 최저 거래가 (최근 24시간)
    max_price	                                회원 최고 거래가 (최근 24시간)
    average_price	                            평균가 (최근 24시간)
    units_traded	                            거래량 (최근 24시간)
    volume_1day	                                Currency 거래량 (최근 1일)
    volume_7day	                                Currency 거래량 (최근 7일)
    fluctate_24H	                            최근 24시간 변동가
    fluctate_rate_24H	                        최근 24시간 변동률
    Date	                                    타임 스탬프
    """

    url = '/info/ticker'
    return execute(url=url, **kwargs)

# 주문 조회
def orders(**kwargs):
    """
    [Require]
    * order_currency                            티커
    order_id                                    주문번호
    type                                        거래 유형 (ask : 매도. bid : 매수)
    count                                       1 ~ 1000 (default : 100)
    after                                       입력한 시간보다 나중의 데이터 추출 (YYYY-MM-DD hh:mm:ss 의 UNIX Timestamp)
    payment_currency                            결제 통화

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_currency	                            주문 통화 (코인)
    payment_currency	                        결제 통화 (마켓)
    order_id	                                매수/매도 주문 등록된 주문번호
    order_date	                                주문일시 타임 스탬프
    type	                                    주문 요청 구분 (bid : 매수 ask : 매도)
    watch_price	                                주문 접수가 진행되는 가격 (자동주문시)
    units	                                    거래요청 Currency
    units_remaining	                            주문 체결 잔액
    price	                                    1Currency당 주문 가격
    """

    url = '/info/orders'
    return execute(url=url, **kwargs)

# 주문 상세 정보 조회
def order_detail(**kwargs):
    """
    [Require]
    * order_currency                            티커
    * order_id                                  주문번호
    payment_currency                            결제 통화

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_date	                                주문요청 시간 타임 스탬프
    type	                                    주문 요청 구분 (bid : 매수 ask : 매도)
    order_status	                            주문 상태
    order_currency	                            주문 통화 (코인)
    payment_currency	                        결제 통화 (마켓)
    watch_price	                                주문 접수가 진행된 가격 (자동주문시)
    order_price	                                주문요청 호가
    order_qty	                                주문요청 수량
    cancel_date	                                취소 일자 타임스탬프
    cancel_type	                                취소 유형
    contract	                                해당주문 체결정보
    transaction_date	                        거래 체결 시간 타임 스탬프
                                                ㄴ (YYYY-MM-DD HH:MM:SS)
    price	                                    1Currency당 체결가
    units	                                    거래수량
    fee_currency	                            수수료 통화
    fee	                                        거래 수수료
    total	                                    체결 금액
    """

    url = '/info/order_detail'
    return execute(url=url, **kwargs)

# 거래 내역 조회
def transactions(**kwargs):
    """
    [Require]
    * order_currency                            티커
    * payment_currency                          결제 통화
    searchGb                                    0 : 전체, 1 : 매수 완료, 2 : 매도 완료, 3 : 출금 중, 4 : 입금, 5 : 출금, 9 : KRW 입금 중
    count                                       1 ~ 50 (default : 20)
    offset                                      0 ~ (default : 0)

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    search	                                    검색 구분
                                                ㄴ 0 : 전체, 1 : 매수 완료, 2 : 매도 완료, 3 : 출금 중, 4 : 입금, 5 : 출금, 9 : KRW 입금 중
    transfer_date	                            거래 일시 타임 스탬프
                                                ㄴ YYYY-MM-DD HH:MM:SS
    order_currency	                            주문 통화 (코인)
    payment_currency	                        결제 통화 (마켓)
    units	                                    거래요청 Currency 수량
    price	                                    1Currency당 가격
    amount	                                    거래 금액
    fee_currency	                            수수료 통화
    fee	                                        거래 수수료
    order_balance	                            주문 통화 잔액
    payment_balance	                            결제 통화 잔액
    """

    url = '/info/user_transactions'
    return execute(url=url, **kwargs)

# 지정가 주문 생성
def limit_order(**kwargs):
    """
    [Require]
    * order_currency                            티커
    * payment_currency                          주문 통화
    * units                                     수량(float)
    * price                                     가격
    * type                                      매수 : bid, 매도 : ask

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_id	                                주문 번호
    """

    url = '/trade/place'
    return execute(url=url, **kwargs)

# 주문 취소
def cancel_order(**kwargs):
    """
    [Require]
    * type                                      거래유형 bid or ask
    * order_id                                  주문 번호
    * order_currency                            주문 통화
    * payment_currency                          결제 통화

    [Response]
    status                                      결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    """

    url = '/trade/cancel'
    return execute(url=url, **kwargs)

# 시장가 매수 주문
def market_buy(**kwargs):
    """
    [Require]
    * units                                     코인 매수 수량 [Maximum : 10B]
    * order_currency                            티커
    * payment_currency                          결제 통화

    [Response]
    status                                      결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_id                                    주문 번호
    """

    url = '/trade/market_buy'
    return execute(url=url, **kwargs)

# 시장가 매도 주문
def market_sell(**kwargs):
    """
    [Require]
    * units                                     코인 매수 수량 [Maximum : 10B]
    * order_currency                            티커
    * payment_currency                          결제 통화

    [Response]
    status                                      결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_id                                    주문 번호
    """

    url = '/trade/market_sell'
    return execute(url=url, **kwargs)

# S/L 주문
def stop_limit(**kwargs):
    """
    [Require]
    * units                                     코인 매수 수량 [Maximum : 5B]
    * order_currency                            티커
    * payment_currency                          결제 통화
    * watch_price                               주문 접수가 진행되는 가격 (자동 주문 시)
    * price                                     Currency 거래가
    * type                                      주문 요청 구분 (bid : 매수, ask : 매도)

    [Response]
    status                                      결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_id                                    주문 번호
    """

    url = '/trade/stop_limit'
    return execute(url=url, **kwargs)

# 코인 출금 요청
def withdraw_coin(**kwargs):
    # todo URI Not Found 문제 해결 해야함,,, 출금 차단으로 인한 오류일거라고 생각이 되긴함 ..
    """
    [Require]
    * units                                     코인 출금 수량
    * address                                   지갑 주소
    destination                                 2차 주소 (XRP : detination tag, STEEM : memo, XMR : Payment ID)
    * currency                                  티커
    * exchange_name                             출금 거래소명명    * watch_price                               주문 접수가 진행되는 가격 (자동 주문 시)
    * cust_type_cd                              개인/법인 여부(개인 01, 법인 02) (string)
    * ko_name                                   수취인 국문명
    * en_name                                   수취인 영문명

    * corp_ko_name                              법인 수취 정보 국문 법인명
    * corp_en_name                              법인 수취 정보 영문 법인명
    * corp_rep_ko_name                          법인 수취 정보 국문 법인 대표자명
    * corp_rep_en_name                          법인 수취 정보 영문 법인 대표자명

    [Response]
    status                                      결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)
    order_id                                    주문 번호
    """

    url = '/trade/{}_withdrawal'.format(kwargs['query']['currency'])
    return execute(url=url, **kwargs)
#
# query = {
#     'units': '1',
#     'address': '0x64460153681F58cD2Df9cE1E788Ec15e4A27e425',
#     'currency': 'eth',
#     'exchane_name': 'metamask',
#     'cust_type_cd': '01',
#     'ko_name': '송영빈',
#     'en_name': 'YEONGBIN SONG'
# }

# Candlestick API
# 캔들 스틱 요청
def candle(**kwargs):
    """
    [Require]
    * order_currency                            티커
    * payment_currency                          결제 통화
    * chart_intervals                           24h {1m, 3m, 5m, 10, 30, 1h, 6h, 12h, 24h}

    [Response]
    status	                                    결과 상태 코드 (정상: 0000, 그 외 에러 코드 참조)	String
    [data] – [N] – [0]	                        기준 시간
    [data] – [N] – [1]	                        시가	Number
    [data] – [N] – [2]	                        종가	Number
    [data] – [N] – [3]	                        고가	Number
    [data] – [N] – [4]	                        저가	Number
    [data] – [N] – [5]	                        거래량
    """
    order_currency = kwargs['query']['order_currency']
    payment_currency = kwargs['query']['payment_currency']
    chart_intv = kwargs['query']['chart_intervals']
    url = 'candlestick/{}_{}/{}'.format(order_currency, payment_currency, chart_intv)
    return quotation(url=url)

query = {
    'currency': 'req'
}

# print(account(query=query))
# print(balance(query=query))
print(wallet(query=query))
# print(ticker_user(query=query))
# print(orders(query=query))
# print(order_detail(query=query))
# print(transactions(query=query))
# print(limit_order(query=query))
# print(cancel_order(query=query))
# print(market_buy(query=query))
# print(market_sell(query=query))
# print(stop_limit(query=query))
# print(withdraw_coin(query=query)) # 이거는 오류 찾아야댐 출금 차단으로 인한 접근 오류인가 ?
# print(candle(query=query))


# print(ticker(base='krw', ticker='all'))
# print(orderbook(base='krw', ticker='btc', query=query))
# print(transaction('krw', 'eth', query=query))
# print(assetsstatus('all'))
# print(btci())