from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import tempfile

import time

import shutil
from rtmbot.core import Plugin

from rq import Queue
from redis import Redis
from slackclient import SlackClient
from subprocess import call

redis_conn = Redis()
q = Queue(connection=redis_conn)


def make_github_attachment(slack_token, channel, user, repo, tree):
    sc = SlackClient(slack_token)
    dir = tempfile.mkdtemp()
    call(['git','clone','--depth=1','-b',tree,'git@github.com:{}/{}.git'.format(user, repo),dir], env={"PATH": "/usr/bin",
                                                                                                       "GIT_SSH_COMMAND": 'ssh -i {}'.format(os.path.join(os.getcwd(), 'id_rsa'))})
    call(['docker','run','--rm','-v','{}:/data'.format(dir),'psmit/latexmk','-outdir=build'])
    returns=[]
    for file in os.listdir(os.path.join(dir, 'build')):
        if file.endswith(".pdf"):
            returns.append(sc.api_call("files.upload", filename=file, channels=channel, file=open(os.path.join(dir, 'build', file), 'rb') ))
    shutil.rmtree(dir)
    return returns


class PdfGithubPlugin(Plugin):

    def process_message(self, data):

        if 'attachments' in data:
            print("found attachments")
            for attachment in data['attachments']:
                print("in attachment")
                print(attachment)
                if 'pretext' in attachment and 'ommit' in attachment['pretext']:
                    print("before match")
                    print(attachment['pretext'])
                    m = re.match(".*https://github.com/([a-z_-]*)/([a-z_-]*)/tree/([a-z_-]*)", attachment['pretext'])
                    if m is not None:
                        print("Match")
                        job = q.enqueue(make_github_attachment, self.slack_client.token, data['channel'], m.group(1),m.group(2),m.group(3))
                        print(job.result)
                        time.sleep(3)
                        print(job.result)

        print(data)

