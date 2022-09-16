import requests
import json
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import time

"""
    모든 반환값은 json 형식 입니다 
    함수가 파라미터를 요구하는 경우
    query=(dict) 형식으로 호출하세요
"""

# API키 할당
with open('../json/api.json', 'r') as f:
    api = json.load(f)
    accessKey = api['UPBIT']['ACCESS']
    secretKey = api['UPBIT']['SECRET']

# 요청 실행 (Exchange API 실행 부분입니다)
def excute(url, method, **kwargs):
    endpoint = 'https://api.upbit.com/'
    payload = {
        'access_key': accessKey,
        'nonce': str(uuid.uuid4()),
    }

    # print('업비트에 전송된 파라미터', kwargs['query'])

    def setpayload(payload):
        jwt_token = jwt.encode(payload, secretKey)
        jwt_token = 'Bearer {}'.format(jwt_token)
        new_header = {'Authorization': jwt_token}
        return new_header

    if 'query' in kwargs:
        query_string = urlencode(kwargs['query']).encode()
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload['query_hash'] = query_hash
        payload['query_hash_alg'] = 'SHA512'
        headers = setpayload(payload)

        res = requests.request(method, endpoint + url, headers=headers, params=kwargs['query'])
        return res.status_code, res.json()

    headers = setpayload(payload)

    res = requests.request(method, endpoint + url, headers=headers)
    return res.status_code, res.json()

# 요청 실행 (Quotation API 실행 부분입니다)
def quotation(url, **kwargs):
    endpoint = 'https://api.upbit.com/v1/'
    headers = {'Accept': "application/json"}
    method = 'get'
    if 'query' in kwargs:
        query_string = urlencode(kwargs['query']).encode()
        # print(query_string)
        res = requests.request(method, endpoint + url, headers=headers, params=query_string)
        return res.status_code, res.json()

    res = requests.request(method, endpoint + url, headers=headers)
    return res.status_code ,res.json()

# 계좌 잔액 불러오기
def accounts(**kwargs):
    """
    [Response]
    currency                                화폐를 의미하는 영문 대문자 코드
    balance                                 주문가능 금액/수량
    locked                                  주문 중 묶여있는 금액/수량
    avg_buy_price                           매수평균가
    avg_buy_price_modified                  매수평균가 수정 여부
    unit_currency                           평단가 기준 화폐
    """

    url = 'v1/accounts'
    method = 'get'
    return excute(url=url, method=method)

# 주문 가능 정보
def orders_chance(**kwargs):
    """
    [Require]
    * market                                마켓 정보 (base-ticker)

    [Response]
    ask_fee                                 매도 수수료 비율
    market                                  마켓에 대한 정보
    market.id                               마켓의 유일 키
    market.name                             마켓 이름
    market.order_types                      지원 주문 방식
    market.order_sides                      지원 주문 종류
    market.bid                              매수 시 제약사항
    market.bid.currency                     화폐를 의미하는 영문 대문자 코드
    market.bit.price_unit                   주문금액 단위
    market.bid.min_total                    최소 매도/매수 금액
    market.ask                              매도 시 제약사항
    market.ask.currency                     화폐를 의미하는 영문 대문자 코드
    market.ask.price_unit                   주문금액 단위
    market.ask.min_total                    최소 매도/매수 금액
    market.max_total                        최대 매도/매수 금액
    market.state                            마켓 운영 상태
    bid_account                             매수 시 사용하는 화폐의 계좌 상태
    bid_account.currency                    화폐를 의미하는 영문 대문자 코드
    bid_account.balance                     주문가능 금액/수량
    bid_account.locked                      주문 중 묶여있는 금액/수량
    bid_account.avg_buy_price               매수평균가
    bid.account.avg_buy_price_modified      매수평균가 수정 여부
    bid_account.unit_currency               평단가 기준 화폐
    ask_account                             매도 시 사용하는 화폐의 계좌 상태
    ask_account.currency                    화폐를 의미하는 영문 대문자 코드
    ask_account.balance                     주문가능 금액/수량
    ask_account.locked                      주문 중 묶여있는 금액/수량
    ask_account.avg_buy_price               매수평균가
    ask_account.avg_buy_price_modified      매수평균가 수정 여부
    ask_account.unit_currency               평단가 기준 화폐
    """

    query = kwargs['query']
    url = 'v1/orders/chance'
    method = 'get'
    return excute(url=url, query=query, method=method)

