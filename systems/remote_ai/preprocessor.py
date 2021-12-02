from collections import Counter
from django.conf import settings

import string
import re


class MetaPreprocessor(type):

    def run(self, text):
        text = self.remove_punctuation(text.lower())
        text = self.remove_stopwords(text)
        text = self.remove_freqwords(text)
        text = self.remove_urls(text)
        return text


    def remove_punctuation(self, text):
        return text.translate(str.maketrans(" ", " ", string.punctuation))

    def remove_stopwords(self, text):
        text = [
            word
            for word in text.split()
            if word not in settings.REMOTE_AI_STOPWORDS and len(word) > 2
        ]
        return " ".join(text)

    def remove_freqwords(self, text):
        count = Counter()

        for t in text:
            for word in t.split():
                count[word] += 1

        freq_words = set([w for (w, wc) in count.most_common(10)])

        return " ".join(
            [word for word in str(text).split() if word not in freq_words]
        )

    def remove_urls(self, text):
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub(r'', text)


class Preprocessor(object, metaclass = MetaPreprocessor):
    pass
