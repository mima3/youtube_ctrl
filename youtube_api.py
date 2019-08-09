"""youtubeの操作を行う"""
import json
import traceback
from datetime import datetime
from datetime import timedelta
import requests
from bs4 import BeautifulSoup


def get_video_info(conn, api_key, video_id):
    """動画情報の取得"""
    conn_str = '/youtube/v3/videos?id={0}&key={1}&fields=items(id,snippet(channelId,title,categoryId,publishedAt),statistics)&part=snippet,statistics'.format(video_id, api_key)
    conn.request('GET', conn_str)
    res = conn.getresponse()
    if res.status != 200:
        raise Exception(res.status, res.reason)
    data = res.read().decode("utf-8")
    return json.loads(data)


def get_channel_video_list(conn, api_key, channel_id, published_before=None, published_after=None):
    """チャンネル中の動画一覧取得"""
    # 参考資料
    # https://developers.google.com/youtube/v3/docs/search/list?hl=ja
    # https://support.google.com/youtube/forum/AAAAiuErobU8A1V4NqExIE/?hl=en&gpf=%23!topic%2Fyoutube%2F8A1V4NqExIE
    # https://qiita.com/yuji_saito/items/8f472dcd785c1fadf666
    result = []
    conn_str = '/youtube/v3/search?part=snippet&channelId={0}&key={1}&maxResults=50&order=date&kind=video'.format(channel_id, api_key)
    print (conn_str)
    if published_before:
        conn_str = conn_str + '&publishedBefore=' + published_before
    if published_after:
        conn_str = conn_str + '&publishedAfter=' + published_after

    conn.request('GET', conn_str)
    res = conn.getresponse()
    if res.status != 200:
        raise Exception(res.status, res.reason)
    data = res.read().decode("utf-8")
    data = json.loads(data)
    for item in data['items']:
        if item['id']['kind'] == 'youtube#video':
            result.append({'videoId' : item['id']['videoId'], 'title':item['snippet']['title'], 'publishedAt':item['snippet']['publishedAt']})
    return result


def convert_string_to_datetime(str_dt):
    """文字を日付時刻型に変換"""
    date_time = datetime.strptime(str_dt, '%Y-%m-%dT%H:%M:%S.000Z')
    return date_time


def convert_datetime_to_string(date_time):
    """日付時刻型を文字に変換"""
    return date_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def get_all_channel_video_list(conn, api_key, channel_id, published_after=None):
    """チャンネル中の動画をすべて取得"""
    tmp_result = []
    result = get_channel_video_list(conn, api_key, channel_id, None, published_after)
    if not result:
        return result

    while 1:
        tmp_dt = convert_string_to_datetime(result[len(result)-1]['publishedAt'])
        tmp_dt = tmp_dt - timedelta(seconds=1)
        published_before = convert_datetime_to_string(tmp_dt)
        tmp_result = get_channel_video_list(conn, api_key, channel_id, published_before, published_after)
        if not tmp_result:
            return result
        result.extend(tmp_result)