# 개별 주문 조회
def order(**kwargs):
    """
    [Require]
    uuid	                                주문 UUID
    identifier	                            조회용 사용자 지정 값

    [Response]
    uuid                                    주문의 고유 아이디
    side                                    주문 종류
    ord_type                                주문 방식
    price                                   주문 당시 화폐 가격
    state                                   주문 상태
    market                                  마켓의 유일키
    created_at                              주문 생성 시간
    volume                                  사용자가 입력한 주문 양
    remaining_volume                        체결 후 남은 주문 양
    reserved_fee                            수수료로 예약된 비용
    remaining_fee                           남은 수수료
    paid_fee                                사용된 수수료
    locked                                  거래에 사용중인 비용
    executed_volume                         채결된 양
    trade_count                             해당 주문에 걸린 체결 수
    trades                                  체결
    trades.market                           마켓의 유일 키
    trades.uuid                             체결의 고유 아이디
    trades.price                            체결 가격
    trades.volume                           체결 양
    trades.funds                            체결된 총 가격
    trades.side                             체결 종류
    trades.created_at                       체결 시각
    """

    query = kwargs['query']
    url = 'v1/order'
    method = 'get'
    return excute(url=url, query=query, method=method)

# 주문 리스트 조회
def orders(**kwargs):
    url = 'v1/orders'
    method = 'get'

    if bool(kwargs):
        query = kwargs['query']
        return excute(url=url, query=query, method=method)

    return excute(url=url, method=method)
    #todo 나중에 여기는 생각해보자

# 주문 취소 요청
def order_cancel(**kwargs):
    """
    [Response]
    uuid                                    주무의 고유 아이디
    side                                    주문 종류
    ord_type                                주문 방식
    price                                   주문 당시 화폐 가격
    state                                   주문 상태
    market                                  마켓의 유일키
    created_at                              주문 생성 새간
    volume                                  사용자가 입력한 주문 양
    remaining_volume                        체결 후 남은 주문 양
    reserved_fee                            수수료로 예약된 비용
    remaining_fee                           남은 수수료
    paid_fee                                사용된 수수료
    locked                                  거래에 사용중인 비용
    executed_volume                         체결된 양
    trade_count                             해당 주문에 걸린 체결 수
    """

    query = kwargs['query']
    url = 'v1/order'
    method = 'delete'
    return excute(url=url, query=query, method=method)

# 주문 생성 요청
def order_place(**kwargs):
    """
    [Require]
    * market                                 마켓 ID
    * side                                   주문 종류 bid : 매수, ask : 매도
    * volume                                 주문량
    * price                                  주문가격
    * ord_type                               주문 타입 limit : 지정가, price : 시장가(매수), market : 시장가(매도)
    identifier

    [Response]
    uuid                                    주문의 고유아이디
    side                                    주문 종류
    ord_type                                주문 방식
    price                                   주문 당시 화폐 가격
    avg_price                               체결 가격의 평균가
    state                                   주문 상태
    market                                  마켓의 유일키
    created_at                              주문 생성 시간
    volume                                  사용자가 입력한 주문 양
    remaining_volume                        체결 후 남은 주문 양
    reserved_fee                            수수료로 예약된 비용
    remaining_fee                           남은 수수료
    paid_fee                                사용된 수수료
    locked                                  거래에 사용중인 비용
    executed_volume                         체결된 양
    trade_count                             해당 주문에 걸린 체결 수
    """

    query = kwargs['query']
    url = 'v1/orders'
    method = 'post'
    return excute(url=url, query=query, method=method)

