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
            'text': output_text,
            'application/json': output_json,
        }

api = MyApi(app)

LANGUAGE = "english"
SENTENCES_COUNT = 5
length = 134


article_parser = reqparse.RequestParser()
article_parser.add_argument('url', type=unicode, help='The url of the site to scrape')
article_parser.add_argument('format', type=unicode, help='Format of article in json/text', default='json')
article_parser.add_argument('markdownify', type=bool, help='Should the text of the article be markdown', default=True)
article_parser.add_argument('include_summary', type=bool, help='Should a nlp summary be included', default=False)
article_parser.add_argument('redirect', type=unicode, help='Should redirect to another program', default='')

class ArticleSimple(Resource):
    def get(self):
        args = article_parser.parse_args()
        url = args['url']
        output_format = args['format']
        article = Article(url, keep_article_html=True)
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
                'html': article.article_html,
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

            if output_format == 'json':
                return output_json(data, 200, {})

            if output_format == 'text':
                output = u'---\n'
                output += u'link: %s\n' % (article.url)
                output += u'title: %s\n' % (article.title)
                output += u'authors: %s\n' % (u', '.join(article.authors))
                output += u'keywords: %s\n' % (u', '.join(article.keywords))
                output += u'---\n\n'
                if args['include_summary']:
                    output += u'# Summary\n\n%s\n' % (article.summary)

                output += text

                r = args.get('redirect')
                if r and r in ['nvalt', 'notsey']:
                    title = u'%s - %s' % (article.title, u', '.join(article.authors))
                    title = title.encode('utf-8')
                    output = output.encode('utf-8')

                    if r == 'nvalt':
                        opts = {
                            'txt': output,
                            'title': title,
                        }
                        opts = '&'.join(['%s=%s' % (key, quote(val)) for key, val in opts.items()])
                        url = 'nvalt://make/?' + opts

                    if r == 'notsey':
                        opts = {
                            'text': output,
                            'name': title,
                        }
                        opts = '&'.join(['%s=%s' % (key, quote(val)) for key, val in opts.items()])
                        url = 'notesy://x-callback-url/append?' + opts

                    return make_response(redirect(url))

                return output_text(output, 200, {'Content-Type': 'text'})






api.add_resource(ArticleSimple, '/article')


if __name__ == '__main__':
    app.run(debug=True)
