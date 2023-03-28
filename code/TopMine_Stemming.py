from topmine import *
from pathlib import *
from textblob import TextBlob, Word
from nltk.stem.snowball import SnowballStemmer
import re
import nltk
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

def topmine_1_docs(input_path='Dataset/Texts_cut', output_path='Dataset/TopMine_texts'):
    """
    Applying TopMine to texts with the selection of terms from a single word
            Parameters:
                    input_path (str): directory with documents sorted by year to load
                    output_path (str): directory with documents sorted by year to save
    """
    for direct in Path(input_path).iterdir():
        number = direct.stem
        new_input_path = Path(input_path + '/' + number)

        for item in Path(new_input_path).iterdir():
            new_output_path = Path(output_path + '/' + number + '/' + item.name)

            with open(item, 'r', errors="ignore") as fin:
                fout = open(new_output_path, 'w')

                # Mining terms
                p = PhraseMining(fin)
                mined_words = p.mine()[-1]

                for i in mined_words:
                    fout.write(i + ' ')

                fout.close()


def stem_texts(input_path='Dataset1', output_path='Dataset/TopMine_Stem_Texts'):
    """
    Applying stemming to texts
            Parameters:
                    input_path (str): directory with documents to load
                    output_path (str): directory with documents to save
    """
    for item in Path(input_path).iterdir():
        new_output_path = Path(output_path + '/' + item.name)

        with open(item, 'r', errors="ignore") as fin:
            fout = open(new_output_path, 'w')

            # Stemming
            sent = TextBlob(fin.read())
            lemmatized_output = ' '.join([w.lemmatize() for w in sent.words if len(w) > 2])

            without_nums = re.sub(r"\d+", "", lemmatized_output, flags=re.UNICODE)
            fout.write(without_nums)
            fout.close()


def stem_texts_2(input_path='Dataset/Texts_cut_num', output_path='Dataset/Stem_texts'):
    """
    Applying stemming to texts (type 2)
            Parameters:
                    input_path (str): directory with documents sorted by year to load
                    output_path (str): directory with documents sorted by year to save
    """
    stemmer = SnowballStemmer(language='english')

    for direct in Path(input_path).iterdir():
        number = direct.stem
        new_input_path = Path(input_path + '/' + number)

        for item in Path(new_input_path).iterdir():
            new_output_path = Path(output_path + '/' + number + '/' + item.name)
            print(item.name)

            with open(item, 'r', errors="ignore") as fin:
                fout = open(new_output_path, 'w')

                sent = TextBlob(fin.read())
                # Stemming
                stemmed_output = ' '.join([stemmer.stem(w) for w in sent.words])
                fout.write(stemmed_output)

                fout.close()