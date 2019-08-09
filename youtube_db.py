"""youtubeのメッセージ記録用DB操作."""
from peewee import *
from playhouse.sqlite_ext import *
from statistics import mean, median,variance,stdev
#import logging
#logger = logging.getLogger('peewee')
#logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler())


database_proxy = Proxy()


class Video(Model):
    """動画情報"""
    video_id = CharField(primary_key=True, unique=True)
    title = CharField()
    channel_id = CharField(index=True)
    published_at = CharField()


    class Meta:
        """Moviesのメタ情報"""
        database = database_proxy


class LiveChatMessage(Model):
    """Live Chatのメッセージ"""
    id = AutoIncrementField()
    video_id = ForeignKeyField(Video, related_name='related_id', index=True, null=False)
    author = CharField()
    message = CharField()
    offset_time_msec = IntegerField()
    purchase_amount = CharField()

    class Meta:
        """LiveChatMessagesのメタ情報"""
        database = database_proxy


class YoutubeDb:
    """Youtube用のDB操作"""
    database = None

    def connect(self, db_path):
        """SQLiteへの接続"""
        self.database = SqliteDatabase(db_path)
        database_proxy.initialize(self.database)
        self.database.create_tables([Video, LiveChatMessage])


    def get_histogram(self, video_id, interval_msec):
        """時間ごとのヒストグラムを作成"""
        max_time = LiveChatMessage.select(
            fn.MAX(LiveChatMessage.offset_time_msec)
        ).where(LiveChatMessage.video_id == video_id).scalar()
        if max_time is None:
            return []
        tmp_start = 0
        ret = []
        while tmp_start < max_time:
            data = (
                LiveChatMessage.select().where(
                    (LiveChatMessage.video_id == video_id) &
                    (LiveChatMessage.offset_time_msec >= tmp_start) &
                    (LiveChatMessage.offset_time_msec < tmp_start + interval_msec)
                ).count()
            )
            ret.append(data)
            tmp_start = tmp_start + interval_msec
        return ret


    def get_histogram_all(self, video_id, interval_msec):
        """時間ごとのヒストグラムを作成"""
        max_time = LiveChatMessage.select(
            fn.MAX(LiveChatMessage.offset_time_msec)
        ).where(LiveChatMessage.video_id == video_id).scalar()
        if max_time is None:
            return []
        tmp_start = 0
        ret = []
        while tmp_start < max_time:
            data = (
                LiveChatMessage.select().where(
                    (LiveChatMessage.video_id == video_id) &
                    (LiveChatMessage.offset_time_msec >= tmp_start) &
                    (LiveChatMessage.offset_time_msec < tmp_start + interval_msec)
                )
            )
            ret.append({'start': tmp_start, 'end': tmp_start + interval_msec, 'data': data, 'count': len(data)})
            tmp_start = tmp_start + interval_msec
        return ret
