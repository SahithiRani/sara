import string
import numpy as np
import pandas as pd
from textblob import TextBlob
from collections import Counter
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from sklearn.model_selection import train_test_split
nltk.download('stopwords')
nltk.download('wordnet')


df = pd.read_csv("emodata.csv")


def get_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        result = "Positive"
    elif sentiment < 0:
        result = "Negative"
    else:
        result = "Neutral"
    return result

df['Sentiment'] = df['Text'].apply(get_sentiment)



def remove_punct(text):
    text = text.lower()
    text = re.sub('[^a-zA-Z\n\.]', ' ', text)
    return text

df['Text_punct'] = df['Text'].apply(lambda x: remove_punct(x))



def tokenization(text):
    text = re.split('\W+', text)
    return text

df['Text_tokenized'] = df['Text_punct'].apply(lambda x: tokenization(x.lower()))



stopword = nltk.corpus.stopwords.words('english')
stopword.append('https')
stopword.append('www')
stopword.append('name')


def remove_stopwords(text):
    text = [word for word in text if word not in stopword]
    return text

df['Text_nonstop'] = df['Text_tokenized'].apply(lambda x: remove_stopwords(x))



ps = nltk.PorterStemmer()

def stemming(text):
    text = [ps.stem(word) for word in text]
    return text

df['Text_stemmed'] = df['Text_nonstop'].apply(lambda x: stemming(x))



wn = nltk.WordNetLemmatizer()
def lemmatizer(text):
    text = " ".join([wn.lemmatize(word) for word in text])
    return text

df['Text_lemmatized'] = df['Text_stemmed'].apply(lambda x: lemmatizer(x))
df['Clean_Text'] = df['Text_lemmatized']


def extract_keywords(text, num=50):
    tokens = [tok for tok in text.split()]
    most_common_tokens = Counter(tokens).most_common(num)
    return dict(most_common_tokens)

emotion_list = df['Emotion'].unique().tolist()
joy_list = df[df['Emotion'] == 'joy']['Clean_Text'].tolist()
joy_docx = ' '.join(joy_list)
keyword_joy = extract_keywords(joy_docx)

surprise_list = df[df['Emotion'] == 'surprise']['Clean_Text'].tolist()
surprise_docx = ' '.join(surprise_list)
keyword_surprise = extract_keywords(surprise_docx)


Xfeatures = df['Clean_Text']
ylabels = df['Emotion']

cv = CountVectorizer()
X = cv.fit_transform(Xfeatures)
X_train, X_test, y_train, y_test = train_test_split(X, ylabels, test_size=0.3, random_state=42)

nv_model = MultinomialNB()
nv_model.fit(X_train, y_train)
model_file1 = open("emotion_classifier_nv_model_11_may_2021.pkl", "wb")
joblib.dump(nv_model, model_file1)
model_file1.close()

lr_model = LogisticRegression()
lr_model.fit(X_train, y_train)
model_file2 = open("emotion_classifier_lr_model_11_may_2021.pkl", "wb")
joblib.dump(lr_model, model_file2)
model_file2.close()



def predict_emotion(sample_text, model):
    myvect = cv.transform(sample_text).toarray()
    prediction = model.predict(myvect)
    pred_proba = model.predict_proba(myvect)
    pred_percentage_for_all = dict(zip(model.classes_, pred_proba[0]))
    return [prediction[0], np.max(pred_proba)]



def return_emo(msg):
    msg = remove_punct(msg)
    msg = tokenization(msg)
    msg = remove_stopwords(msg)
    msg = stemming(msg)
    msg = lemmatizer(msg)
    senti1 = predict_emotion([msg], nv_model)[0]
    senti1score = predict_emotion([msg], nv_model)[1]
    senti2 = predict_emotion([msg], lr_model)[0]
    senti2score = predict_emotion([msg], lr_model)[1]

    if senti1score >= senti2score:
        return senti1
    else:
        return senti2



