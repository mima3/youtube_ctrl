"""指定のDBの時間ごとのコメント数を確認する"""
import sys
import youtube_db
import matplotlib.pyplot as plt


def main(argvs, argc):
    """指定のDBの時間ごとのコメント数を確認する"""
    if argc != 3:
        print("Usage #python %s video_id interval_msec" % argvs[0])
        return 1
    video_id = argvs[1]
    db = youtube_db.YoutubeDb()
    db.connect('youtube.sqlite')
    interval_msec = int(argvs[2])
    items = db.get_histogram(video_id, interval_msec)
    x = []
    y = []
    label = []
    i = 1
    ltmp = 0
    for item in items:
        if i == 1 or i == len(items) or (i % (len(items) // 10) == 0):
            label.append(ltmp)
        else:
            label.append('')
        print(ltmp, '\t', item)
        y.append(item)
        x.append(i)
        i = i + 1
        ltmp = ltmp + (interval_msec / 1000)
    plt.bar(x, y)
    plt.xticks(x, label)
    plt.show()


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
