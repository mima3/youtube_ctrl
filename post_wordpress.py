import sys
import json
from jinja2 import Environment, FileSystemLoader
from wordpress_ctrl import WordPressCtrl,WordPressError


def main(argvs, argc):
    """WORDPRESS投稿"""
    if argc != 6:
        print("Usage #python %s wordプレスurl ユーザ名 パスワード ブログタイトル JSONパス" % argvs[0])
        return 1
    url = argvs[1]
    user = argvs[2]
    password = argvs[3]
    title = argvs[4]
    json_path = argvs[5]

    env = Environment(loader = FileSystemLoader('./templates'))
    template = env.get_template(f'{title}.tpl')

    with open(json_path,  mode='r', encoding='utf8') as fp:
        json_data = json.load(fp)
    wpctrl = WordPressCtrl(url, user, password)
    try:
        wpres = wpctrl.add_post(title, template.render(json_data=json_data), [6], [])
        print(wpres['id'])
    except WordPressError as ex:
        print(ex.status_code, ex.reason, ex.message)


if __name__ == '__main__':
    argvs = sys.argv
    argc = len(argvs)
    sys.exit(main(argvs, argc))
