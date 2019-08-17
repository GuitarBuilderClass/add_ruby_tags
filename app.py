import os
from datetime import date, datetime

import responder

from src.add_phonetics import Phonetic

api = responder.API(
    templates_dir='static/templates',
    auto_escape=True,
)


class Revision:
    def __init__(self):
        self.p = Phonetic()

    def on_get(self, req, resp) -> None:
        raw_text = "樹木希林はFUJIカラーで写せない遠いお正月へ旅立ったよ。"
        converted_text = self.p.export_html(raw_text)
        resp.html = api.template('index.html',
                                 raw_text=raw_text,
                                 converted_text=converted_text)

    async def on_post(self, req, resp) -> None:
        data: object = await req.media(format='form')
        raw_text: str = data['raw-text'].replace("<",
                                                 "&lt").replace(">", "&gt")
        converted_text = self.p.export_html(raw_text)

        @api.background.task
        def log():
            today = date.today()
            exec_time = datetime.today()
            raw = '-'.join(raw_text.splitlines())
            converted = '-'.join(converted_text.splitlines())
            with open(f'./logs/{today}.tsv', mode='a',
                      encoding='utf-8') as log:
                log.write(f"{exec_time}\t{raw}\t{converted}\n")

        log()
        resp.content = api.template('index.html',
                                    raw_text=raw_text,
                                    converted_text=converted_text)


api.add_route('', Revision())
api.add_route('/', Revision())

if __name__ == '__main__':
    api.run(address='0.0.0.0',
            port=5042,
            )
