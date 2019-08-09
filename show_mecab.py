"""Mecabによるチャットの解析"""
import sys
import codecs
from collections import defaultdict
import MeCab
import youtube_db


def main(argvs, argc):
    """Mecabによるチャットの解析"""
    if argc < 2:
        print("Usage #python %s video_id1 video_id2 ..." % argvs[0])
        return 1
    video_list = []
    for id in argvs[1:]:
        video_list.append(id)

    db = youtube_db.YoutubeDb()
    db.connect('youtube.sqlite')
    records = youtube_db.LiveChatMessage.select().where(youtube_db.LiveChatMessage.video_id << video_list)
    mecab = MeCab.Tagger('')
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
        if v < 10:
            break
        print("%s\t%d" % (k, v))

if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
