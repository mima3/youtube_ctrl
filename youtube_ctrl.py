"""Youtubeのライブからアーカイブコメントを取得してDBに格納する"""
import sys
import http.client
from datetime import datetime
from datetime import timedelta
import youtube_api
import youtube_db
from peewee import *


db = youtube_db.YoutubeDb()
db.connect('youtube.sqlite')


def callback_analyze_live(items):
    """ライブのアーカイブからチャット情報を取得する際のコールバック"""
    with db.database.transaction():
        youtube_db.LiveChatMessage.insert_many(items).execute()


def analyze_live(api_key, video_id):
    """ライブのアーカイブからチャット情報を取得する"""
    conn = http.client.HTTPSConnection("www.googleapis.com", 443)
    video_info = youtube_api.get_video_info(conn, api_key, video_id)
    print(video_info['items'][0]['snippet']['title'])
    try:
        video_rec = youtube_db.Video.get(youtube_db.Video.video_id == video_id)
        video_rec.title = video_info['items'][0]['snippet']['title']
        video_rec.channel_id = video_info['items'][0]['snippet']['channelId']
        video_rec.published_at = video_info['items'][0]['snippet']['publishedAt']
        video_rec.save()
    except youtube_db.DoesNotExist:
        video_rec = youtube_db.Video.create(
            video_id=video_id,
            title=video_info['items'][0]['snippet']['title'],
            channel_id=video_info['items'][0]['snippet']['channelId'],
            published_at=video_info['items'][0]['snippet']['publishedAt']
            
        )
    conn.close()

    # 動画に紐づくチャットメッセージをいったん消す
    youtube_db.LiveChatMessage.delete().where(youtube_db.LiveChatMessage.video_id == video_id).execute()
    youtube_api.get_archive_live_chat(video_id, callback_analyze_live)


def analyze_channel(api_key, channel_id):
    """チャンネルからビデオの一覧を取り出してアーカイブされたライブチャットを取得する"""
    conn = http.client.HTTPSConnection("www.googleapis.com", 443)
    published_after = None
    max_published_after = youtube_db.Video.select(
        fn.MAX(youtube_db.Video.published_at)
    ).where(youtube_db.Video.channel_id == channel_id).scalar()
    if not max_published_after is None:
        tmp_dt = youtube_api.convert_string_to_datetime(max_published_after)
        tmp_dt = tmp_dt - timedelta(days=1)
        published_after = youtube_api.convert_datetime_to_string(tmp_dt)
    print(channel_id, published_after)
    video_list = youtube_api.get_all_channel_video_list(conn, api_key, channel_id, published_after=published_after)
    conn.close()
    print(video_list)
    for video in video_list:
        print(video['videoId'] , '\t', video['title'])
    for video in video_list:
        analyze_live(api_key, video['videoId'])


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    if argc != 4:
        print("Usage #python %s video/channel api_key video_id/channel_id" % argvs[0])
        exit()
    if argvs[1] == 'video':
        analyze_live(argvs[2], argvs[3])
    if argvs[1] == 'channel':
        analyze_channel(argvs[2], argvs[3])
