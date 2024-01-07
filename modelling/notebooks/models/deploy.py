import pandas as pd
import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout
from keras.initializers import Constant
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tqdm import tqdm
from keras.layers import Dense, SpatialDropout1D
import contractions
import re
import nltk

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
# initializing Stop words libraries
nltk.download("stopwords")
from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))
from nltk.tokenize import word_tokenize

# comment spacy imports locally because of incompatibility with numpy 1.19.5
# spacy

# import spacy
# from spacy.util import filter_spans
# from spacy.tokens import Span
# from spacy.matcher import Matcher

# import en_core_web_sm
# nlp = spacy.load(en_core_web_sm)


# clean desc
def clean(desc):
    desc = contractions.fix(desc)
    desc = re.sub("[!@.$''':()]", "", desc)
    return desc


# create pos tags
def tokenize_and_tag(desc):
    tokens = nltk.word_tokenize(desc.lower())
    filtered_tokens = [w for w in tokens if not w in stop_words]
    tagged = nltk.pos_tag(filtered_tokens)
    return tagged


def extract_POS(tagged):
    # pattern 1
    grammar1 = """Noun Phrases: {<DT>?<JJ>*<NN|NNS|NNP>+}"""
    chunkParser = nltk.RegexpParser(grammar1)
    tree1 = chunkParser.parse(tagged)

    # typical noun phrase pattern appending to be concatted later
    g1_chunks = []
    for subtree in tree1.subtrees(filter=lambda t: t.label() == "Noun Phrases"):
        g1_chunks.append(subtree)

    # pattern 2
    grammar2 = """NP2: {<IN>?<JJ|NN>*<NNS|NN>} """
    chunkParser = nltk.RegexpParser(grammar2)
    tree2 = chunkParser.parse(tagged)

    # variation of a noun phrase pattern to be pickled for later analyses
    g2_chunks = []
    for subtree in tree2.subtrees(filter=lambda t: t.label() == "NP2"):
        g2_chunks.append(subtree)

    # pattern 3
    grammar3 = """ VS: {<VBG|VBZ|VBP|VBD|VB|VBN><NNS|NN>*}"""
    chunkParser = nltk.RegexpParser(grammar3)
    tree3 = chunkParser.parse(tagged)

    # verb-noun pattern appending to be concatted later
    g3_chunks = []
    for subtree in tree3.subtrees(filter=lambda t: t.label() == "VS"):
        g3_chunks.append(subtree)

    # pattern 4
    # any number of a singular or plural noun followed by a comma followed by the same noun, noun, noun pattern
    grammar4 = """Commas: {<NN|NNS>*<,><NN|NNS>*<,><NN|NNS>*} """
    chunkParser = nltk.RegexpParser(grammar4)
    tree4 = chunkParser.parse(tagged)

    # common pattern of listing skills appending to be concatted later
    g4_chunks = []
    for subtree in tree4.subtrees(filter=lambda t: t.label() == "Commas"):
        g4_chunks.append(subtree)

    return g1_chunks, g2_chunks, g3_chunks, g4_chunks


def training_set(chunks):
    """creates a dataframe that easily parsed with the chunks data"""
    df = pd.DataFrame(chunks)
    df.fillna("X", inplace=True)

    train = []
    for row in df.values:
        phrase = ""
        for tup in row:
            # needs a space at the end for seperation
            phrase += tup[0] + " "
        phrase = "".join(phrase)
        # could use padding tages but encoder method will provide during
        # tokenizing/embeddings; X can replace paddding for now
        train.append(phrase.replace("X", "").strip())

    df["phrase"] = train

    # only returns 10% of each dataframe to be used
    # Update: only do 50% if running on excel
    return df.phrase


def strip_commas(df):
    """create new series of individual n-grams"""
    grams = []
    for sen in df:
        sent = sen.split(",")
        for word in sent:
            grams.append(word)
    return pd.Series(grams)


def generate_phrases(desc):
    tagged = tokenize_and_tag(desc)
    g1_chunks, g2_chunks, g3_chunks, g4_chunks = extract_POS(tagged)
    c = training_set(g4_chunks)
    separated_chunks4 = strip_commas(c)
    # one training corpus with 10% of each POS regex identification
    phrases = pd.concat(
        [
            training_set(g1_chunks),
            training_set(g2_chunks),
            training_set(g3_chunks),
            separated_chunks4,
        ],
        ignore_index=True,
    )
    return phrases


