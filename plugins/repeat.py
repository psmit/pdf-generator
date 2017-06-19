from __future__ import print_function
from __future__ import unicode_literals

from rtmbot.core import Plugin


class RepeatPlugin(Plugin):

    def process_message(self, data):
        print(data)
        return
        if data['channel'].startswith("D"):
            self.outputs.append(
                [data['channel'], 'from repeat1 "{}" in channel {}'.format(
                    data['text'], data['channel']
                )]
            )
