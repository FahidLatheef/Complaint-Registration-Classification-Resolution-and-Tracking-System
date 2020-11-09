# -*- coding: utf-8 -*-
import pickle
import warnings
import smtplib

warnings.filterwarnings('ignore')

stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
             'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
             'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
             'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
             'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but',
             'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
             'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
             'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
             'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
             'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
             "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't",
             'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
             "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
             "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn',
             "wouldn't", 'nan']


def prediction_category(new_complaint):
    filename = 'model/CC_model_LR.pkl'
    loaded_model = pickle.load(open(filename, 'rb'))
    result = loaded_model.predict(new_complaint)
    return result


# Function to remove punctuations
# Replace Punctuations with ' '
punctuations_list = [',', '.', ';', ':', '(', ')', '{', '}', '[', ']']


def remove_punctuations(text, punctuations=punctuations_list):
    if punctuations is None:
        punctuations = [',', '.', ';', ':', '(', ')', '{', '}', '[', ']']
    for letter in text:
        if letter in punctuations:
            text = text.replace(letter, ' ')
    return text


def preprocessing(a, b, c):
    joined = str(a) + ' ' + str(b) + ' ' + str(c)
    joined = joined.strip()
    joined = joined.lower()
    all_words = joined.split()
    final = ''
    for word in all_words:
        if word not in stopwords:
            final = final + ' ' + word
    text = remove_punctuations(final)
    return text


def send_the_email(recipient, subject, body, sender='youremail@gmail.com'):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Client depending upon your mail
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, 'your password')  # Doing 2-step authentification and create an app password and using that as password
        msg = f"Subject: {subject} \n\n{body}"
        server.sendmail(
            sender,
            recipient,
            msg
        )
        print("An Email has been sent")
        server.quit()
    except smtplib.SMTPException:
        print("Error: unable to send email")