def create_corpus(df):
    """Creates corpus from feature column, which is a pandas series"""
    corpus = []
    for phrase in tqdm(df):
        words = [
            word.lower() for word in word_tokenize(phrase) if (word.isalpha() == 1)
        ]
        corpus.append(words)
    return corpus


def create_padded_inputs(corpus):
    """Create padded sequences of equal lenght as input to LSTM"""
    MAX_LEN = 20
    tokenizer_obj = Tokenizer()
    tokenizer_obj.fit_on_texts(corpus)
    sequences = tokenizer_obj.texts_to_sequences(corpus)

    phrase_pad = pad_sequences(
        sequences, maxlen=MAX_LEN, truncating="post", padding="post"
    )
    return phrase_pad


def get_predictions(desc):
    # clean
    desc = clean(desc)
    # load model
    model = tf.keras.models.load_model(
        "/Users/koechian/PycharmProjects/skillexplore/modelling/notebooks/models/lstm_skill_extractor.h5"
    )
    # tokenize and convert to phrases
    phrases = generate_phrases(desc)
    # preprocess unseen data
    corpus = create_corpus(phrases)
    corpus_pad = create_padded_inputs(corpus)
    # get predicted classes
    predictions = (model.predict(corpus_pad) > 0.80).astype("int32")
    # return predicted skills as list
    out = pd.DataFrame({"Phrase": phrases, "Class": predictions.ravel()})
    skills = out.loc[out["Class"] == 1]
    return skills["Phrase"].tolist()


def get_predictions_excel(filename):
    """description column must be titled Job Desc"""
    df = pd.read_csv(filename)
    df["Extracted skills"] = df["Job Description"].apply(lambda x: get_predictions(x))

    return df.to_csv("extracted.csv")


desc = "The SI Lead will manage all monitoring, evaluation and learning and strategic information components of the program. S/he will be responsible for the design and implementation of monitoring, evaluation and reporting (MER) systems that document, report and enable timely use of results, as well as strengthen and use relevant national and county reporting systems. S/he will be expected to develop a strong monitoring and evaluation plan consistent with donor's results framework, including appropriate indicators, baseline assessment plan/ data, targets and plan to evaluate performance and produce timely, accurate and complete reporting. S/he will be responsible for the design and implementation of the learning agenda, as well as implementing key findings in the program in collaboration with the technical director. S/he will coordinate the collection of data and conduct field visits for data validation, quality, and completeness of data sets. He will be responsible for building the capacity of the supported facilities, county health team and project staff in collecting, utilizing, and disseminate data as well as ensuring harmonization of all data. Duties and Responsibilities: Oversee, implement and monitor all monitoring and evaluation activities for the program. Develop a robust strategic information approach that can track the immediate and intermediate effects of program activities, including changes in knowledge, attitudes, responsiveness, data use and technical assistance demand. Design and implement an M&E system capable of timely tracking performance and using the data to adjust implementation for optimal performance Conduct training and workshops related to M&E for program, county, sub-county and facility teams Ensure timely reporting of supported activities to county, MoH and donor through DHIS2 and DATIM Scale up use of HMIS systems for HIV including eHTS, KenyaEMR Work with PI/PD/Senior Technical Advisor to establish networks for collaboration between CDC, other stakeholders and donors, academia, research institutes, and other CDC funded programs in country Work with PI/PD and technical team in developing program goals and objectives as well as MER tools and strategies and synthesize data to inform the decisions on project performance Provide regular reports on the status of implementation against the project goals and objectives to PI, PD, Senior Technical Advisor and CDC and other program managers as required. Collaborate with the project team in identifying project activities, processes and outcomes for documentation and sharing lessons learned and best practices Collaborate with MOH M&E department, Health informatics and Data warehouse to create platform for dialogue, data sharing, and addressing key M&E issues within MOH Strong understanding of Kenya health information systems, and issues related to data (e.g. data security; tracking through the cascade etc.) on key and priority populations Job Specification: Master of Science in Epidemiology and/or Statistics with 10 years of experience in international health programs, at least 5 of which are with PEPFAR-funded programs and 3 of which are CDC-funded. Proven expertise in quantitative and qualitative methodologies, evaluation and implementation research, health information systems, reporting, data quality assessments, data analysis, and presentation. Must have prior experience in capacity building, such as developing content, planning, and facilitating trainings and providing technical assistance. Preferred familiarity with adult learning principles/techniques and demonstrated ability to design and facilitate learning opportunities for adults. Proficient in use of data management and analysis tools and advanced skills in MS Excel or statistical packages such SAS, SPSS."

skills = get_predictions(desc)

print(skills)
