# First have to monkey patch ntlk to find it data in a local directory
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
import os
from nltk import data
from SummaryTweets.tf_idf import tfidf


current_path = os.path.dirname(os.path.realpath(__file__))
nltk_data = os.path.join(current_path, 'nltk_data', '')
data.path = [nltk_data]




from flask import Flask, make_response, redirect, abort
from flask.ext.restful import Resource, Api, reqparse
from flask.ext.restful.representations.json import output_json


from sumy._compat import to_unicode
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.sum_basic import SumBasicSummarizer
from sumy.summarizers.kl import KLSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


from newspaper import Article
from newspaper import nlp
app = Flask(__name__)
app.config['DEBUG'] = True


def output_text(data, code, headers):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


class MyApi(Api):
    def __init__(self, *args, **kwargs):
        super(MyApi, self).__init__(*args, **kwargs)
        self.representations = {
            'application/json': output_json,
        }

api = MyApi(app)

LANGUAGE = "english"
SENTENCES_COUNT = 5
length = 175


article_parser = reqparse.RequestParser()
article_parser.add_argument('url', type=unicode, help='The url of the site to scrape')


class ArticleSimple(Resource):
    def get(self):
        args = article_parser.parse_args()
        url = args['url']
        article = Article(url)
        article.download()

        if article.html == "":
            abort(404)
        else:
            article.parse()
            article.nlp()
            program = tfidf()
            summary_sents = nlp.summarize(title=article.title, text=article.text)
            parser = PlaintextParser.from_string(article.text, Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            lsasummarizer = LsaSummarizer(stemmer)
            lsasummarizer.stop_words = get_stop_words(LANGUAGE)

            lexsummarizer = LexRankSummarizer(stemmer)
            lexsummarizer.stop_words = get_stop_words(LANGUAGE)



            luhnsummarizer = LuhnSummarizer(stemmer)
            luhnsummarizer.stop_words = get_stop_words(LANGUAGE)

            edmundsonsummarizer = EdmundsonSummarizer(stemmer)
            edmundsonsummarizer.stop_words = get_stop_words(LANGUAGE)



            textsummarizer = TextRankSummarizer(stemmer)
            textsummarizer.stop_words = get_stop_words(LANGUAGE)



            lsasummary =[]
            lsasentences = lsasummarizer(parser.document, SENTENCES_COUNT)
            for lsasentence in lsasentences:
                lsasummary.append(to_unicode(lsasentence))



            splitsents =  ' '.join(nlp.split_sentences(article.text))


            lexsummary =[]
            lexsentences = lexsummarizer(parser.document, SENTENCES_COUNT)
            for lexsentence in lexsentences:
                lexsummary.append(to_unicode(lexsentence))

            luhnsummary =[]
            luhnsentences = luhnsummarizer(parser.document, SENTENCES_COUNT)
            for luhnsentence in luhnsentences:
                luhnsummary.append(to_unicode(luhnsentence))



            textsummary =[]
            textsentences = textsummarizer(parser.document, SENTENCES_COUNT)
            for textsentence in textsentences:
                textsummary.append(to_unicode(textsentence))

            #print (summary)
            edmundsonsummary =[]
            edmundsonsummarizer.bonus_words = parser.significant_words
            edmundsonsummarizer.stigma_words = parser.stigma_words
            edmundsonsummarizer.null_words = edmundsonsummarizer.stop_words
            edmundsonsentences = edmundsonsummarizer(parser.document, SENTENCES_COUNT)
            for edmundsonsentence in edmundsonsentences:
                edmundsonsummary.append(to_unicode(edmundsonsentence))





            processed_text = program.read_input_text(splitsents)
            scores = program.tf_idf(processed_text)

            summary = program.total_sent_score(processed_text, scores)
            dropped = program.compressor.simple_drop(summary, processed_text, scores)

            compressed = program.compressor.compress_sentences(dropped)
            output = program.output_sentences(compressed, length)
            data = {
                'url': article.url,
                'title': article.title,
                'top_image': article.top_img,
                'images': [x for x in article.imgs],
                'text': article.text,
                'html': article.html,
                'keywords': article.keywords,
                'authors': article.authors,
                'summary1': output,
                'summary2': lexsummary,
                'summary3': edmundsonsummary,
                'summary4': luhnsummary,
                'summary5': lsasummary,
                'summary6': textsummary,
                'summary7': summary_sents,
                'meta_description': article.meta_description,
                'meta_lang': article.meta_lang,
                'meta_favicon': article.meta_favicon,
                'meta_keywords': article.meta_keywords,
                'canonical_link': article.canonical_link,
                'tags': [unicode(x) for x in article.tags],
                'movies': article.movies,
                'additional_data': article.additional_data,
            }


            return output_json(data, 200, {})







api.add_resource(ArticleSimple, '/article')


if __name__ == '__main__':
    app.run(debug=True)
