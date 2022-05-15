import re
import smtplib
import mimetypes
from email.utils import formataddr
from email.message import EmailMessage
from string import Template
from os.path import exists
from pathlib import Path
from string import digits
from urllib.request import urlopen
from urllib.parse import urlparse
from textwrap import dedent
from sched import scheduler
from time import time, sleep
from dataclasses import dataclass, field
from typing import Tuple, List, Union, Optional
from errors import InvalidPathError, UnmatchedImageNumberError

IMG_URL_PATTERN = re.compile(r'https?://.*\.(?:jpg|jpeg|png|tiff|bmp|svg|gif|webp|raw)')


def is_img(url):
    return IMG_URL_PATTERN.match(url)


def split_num_text(s):
    head = s.lstrip(digits)
    tail = int(s[:0 - len(head)])
    return tail, head


def parse_freq(unit, n):
    return {
        'ds': 0.1, 's': 1, 'm': 60, 'h': 60 * 60,
        'd': 60 * 60 * 24, 'w': 60 * 60 * 24 * 7
    }[unit] * n


def parse_attr(size_attrs):
    for attr in size_attrs:
        prop = 'width' if attr[0] == 'w' else 'height'
        yield f'{prop}="{int(attr[1:])}"'


def make_tuple(content):
    return content if isinstance(content, tuple) else tuple(content) \
        if isinstance(content, (list, set)) else (content,)


def _get_attachments(attrs):
    for path in attrs:
        if is_img(path):
            r = urlopen(path)
            mtype = r.getheader('Content-Type')
            content = r.read()
            path = urlparse(path).path[1:]
        else:
            p = Path(path)
            mtype = mimetypes.guess_type(path)[0]
            content = p.read() if mtype == 'text' else p.read_bytes()

        stype = mtype.split('/')[1]
        yield content, mtype, stype, path


@dataclass(frozen=True)
class Info:
    recipients: Union[str, Tuple[str]]
    name: str
    subject: str
    body: str
    images: Union[str, Tuple[str]] = field(default_factory=tuple)
    attachments: Union[str, Tuple[str]] = field(default_factory=tuple)
    font_name: str = 'Verdana'
    font_size: int = 12

    def __post_init__(self):
        object.__setattr__(self, 'recipients', make_tuple(self.recipients))
        object.__setattr__(self, 'images', make_tuple(self.images))
        object.__setattr__(self, 'attachments', make_tuple(self.attachments))


class Sender:
    """Gmail sender class"""
    mimetypes.add_type('text/markdown', '.md')

    def __init__(self, sender: str, app_pwd: str, close_after: Optional[int] = None):
        self.sender = sender
        self.app_pwd = app_pwd
        self.limit = close_after
        self.conn = smtplib.SMTP('smtp.gmail.com', 587)
        self.conn.ehlo()
        self.conn.starttls()
        self.conn.login(sender, app_pwd)
        self._img_files = {}
        self._counter = 0
        self._s = scheduler(time, sleep)
        self._cache = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def send(self, info: Info, every: Optional[str] = None, mail_n: int = 3) -> None:
        if msg := self._cache.get(info):
            self._counter += 1
            return self._send_mail(msg, every, mail_n)

        body = info.body
        for string, link in re.findall(r'\[(.+?)]\((.+?)\)', body):
            text = f'[{string}]({link})'
            path = f'<a href="{link}" target="_blank">{string}</a>'
            body = body.replace(text, path)

        msg = EmailMessage()
        msg['Subject'] = info.subject
        msg['From'] = formataddr((info.name, self.sender))
        msg['To'] = info.recipients if isinstance(info.recipients, str) \
            else ','.join(info.recipients)
        msg.set_content(info.body)

        imgs = info.images
        img_nums = [int(i) for i in re.findall(r'\$img(\d)', body)]

        if len(img_nums) != len(imgs) and len(set(img_nums)) != len(imgs):
            raise UnmatchedImageNumberError(len(img_nums), len(imgs))

        template = Template(dedent(f'''\
                    <html>
                        <body>
                            <pre style="font-size: {info.font_size}px"><font face="{info.font_name},
                                   sans-serif, Times New Roman, Georgia, monospace">{body}</font></pre>
                        </body>
                    </html>'''))

        msg.add_alternative(self._get_template(template, imgs, img_nums), subtype='html')
        for img_cid, (path, img_ext, img_con) in self._img_files.items():
            msg.get_body().add_related(img_con, 'image', img_ext, cid=img_cid, filename=path)

        attas = info.attachments
        for content, mtype, stype, path in _get_attachments(attas):
            msg.add_attachment(content, mtype, stype, filename=path)

        self._cache[info] = msg
        self._counter += 1
        self._send_mail(msg, every, mail_n)

    def _get_template(self, template: Template, imgs: Tuple[str], img_nums: List[int]) -> str:
        img_maps = {}
        for img_n in img_nums:
            img = imgs[img_n - 1]

            if isinstance(img, str):
                path, dims = img, ''
            else:
                path, dims = img[0], ' '.join(parse_attr(img[1:]))

            if exists(path):
                p = Path(path)
                img_cid, img_ext, img_con = f'<img{img_n}>', p.suffix[1:], p.read_bytes()
                self._img_files[img_cid] = (path, img_ext, img_con)
                img_maps[f'img{img_n}'] = f'<img src="cid:img{img_n}" {dims}/>'
            elif is_img(path):
                img_maps[f'img{img_n}'] = f'<img src="{path}" {dims}/>'
            else:
                raise InvalidPathError(path)

        return template.substitute(img_maps)

    def _send_mail(self, msg: EmailMessage, every: Union[str, None], mail_n: int) -> None:
        if not every:
            self.conn.send_message(msg)
        else:
            n, unit = split_num_text(every)
            t = parse_freq(unit, n)

            def send_wrapper():
                nonlocal mail_counter
                self.conn.send_message(msg)
                if mail_counter < mail_n:
                    mail_counter += 1
                    self._s.enter(t, 1, send_wrapper)

            mail_counter = 1
            send_wrapper()
            self._s.run()

        if self._counter == self.limit:
            self.close()

    def close(self):
        self.conn.quit()
