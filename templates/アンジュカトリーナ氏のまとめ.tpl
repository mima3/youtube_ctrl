<h2>目的</h2>
本記事は視聴者の片腕を代価として彼氏を企んでいる錬金術師、アンジュ・カトリーナ氏のYotubeのライブチャットを解析したものである。

<h2>集計結果</h2>
アンジュ・カトリーナ氏の動画に対するライブチャットのコメント数を集計したものは下記の通りである。
<table border=1>
    <tr>
      <th>動画</th>
      <th>合計</th>
      <th>1分間<br>平均</th>
      <th>1分間<br>中央値</th>
      <th>1分間<br>分散</th>
    </tr>
    {% for item in json_data %}
        <tr>
           <td><a href="https://www.youtube.com/watch?v={{ item.id | e}}">{{ item.title | e}}</a></td>
           <td align="right">{{ "{:,d}".format(item.sum) }}</td>
           <td align="right">{{ "{:,.2f}".format(item.mean) }}</td>
           <td align="right">{{ "{:,.2f}".format(item.median) }}</td>
           <td align="right">{{ "{:,.2f}".format(item.stdev) }}</td>
        </tr>
    {% endfor %}
</table>
<h2>各動画の見どころ</h2>
{% for item in json_data %}
    <h3><a href="https://www.youtube.com/watch?v={{ item.id | e}}">{{ item.title | e}}</a></h3>
    <table border=1>
        <tr>
            <th>開始位置</th>
            <th>頻出単語</th>
        </tr>
        {% for highlite in item.highlite %}
            <tr>
                <td>
                    <a href="https://www.youtube.com/watch?v={{ item.id | e}}&t={{"{:.0f}".format(highlite.start/1000)}}">
                        {{"{:.0f}".format(highlite.start/1000)}}
                    </a>
                </td>
                <td>
                    {% for word in highlite.words %}{{ word.word }}({{ "{:,d}".format(word.count) }}), {% endfor %}
                </td>
            </tr>
        {% endfor %}
{% endfor %}