# 출금 리스트 조회
def withdraws(**kwargs):
    """
    [Response]
    type                                    입출금 종류
    uuid                                    출금의 고유 아이디
    currency                                화폐를 의미하는 영문 대문자 코드
    txid                                    출금의 트랜잭션 아이디
    state                                   출금 상태
    created_at                              출금 생성 시간
    done_at                                 출금 완료 시간
    amount                                  출금 금액/수량
    fee                                     출금 수수료
    transaction_type                        출금유형
    ㄴ default : 일반출금
    ㄴ internal : 바로출금
    """

    query = kwargs['query']
    url = 'v1/withdraws'
    method = 'get'
    return excute(url=url, query=query, method=method)

# 개별 출금 조회
def withdraw(**kwargs):
    """
    [Response]
    type                                    입출금의 종류
    uuid                                    출금의 고유 아이디
    currency                                화폐를 의미하는 영문 대문자 코드
    txid                                    출금의 트랜잭션 아이디
    state                                   출금 상태
    created_at                              출금 생성 시간
    done_at                                 출금 완료 시간
    amount                                  출금 금액/수량
    fee                                     출금 수수료
    transaction_type                        출금 유형
    ㄴ default : 일반출금
    ㄴ internal : 바로출금
    """

    query = kwargs['query']
    url = 'v1/withdraw'
    method = 'get'
    return excute(url=url, query=query, method=method)

# 출금 가능 정보
def withdraws_chance(**kwargs):
    """
    [Require]
    * currency                              티커

    [Response]
    member_level	                        사용자의 보안등급 정보
    member_level.security_level	            사용자의 보안등급
    member_level.fee_level	                사용자의 수수료등급
    member_level.email_verified	            사용자의 이메일 인증 여부
    member_level.identity_auth_verified	    사용자의 실명 인증 여부
    member_level.bank_account_verified	    사용자의 계좌 인증 여부
    member_level.kakao_pay_auth_verified    사용자의 카카오페이 인증 여부
    member_level.locked	                    사용자의 계정 보호 상태
    member_level.wallet_locked	            사용자의 출금 보호 상태
    currency	                            화폐 정보
    currency.code	                        화폐를 의미하는 영문 대문자 코드
    currency.withdraw_fee	                해당 화폐의 출금 수수료
    currency.is_coin	                    화폐의 코인 여부
    currency.wallet_state	                해당 화폐의 지갑 상태
    currency.wallet_support	                해당 화폐가 지원하는 입출금 정보
    account	                                사용자의 계좌 정보
    account.currency	                    화폐를 의미하는 영문 대문자 코드
    account.balance	                        주문가능 금액/수량
    account.locked	                        주문 중 묶여있는 금액/수량
    account.avg_buy_price	                매수평균가
    account.avg_buy_price_modified	        매수평균가 수정 여부
    account.unit_currency	                평단가 기준 화폐
    withdraw_limit	                        출금 제약 정보
    withdraw_limit.currency	                화폐를 의미하는 영문 대문자 코드
    withdraw_limit.minimum	                출금 최소 금액/수량
    withdraw_limit.onetime	                1회 출금 한도
    withdraw_limit.daily	                1일 출금 한도
    withdraw_limit.remaining_daily	        1일 잔여 출금 한도
    withdraw_limit.remaining_daily_krw	    통합 1일 잔여 출금 한도
    withdraw_limit.fixed	                출금 금액/수량 소수점 자리 수
    withdraw_limit.can_withdraw	            출금 지원 여부
    """

    query = kwargs['query']
    url = 'v1/withdraws/chance'
    method = 'get'
    return excute(url=url, query=query, method=method)

# query = {
#     'currency': 'BTC',
#     'amount': '0.001',
#     'address': 'btc-pizzaday-2022',
#     'transaction_type': 'internal'
# }

