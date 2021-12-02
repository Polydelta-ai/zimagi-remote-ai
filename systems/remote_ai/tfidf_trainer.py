from sklearn.feature_extraction.text import TfidfVectorizer

import numpy
import pickle


class TfidfTrainer(object):

    def __init__(self, model_provider):
        self.model_provider = model_provider
        self.load()


    def word_vectorizer_file(self, vectorizer_path):
        return "{}_{}_{}".format(vectorizer_path, self.model_provider.name, 'word_vectorizer.pk')

    def char_vectorizer_file(self, vectorizer_path):
        return "{}_{}_{}".format(vectorizer_path, self.model_provider.name, 'char_vectorizer.pk')


    def load(self):
        with self.model_provider.get_model_project() as project:
            vectorizer_path = project.path(self.model_provider.instance.name)
            word_file = self.word_vectorizer_file(vectorizer_path)
            char_file = self.char_vectorizer_file(vectorizer_path)

            if project.exists(word_file):
                with open(word_file, "rb") as file:
                    self.word_vectorizer = pickle.load(file)

                with open(char_file, "rb") as file:
                    self.char_vectorizer = pickle.load(file)
            else:
                self.build_vectorizer()
                self.save()

    def save(self):
        with self.model_provider.get_model_project() as project:
            vectorizer_path = project.path(self.model_provider.instance.name)

            with open(self.word_vectorizer_file(vectorizer_path), "wb") as file:
                pickle.dump(self.word_vectorizer, file)

            with open(self.char_vectorizer_file(vectorizer_path), "wb") as file:
                pickle.dump(self.char_vectorizer, file)

    def remove(self):
        with self.model_provider.get_model_project() as project:
            vectorizer_path = project.path(self.model_provider.instance.name)

            project.remove(self.word_vectorizer_file(vectorizer_path))
            project.remove(self.char_vectorizer_file(vectorizer_path))


    def build_vectorizer(self):
        self.word_vectorizer = TfidfVectorizer(
            sublinear_tf = True,
            stop_words = "english",
            strip_accents = "unicode",
            lowercase = True,
            analyzer = "word",
            token_pattern = r"\w{1,}",
            ngram_range = (1, 3),
            dtype = numpy.float32,
            max_features = 8000
        )
        self.char_vectorizer = TfidfVectorizer(
            sublinear_tf = True,
            strip_accents = "unicode",
            lowercase = True,
            analyzer = "char_wb",
            ngram_range = (1, 4),
            dtype = numpy.float32,
            max_features = 5000
        )

    def fit(self, dataset):
        self.word_vectorizer.fit(dataset)
        self.char_vectorizer.fit(dataset)
        self.save()

    def transform(self, dataset):
        tfidf_word_data = self.word_vectorizer.transform(dataset).toarray()
        tfidf_char_data = self.char_vectorizer.transform(dataset).toarray()
        return numpy.hstack([ tfidf_word_data, tfidf_char_data ])
