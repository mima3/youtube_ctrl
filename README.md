依存パッケージ：
 - beautifulsoup4                4.8.0
 - lxml                          4.4.0
 - mecab-python-windows          0.996.3
 - peewee                        3.9.6
 - urllib3                       1.25.3


チャンネルまたはビデオからライブチャットの情報を抜き出す。
```
python youtube_ctrl.py video/channel api_key video_id/channel_id
```

チャンネルのライブチャットの解析
```
python youtube_statistics.py チャンネルID 出力先JSONファイル
```

WordPressの追加
```
python post_wordpress.py URL ユーザ名 パスワード ブログタイトル json
```

WordPressの更新
```
python update_wordpress.py URL ユーザ名 パスワード ブログタイトル ブログID json
```

WordPressでの出力例
http://needtec.sakura.ne.jp/wod07672/2019/10/21/%e3%82%a2%e3%83%b3%e3%82%b8%e3%83%a5%e3%82%ab%e3%83%88%e3%83%aa%e3%83%bc%e3%83%8a%e6%b0%8f%e3%81%ae%e3%81%be%e3%81%a8%e3%82%81/

参考  
https://developers.google.com/youtube/v3/docs/search/list?hl=ja  
https://support.google.com/youtube/forum/AAAAiuErobU8A1V4NqExIE/?hl=en&gpf=%23!topic%2Fyoutube%2F8A1V4NqExIE  
https://qiita.com/yuji_saito/items/8f472dcd785c1fadf666  
http://watagassy.hatenablog.com/entry/2018/10/08/132939  