# 코인 출금
def withdraws_coin(**kwargs):
    """
    [Require]
    * currency                              Currency 코드
    * amount                                출금 수량
    * address                               출금 가능 주소에 등록된 출금 주소
    secondary_address	                    2차 출금 주소 (필요한 코인에 한해서)
    transaction_type	                    출금 유형

    [Response]
    type	                                입출금 종류
    uuid	                                출금의 고유 아이디
    currency	                            화폐를 의미하는 영문 대문자 코드
    txid	                                출금의 트랜잭션 아이디
    state	                                출금 상태
    created_at	                            출금 생성 시간
    done_at	                                출금 완료 시간
    amount	                                출금 금액/수량
    fee	                                    출금 수수료
    krw_amount	                            원화 환산 가격
    transaction_type	                    출금 유형
    ㄴ default : 일반출금
    ㄴ internal : 바로출금
    """

    query = kwargs['query']
    url = 'v1/withdraws/coin'
    method = 'post'
    return excute(url=url, query=query, method=method)

# 원화 출금
def withdraws_krw(**kwargs):
    """
    [Require]
    *amount                                 출금액

    [Response]
    type	                                입출금 종류
    uuid	                                출금의 고유 아이디
    currency	                            화폐를 의미하는 영문 대문자 코드
    txid	                                출금의 트랜잭션 아이디
    state	                                출금 상태
    created_at	                            출금 생성 시간
    done_at	                                출금 완료 시간
    amount	                                출금 금액/수량
    fee	                                    출금 수수료
    transaction_type	                    출금 유형
    ㄴ default : 일반출금
    ㄴ internal : 바로출금
    """

    query = kwargs['query']
    url = 'v1/withdraws/krw'
    method = 'post'
    return excute(url=url, query=query, method=method)

# 입금 리스트 조회
def deposits(**kwargs):
    """
    [Require]
    currency	                            Currency 코드
    state	                                입금 상태
    ㄴ submitting : 처리 중
    ㄴ submitted : 처리완료
    ㄴ almost_accepted : 입금 대기 중
    ㄴ rejected : 거절
    ㄴ accepted : 승인됨
    ㄴ processing : 처리 중
    uuids	                                입금 UUID의 목록
    txids	                                입금 TXID의 목록
    limit	                                개수 제한 (default: 100, limit: 100)
    page	                                페이지 수, default: 1
    order_by	                            정렬
    ㄴ asc : 오름차순
    ㄴ desc : 내림차순 (default)

    [Response]
    type	                                입출금 종류
    uuid	                                입금에 대한 고유 아이디
    currency	                            화폐를 의미하는 영문 대문자 코드
    txid	                                입금의 트랜잭션 아이디
    state	                                입금 상태
    created_at	                            입금 생성 시간
    done_at	                                입금 완료 시간
    amount	                                입금 수량
    fee	                                    입금 수수료
    transaction_type	                    입금 유형
    ㄴ default : 일반입금
    ㄴ internal : 바로입금
    """

    url = 'v1/deposits'
    method = 'get'

    if bool(kwargs):
        query = kwargs['query']
        return excute(url=url, query=query, method=method)

    return excute(url=url, method=method)

# 개별 입금 조회
def deposit(**kwargs):
    """
    [Require]
    uuid	                                입금 UUID
    txid	                                입금 TXID
    currency	                            Currency 코드

    [Response]
    type	                                입출금 종류
    uuid	                                입금에 대한 고유 아이디
    currency	                            화폐를 의미하는 영문 대문자 코드
    txid	                                입금의 트랜잭션 아이디
    state	                                입금 상태
    created_at	                            입금 생성 시간
    done_at	                                입금 완료 시간
    amount	                                입금 수량
    fee	                                    입금 수수료
    transaction_type	                    입금 유형
    ㄴ default : 일반입금
    ㄴ internal : 바로입금	String
    """

    url = 'v1/deposit'
    method = 'get'

    if bool(kwargs):
        query = kwargs['query']
        return excute(url=url, query=query, method=method)

    return excute(url=url, method=method)

# 입금 주소 생성 요청
def deposits_generate(**kwargs):
    """
    [Require]
    * currency	                            Currency 코드

    [Response 1]
    success	                                요청 성공 여부
    message	                                요청 결과에 대한 메세지

    [Response 2]
    currency	                            화폐를 의미하는 영문 대문자 코드
    deposit_address	                        입금 주소
    secondary_address	                    2차 입금 주소
    """

    query = kwargs['query']
    url = 'v1/deposits/generate_coin_address'
    method = 'post'
    return excute(url=url, query=query, method=method)

