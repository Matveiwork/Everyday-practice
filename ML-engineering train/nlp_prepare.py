import re
import nltk
import emoji
import unicodedata
import contractions
import inflect
import spacy
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer


#nltk.download('stopwords')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt')


def clean_text(input_text):
    
    # HTML Tags: The first step is to remove all HTML tags inside the input text
    clean_text = re.sub('<[^<]+?>', '', input_text)
    
    # URLs and Links: Next, we remove every URL and link from the text
    clean_text = re.sub(r'http\S+', '', clean_text)

    # Emojis and Emoticons: We use the self-defined function below to convert emojis to text
    # This is important for understanding the sentiment of the text being presented
    clean_text = convert_emojis_to_words(clean_text)
    
    # Lowercase all the input data
    clean_text = clean_text.lower()

    # Remove all White Spaces
    # Since all the data is now words, let's clean any white spaces
    clean_text = re.sub('\s+', ' ', clean_text)

    # Accented Characters to ASCII Characters: We use the unicode normalize function to convert all accented characters to ASCII characters
    clean_text = unicodedata.normalize('NFKD', clean_text).encode('ascii', 'ignore').decode('utf-8', 'ignore')

    # Expand contractions: Text often contains words like "don't" or "won't", let us expand those
    clean_text = contractions.fix(clean_text)

    # Remove special characters: Removing anything that is not "words"
    clean_text = re.sub('[^a-zA-Z0-9\s\.]', '', clean_text)

    # Convert number words to numeric form
    temp = inflect.engine()
    words = []
    for word in clean_text.split():
        if word.isdigit():
            words.append(temp.number_to_words(word))
        else:
            words.append(word)
    clean_text = ' '.join(words)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(clean_text)
    tokens = [token for token in tokens if token not in stop_words]
    clean_text = ' '.join(tokens)

    # Add full-stop to end of sentences
    clean_text = re.sub('([a-z])\.([A-Z])', r'\1. \2', clean_text)

    # Remove punctuations
    clean_text = re.sub(r'[^\w\s.]', '', clean_text)

    # Return the preprocessed, clean text
    return clean_text


def convert_emojis_to_words(text):
    
    # Convert emojis to words
    text = emoji.demojize(text, delimiters=(" ", " "))
    
    # Remove the : from the words and replace _ with space
    text = text.replace(":", "").replace("_", " ")
    
    return text
    
   

def text_vectorize(input_text):
    
    # Instantiate the CountVectorizer object
    vectorizer = CountVectorizer()
    
    # Use vectorizer.fit to transform the text into a matrix of word counts
    counts_matrix = vectorizer.fit_transform(input_text)
    
    # Convert to a dense matrix
    dense_matrix = counts_matrix.todense()
    
    # Return the dense matrix as a numpy array
    return np.array(dense_matrix)


nlp = spacy.load("en_core_web_sm")


def pos_tag(input_text):

    doc = nlp(input_text)
    tagged_output = []

    # Iterate over each token in the document
    for token in doc:
        # Append the token text and its POS tag to the tagged_output list
        tagged_output.append(token.text + '_' + token.pos_)

    # Join the tagged_output list into a single string
    tagged_output_str = ' '.join(tagged_output)

    return tagged_output_str


def lemmatize_and_vectorize(tagged_text):
    
    # Convert the tagged text to a string
    text = " ".join([word.split("_")[0] for word in tagged_text.split()])

    # Apply the Spacy pipeline to the text
    doc = nlp(text)

    vector_list = []

    # Iterate over each token in the Spacy document
    for token in doc:
        lemma = token.lemma_

        # Get the part-of-speech tag for the token
        pos = token.pos_

        if pos == "VERB":
            vec = token.vector
        else:
            vec = token.vector + nlp(pos).vector
        
        vector_list.append(vec)

    vector_array = np.array(vector_list)

    return vector_array


input_text = """   """

clean_text = clean_text(input_text)
print(clean_text)



tagged_output = pos_tag(clean_text)
print(tagged_output)

vectorized_output = lemmatize_and_vectorize(tagged_output)
print(vectorized_output)

