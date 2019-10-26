"""Mecabによるチャットの解析"""
import sys
import codecs
from collections import defaultdict
import MeCab
from statistics import mean, median,variance,stdev
from datetime import datetime
from datetime import timedelta
import youtube_api
import youtube_db
from peewee import *
import json


def analyze_word(mecab, records, limit_count):
    pos = ['名詞', '形容詞', '形容動詞', '感動詞', '動詞', '副詞']
    exclude = [
        'する',
        'いる',
        'http',
        'https',
        'co',
        'jp',
        'com'
    ]
    wordcount = defaultdict(int)
    result = []
    for rec in records:
        txt = rec.message
        node = mecab.parseToNode(txt)
        while node:
            fs = node.feature.split(",")
            if fs[0] in pos:
                word = (fs[6] != '*' and fs[6] or node.surface)
                word = word.strip()
                if word.isdigit() == False:
                    if len(word) != 1:
                        if word not in exclude:
                            wordcount[word] += 1
            node = node.next
    for k, v in sorted(wordcount.items(), key=lambda x: x[1], reverse=True):
        if v < limit_count:
            break
        result.append({'word' : k, 'count': v})
    return result


def main(argvs, argc):
    """Mecabによるチャットの解析"""
    if argc != 3:
        print("Usage #python %s channel_id 出力パス" % argvs[0])
        return 1
    channel_id = argvs[1]
    outpath = argvs[2]
    db = youtube_db.YoutubeDb()
    db.connect('youtube.sqlite')
    mecab = MeCab.Tagger('')

    video_list = youtube_db.Video.select().where(youtube_db.Video.channel_id == channel_id).order_by(youtube_db.Video.published_at)
    result = []
    for video in video_list:
        msg_cnt = []
        items = db.get_histogram_all(video.video_id, 60 * 1000)
        if not items:
            print (video.title + 'のライブチャットは取得できませんでした')
            continue
        for item in items:
            msg_cnt.append(item['count'])
        if len(msg_cnt) <= 2:
            continue
        ret = {
            'id' : video.video_id,
            'title' : video.title,
            'sum' : sum(msg_cnt),
            'mean' : mean(msg_cnt),
            'median' : median(msg_cnt),
            'variance' : variance(msg_cnt),
            'stdev' : stdev(msg_cnt),
            'highlite' : []
        }
        sorted_items = sorted(items, key=lambda x:x['count'], reverse=True)
        cnt = 0
        for item in sorted_items:
            cnt = cnt + 1
            if cnt > 5:
                break
            words = analyze_word(mecab, item['data'], 5)
            ret['highlite'].append({
                'start' : item['start'],
                'end' : item['end'],
                'count' : item['count'],
                'words' : words
            })
        result.append(ret)

    print ('title, id, sum, mean, median, stdev')
    for ret in result:
        print (ret['title'], ',', ret['id'], ',',ret['sum'], ',',ret['mean'], ',', ret['median'] ,',', ret['stdev'])

    print ('')
    for ret in result:
        print ('--------------------------------------')
        print (ret['title'], ',', ret['id'])
        for h in ret['highlite']:
            words = ''
            for w in h['words']:
                words = words + w['word'] + '(' + str(w['count']) + ') /'
            
            print (h['start'] / 1000, ',' , h['count'], ',', words)

    with open(outpath, mode='w', encoding='utf8') as fp:
        json.dump(result, fp, sort_keys = True, indent = 4)

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