# 전체 입금 주소 조회
def deposits_coin_addresses(**kwargs):
    """
    [Response]
    currency	                            화폐를 의미하는 영문 대문자 코드
    deposit_address	                        입금 주소
    secondary_address	                    2차 입금 주소
    """

    url = 'v1/deposits/coin_addresses'
    method = 'get'

    if bool(kwargs):
        query = kwargs['query']
        return excute(url=url, query=query, method=method)

    return excute(url=url, method=method)

# 개별 입금 주소 조회
def deposit_coin_address(**kwargs):
    """
    [Require]
    * currency                              화폐를 의미하는 영문 대문자 코드

    [Response]
    currency	                            화폐를 의미하는 영문 대문자 코드
    deposit_address	                        입금 주소
    secondary_address	                    2차 입금 주소
    """

    url = 'v1/deposits/coin_address'
    method = 'get'

    if bool(kwargs):
        query = kwargs['query']
        return excute(url=url, query=query, method=method)

    return excute(url=url, method=method)

# 원화 입금하기
def deposits_krw(**kwargs):
    """
    [Require]
    * amount                                입금액

    [Response]
    type	                                입출금 종류
    uuid	                                입금의 고유 아이디
    currency	                            화폐를 의미하는 영문 대문자 코드
    txid	                                입금의 트랜잭션 아이디
    state	                                입금 상태
    created_at	                            입금 생성 시간
    done_at	                                입금 완료 시간
    amount	                                입금 금액/수량
    fee	                                    입금 수수료
    transaction_type	                    트랜잭션 유형
    ㄴ default : 일반출금
    ㄴ internal : 바로출금	String
    """

    url = 'v1/deposits/krw'
    method = 'post'
    query = kwargs['query']
    return excute(url=url, query=query, method=method)

# 입출금 현황
def status_wallet(**kwargs):
    """
    [Response]
    currency	                            화폐를 의미하는 영문 대문자 코드

    wallet_state	                        입출금 상태
    ㄴ working : 입출금 가능
    ㄴ withdraw_only : 출금만 가능
    ㄴ deposit_only : 입금만 가능
    ㄴ paused : 입출금 중단
    ㄴ unsupported : 입출금 미지원

    block_state	                            블록 상태
    ㄴ normal : 정상
    ㄴ delayed : 지연
    ㄴ inactive : 비활성 (점검 등)

    block_height	                        블록 높이
    block_updated_at	                    블록 갱신 시각
    """

    url = 'v1/status/wallet'
    method = 'get'
    return excute(url=url, method=method)

# API키 리스트 조회
def api_keys(**kwargs):
    """
    [Response]
    access_key                              액세스 키
    expire_at                               만료 시간
    """
    url = 'v1/api_keys'
    method = 'get'
    return excute(url=url, method=method)

"""
여기부터 Quotation API
"""

# 마켓 코드 조회
def market_all():
    """
    [Response]
    market	                                업비트에서 제공중인 시장 정보
    korean_name	                            거래 대상 암호화폐 한글명
    english_name	                        거래 대상 암호화폐 영문명
    market_warning	                        유의 종목 여부 -> NONE (해당 사항 없음), CAUTION(투자유의)
    """
    url = 'market/all'
    query = {
        'isDetails': 'true'
    }
    return quotation(url=url, query=query)

