### Talha Shaikh - 218095257 // ITEC 4020 ASSIGNMENT 3
### Python Mini Search Engine + with a bit of autocorrect

#Import statements 
import os
from bs4 import BeautifulSoup

#Extracting content and tokenizing sentences 
def extract_content(file_path):
    """
    Extract and return the text content from an HTML file.

    Parameters:
    file_path (str): The path to the HTML file.

    Returns:
    str: The extracted text content from the HTML file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        content = soup.get_text()
        return content

def tokenize(content):
    """
    Tokenize the text content into a list of sentences, with each sentence further split into words.

    Parameters:
    content (str): The text content to be tokenized.

    Returns:
    list: A list of sentences, where each sentence is a list of words.
    """
    sentences = content.split('.')
    words = [sentence.split() for sentence in sentences]
    return words


def process_files(folder_path):
    """
    Process all HTML files in the given folder, extracting and tokenizing their content.

    Parameters:
    folder_path (str): The path to the folder containing the HTML files.

    Returns:
    dict: A dictionary where keys are filenames and values are lists of tokenized sentences.
    """
    data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.html'):
            file_path = os.path.join(folder_path, filename)
            content = extract_content(file_path)
            words = tokenize(content)
            data[filename] = words
    return data


def build_inverted_index(documents):
    """
    Builds an inverted index from the provided documents.

    Parameters:
    documents (dict): A dictionary where the key is the document name and the value is a list of sentences,
    each sentence being a list of words.

    Returns:
    dict: An inverted index mapping each word to a list of occurrences.
    Each occurrence is represented as a tuple (document_name, sentence_index, word_index).
    """
    inverted_index = {}
    
    for document_name, sentences in documents.items():
        for sentence_index, sentence in enumerate(sentences):
            for word_index, word in enumerate(sentence):
                if word not in inverted_index:
                    inverted_index[word] = []
                inverted_index[word].append((document_name, sentence_index, word_index))
    
    return inverted_index

def country_search(keyword, inverted_index):
    """
    Search for documents containing the given keyword.

    Parameters:
    keyword (str): The word to search for in the documents.
    inverted_index (dict): The inverted index mapping each word to a list of occurrences.
    Each occurrence is represented as a tuple (document_name, sentence_index, word_index).

    Returns:
    list: A list of document names containing the keyword.
    """
    if keyword in inverted_index:
        documents = {entry[0] for entry in inverted_index[keyword]}
        return list(documents)
    return []

def levenshtein_distance(s1, s2):
    """
    Compute the edit (insertions, deletions, replacements) Distance between two strings.

    Parameters:
    s1 (str): The first string.
    s2 (str): The second string.

    Returns:
    int: The Levenshtein Distance between the two strings.
    """
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)

    distance_matrix = [[0 for _ in range(len(s2) + 1)] for _ in range(len(s1) + 1)]

    for i in range(len(s1) + 1):
        distance_matrix[i][0] = i
    for j in range(len(s2) + 1):
        distance_matrix[0][j] = j

    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
            distance_matrix[i][j] = min(distance_matrix[i - 1][j] + 1,      
                                        distance_matrix[i][j - 1] + 1,                     
                                        distance_matrix[i - 1][j - 1] + cost)           

    return distance_matrix[-1][-1]

def fuzzy_search(keyword, inverted_index, threshold=2):
    """
    Perform a fuzzy search to find documents containing words similar to the given keyword.

    Parameters:
    keyword (str): The word to search for in the documents.
    inverted_index (dict): The inverted index mapping each word to a list of occurrences.
                                       Each occurrence is represented as a tuple (document_name, sentence_index, word_index).
    threshold (int): The maximum Levenshtein Distance to consider for similarity. Default is 2.

    Returns:
    list: A list of document names containing words similar to the keyword.
    """
    results = set()
    for word in inverted_index.keys():
        if levenshtein_distance(keyword, word) <= threshold:
            results.update(doc for doc, _, _ in inverted_index[word])
    return list(results)

#extracting the files and letting the user test the functions 
WIKIFILES = process_files(r"C:\Users\Talha\OneDrive\Desktop\4020vs\wikilinks") #change this to the path of your folder
WikifilesInvertedIndex = build_inverted_index(WIKIFILES)
answer1 = country_search(input("enter a keyword: "), WikifilesInvertedIndex)
print("that word is found in the following documents: ", answer1)
answer2 = fuzzy_search(input("enter another keyword, feel free to make a typo: "), WikifilesInvertedIndex)
print("that word is found in the following documents: ", answer2)

# My program returns multiple results for the country_search() function because this approach
# seems most logical. Multiple documents may contain the same word. For example, 
# country_search("Toronto") will return many Wikipedia pages, including some that may seem 
# irrelevant like "Syria - Wikipedia.html" because that file contains a reference from the 
# Toronto Sun. On the other hand, something more specific like country_search("Trudeau") will 
# primarily return "Canada - Wikipedia.html".

# I wanted to clarify this because the instructions mentioned "For instance, the output of 
# country_search('Toronto') should be 'canada.html.'" However, it also stated "Develop a 
# function named country_search(keyword) that, when given a keyword as input, returns the 
# document[S] containing that keyword," indicating that the function should return multiple 
# results. I followed the latter interpretation to ensure comprehensive search functionality.