def get_message_data(video_id, item):
    """["continuationContents"]["liveChatContinuation"]["actions"][1:]以下を解析"""
    message = ''
    purchase_amount = ''
    data = None
    # たぶん、全パターンの網羅はできていない
    if 'addLiveChatTickerItemAction' in item["replayChatItemAction"]["actions"][0]:
        if 'liveChatTextMessageRenderer' in item["replayChatItemAction"]["actions"][0]['addLiveChatTickerItemAction']['item']:
            data = item["replayChatItemAction"]["actions"][0]['addLiveChatTickerItemAction']['item']['liveChatTickerPaidMessageItemRenderer']['showItemEndpoint']['showLiveChatItemEndpoint']['renderer']
        if 'liveChatTickerPaidMessageItemRenderer' in item["replayChatItemAction"]["actions"][0]['addLiveChatTickerItemAction']['item']:
            data = item["replayChatItemAction"]["actions"][0]['addLiveChatTickerItemAction']['item']['liveChatTickerPaidMessageItemRenderer']['showItemEndpoint']['showLiveChatItemEndpoint']['renderer']['liveChatPaidMessageRenderer']
            purchase_amount = data['purchaseAmountText']['simpleText']
        if 'liveChatPlaceholderItemRenderer' in item["replayChatItemAction"]["actions"][0]['addLiveChatTickerItemAction']['item']:
            print(item)
            return None
    if 'addChatItemAction' in item["replayChatItemAction"]["actions"][0]:
        if 'liveChatTextMessageRenderer' in item["replayChatItemAction"]["actions"][0]['addChatItemAction']['item']:
            data = item["replayChatItemAction"]["actions"][0]['addChatItemAction']['item']['liveChatTextMessageRenderer']
        if 'liveChatPaidMessageRenderer' in item["replayChatItemAction"]["actions"][0]['addChatItemAction']['item']:
            data = item["replayChatItemAction"]["actions"][0]['addChatItemAction']['item']['liveChatPaidMessageRenderer']
            purchase_amount = data['purchaseAmountText']['simpleText']
        if 'liveChatPlaceholderItemRenderer' in item["replayChatItemAction"]["actions"][0]['addChatItemAction']['item']:
            print(item)
            return None

    if data is None:
        print(item)
        return None

    if 'message' in data:
        for msg in data['message']['runs']:
            if 'text' in msg:
                # emojiが来る可能性がある
                message = message + msg['text']
            else:
                print(data)
    author = data['authorName']['simpleText']
    offset_time_msec = item["replayChatItemAction"]["videoOffsetTimeMsec"]
    return {'video_id': video_id, 'message': message, 'author': author, 'offset_time_msec': offset_time_msec, 'purchase_amount': purchase_amount}


def get_archive_live_chat(video_id, callback):
    """アーカイブのライブチャットの取得"""
    target_url = 'https://www.youtube.com/watch?v=' + video_id
    result = []
    session = requests.Session()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

    # まず動画ページにrequestsを実行しhtmlソースを手に入れてlive_chat_replayの先頭のurlを入手
    html = requests.get(target_url)
    soup = BeautifulSoup(html.text, "html.parser")
    item = None
    next_url = None

    for iframe in soup.find_all("iframe"):
        if "live_chat_replay" in iframe["src"]:
            next_url = iframe["src"]

    if next_url is None:
        # ライブチャットの再生が無効になっている場合など.
        # 例：JRfVSFJhcLw　配信失敗により、アンジュがただただ病むだけ。
        print ('iframe src not found.')
        return

    while 1:
        try:
            html = session.get(next_url, headers=headers)
            soup = BeautifulSoup(html.text, "lxml")

            # 次に飛ぶurlのデータがある部分をfind_allで探してsplitで整形
            for scrp in soup.find_all("script"):
                if "window[\"ytInitialData\"]" in scrp.text:
                    dict_str = scrp.text.split(" = ")[1]

            # 辞書形式と認識すると簡単にデータを取得できるが, 末尾に邪魔なのがあるので消しておく（「空白2つ + \n + ;」を消す）
            dict_str = dict_str.rstrip("  \n;")
            dics = json.loads(dict_str)

            if not 'liveChatReplayContinuationData' in dics["continuationContents"]["liveChatContinuation"]["continuations"][0]:
                # 次のデータが存在しない
                return

            # "https://www.youtube.com/live_chat_replay?continuation=" + continue_url が次のlive_chat_replayのurl
            continue_url = dics["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]
            next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url
            # dics["continuationContents"]["liveChatContinuation"]["actions"]がコメントデータのリスト。先頭はノイズデータなので[1:]で保存
            for item in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
                rec = get_message_data(video_id, item)
                if not rec is None:
                    result.append(rec)

        # next_urlが入手できなくなったら終わり
        except:
            traceback.print_exc()
            print(item)
            break

        callback(result)
        result = []