# 분봉 조회
def candle_minute(minute, **kwargs):
    """
    [Require]
    * minute                                조회 할 분 1, 3, 5, 10, 15, 30, 60, 240
    * market                                마켓 코드
    to                                      마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ss'Z' or yyyy-MM-dd HH:mm:ss. 비워서 요청시 가장 최근 캔들
    count                                   캔들 개수(최대 200개까지 요청 가능)

    [Response]
    market	                                마켓명	String
    candle_date_time_utc	                캔들 기준 시각(UTC 기준)	String
    candle_date_time_kst	                캔들 기준 시각(KST 기준)	String
    opening_price	                        시가	Double
    high_price	                            고가	Double
    low_price	                            저가	Double
    trade_price	                            종가	Double
    timestamp	                            해당 캔들에서 마지막 틱이 저장된 시각	Long
    candle_acc_trade_price	                누적 거래 금액	Double
    candle_acc_trade_volume	                누적 거래량	Double
    unit	                                분 단위(유닛)	Integer
    """

    url = f'candles/minutes/{minute}'
    query = kwargs['query']
    return quotation(url=url, query=query)

# 일봉 조회
def candle_day(**kwargs):
    """
    [Require]
    * market                                마켓 코드
    to                                      마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ss'Z' or yyyy-MM-dd HH:mm:ss. 비워서 요청시 가장 최근 캔들
    count                                   캔들 개수
    convertingPriceUnit                     종가 환산 화폐 단위 (생략 가능, KRW로 명시할 시 원화 환산 가격을 반환.)

    [Response]
    market	                                마켓명
    candle_date_time_utc	                캔들 기준 시각(UTC 기준)
    candle_date_time_kst	                캔들 기준 시각(KST 기준)
    opening_price	                        시가
    high_price	                            고가
    low_price	                            저가
    trade_price	                            종가
    timestamp	                            마지막 틱이 저장된 시각
    candle_acc_trade_price	                누적 거래 금액
    candle_acc_trade_volume	                누적 거래량
    prev_closing_price	                    전일 종가(UTC 0시 기준)
    change_price	                        전일 종가 대비 변화 금액
    change_rate	                            전일 종가 대비 변화량
    converted_trade_price	                종가 환산 화폐 단위로 환산된 가격(요청에 convertingPriceUnit 파라미터 없을 시 해당 필드 포함되지 않음.)
    """

    url = 'candles/days'
    query = kwargs['query']
    return quotation(url=url, query=query)

# 주봉 조회
def candle_week(**kwargs):
    """
    [Require]
    * market                                마켓 코드
    to                                      마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ss'Z' or yyyy-MM-dd HH:mm:ss. 비워서 요청시 가장 최근 캔들
    count                                   캔들 개수

    [Response]
    market	                                마켓명
    candle_date_time_utc	                캔들 기준 시각(UTC 기준)
    candle_date_time_kst	                캔들 기준 시각(KST 기준)
    opening_price	                        시가
    high_price	                            고가
    low_price	                            저가
    trade_price	                            종가
    timestamp	                            마지막 틱이 저장된 시각
    candle_acc_trade_price	                누적 거래 금액
    candle_acc_trade_volume	                누적 거래량
    first_day_of_period	                    캔들 기간의 가장 첫 날
    """

    url = 'candles/weeks'
    query = kwargs['query']
    return quotation(url=url, query=query)

# 월봉 조회
def candle_month(**kwargs):
    """
    [Require]
    * market                                마켓 코드
    to                                      마지막 캔들 시각 (exclusive). 포맷 : yyyy-MM-dd'T'HH:mm:ss'Z' or yyyy-MM-dd HH:mm:ss. 비워서 요청시 가장 최근 캔들
    count                                   캔들 개수

    [Response]
    market	                                마켓명
    candle_date_time_utc	                캔들 기준 시각(UTC 기준)
    candle_date_time_kst	                캔들 기준 시각(KST 기준)
    opening_price	                        시가
    high_price	                            고가
    low_price	                            저가
    trade_price	                            종가
    timestamp	                            마지막 틱이 저장된 시각
    candle_acc_trade_price	                누적 거래 금액
    candle_acc_trade_volume	                누적 거래량
    first_day_of_period	                    캔들 기간의 가장 첫 날
    """

    url = 'candles/months'
    query = kwargs['query']
    return quotation(url=url, query=query)

# 최근 체결 내역 조회
def trades_tick(**kwargs):
    """
    [Require]
    * market                                마켓 코드
    to                                      마지막 체결 시각. 형식 : [HHmmss 또는 HH:mm:ss]. 비워서 요청시 가장 최근 데이터
    count                                   체결 개수
    cursor                                  페이지네이션 커서
    dayAgo                                  최근 체결 날짜 기준 7일 이내의 이전 데이터 조회 가능. 비워서 요청 시 가장 최근 체결 날짜 반환. (범위: 1 ~ 7))

    [Response]
    trade_date_utc	                        체결 일자(UTC 기준)
    trade_time_utc	                        체결 시각(UTC 기준)
    timestamp	                            체결 타임스탬프
    trade_price	                            체결 가격
    trade_volume	                        체결량
    prev_closing_price	                    전일 종가
    change_price	                        변화량
    ask_bid	                                매도/매수
    sequential_id	                        체결 번호(Unique)
    """

    url = 'trades/ticks'
    query = kwargs['query']
    return quotation(url=url, query=query)

# 현재가 조회
def ticker(**kwargs):
    """
    [Require]
    * markets                               반점으로 구분되는 마켓 코드

    [Response]
    market	                                종목 구분 코드
    trade_date	                            최근 거래 일자(UTC)
    trade_time	                            최근 거래 시각(UTC)
    trade_date_kst	                        최근 거래 일자(KST)
    trade_time_kst	                        최근 거래 시각(KST)
    opening_price	                        시가
    high_price	                            고가
    low_price	                            저가
    trade_price	                            종가
    prev_closing_price	                    전일 종가
    change
    ㄴ EVEN : 보합
    ㄴ RISE : 상승
    ㄴ FALL : 하락	String
    change_price	                        변화액의 절대값
    change_rate	                            변화율의 절대값
    signed_change_price	                    부호가 있는 변화액
    signed_change_rate	                    부호가 있는 변화율
    trade_volume	                        가장 최근 거래량
    acc_trade_price	                        누적 거래대금(UTC 0시 기준)
    acc_trade_price_24h	                    24시간 누적 거래대금
    acc_trade_volume	                    누적 거래량(UTC 0시 기준)
    acc_trade_volume_24h	                24시간 누적 거래량
    highest_52_week_price	                52주 신고가
    highest_52_week_date	                52주 신고가 달성일
    lowest_52_week_price	                52주 신저가
    lowest_52_week_date	                    52주 신저가 달성일
    timestamp	                            타임스탬프
    """

    url = 'ticker'
    query = kwargs['query']
    return quotation(url=url, query=query)

# 호가 정보 조회
def orderbook(**kwargs):
    """
    [Require]
    * markets                               마켓 코드 목록

    [Response]
    market	                                마켓 코드
    timestamp	                            호가 생성 시각
    total_ask_size	                        호가 매도 총 잔량
    total_bid_size	                        호가 매수 총 잔량
    orderbook_units	                        호가
    ask_price	                            매도호가
    bid_price	                            매수호가
    ask_size	                            매도 잔량
    bid_size	                            매수 잔량
    """

    url = 'orderbook'
    query = kwargs['query']
    return quotation(url=url, query=query)

# query = {
#     '': ''
# }

# print(orders_chance(query=query))
# print(accounts())
# print(order(query=query))
# print(orders(query=query))
# print(order_cancel(query=query))
# print(order_place(query=query))
# print(withdraws(query=query))
# print(withdraw(query=query))
# print(withdraws_chance(query=query))
# print(withdraws_coin(query=query))
# print(withdraws_krw(query=query))
# print(deposits(query=query))
# print(deposit(query=query))
# print(deposits_generate(query=query))
# print(deposits_coin_addresses(query=query))
# print(deposit_coin_address(query=query))
# print(deposits_krw(query=query))
# print(status_wallet())
# print(api_keys())

# print(market_all())
# print(candle_minute(1, query=query))
# print(candle_day(query=query))
# print(candle_week(query=query))
# print(candle_month(query=query))
# print(trades_tick(query=query))
# print(ticker(query=query))
# print(orderbook(query=query))