
class stopwords:

    """
    The `stopwords` class provides functionality related to stopwords in natural language processing.
    """

    def __init__(self):

        """
        Initializes a `stopwords` object.
        Takes no parameters.
        Sets the `__stopwords` attribute to a frozenset of commonly used stop words.
        """

        self.__stopwords = frozenset({'your', 'then', 'by', 'being', 'weren', 'those', "you'd", "it's", 'such', 'does', 'a', 'but', 're', "she's", 'am', 'shan', 'don', "shan't", 'just', 'during', 'will', 'do', 've', 'what', 'where', 'after', 'some', 'mightn', "mightn't", 'yourselves', 'below', 'for', 'they', 'hadn', "needn't", 'that', 'were', 'most', 'i', 'which', 'd', "weren't", 'be', 'y', 'down', 'why', 'themselves', 'more', "hadn't", 'll', 'until', 'is', 'no', "doesn't", 'won', "haven't", 'only', 'and', 'than', 'of', 'when', 'in', 'an', 'ours', 'couldn', 'at', "that'll", "won't", 'any', "don't", 'all', 'shouldn', 'his', 'doing', 'with', 'she', 'him', 'under', 'off', "isn't", 'how', 's', 'same', 'doesn', 'while', "you'll", "you're", 'needn', 'wasn', 'her', 'whom', 'hasn', "wouldn't", 'ma', 'haven', 'if', 'them', 'again', 'been', 'or', "wasn't", 'are', 'can', 'on', 'its', 'me', 'himself', "you've", 'he', 'against', 'own', 'it', 'who', 'we', 'herself', 'having', 'had', "shouldn't", 'hers', 'myself', 'have', 'the', 'mustn', 'about', 'over', 'above', 'yourself', 'didn', 'from', 'not', 'itself', 'through', 'our', 'yours', 'you', 'now', 'o', "hasn't", 'isn', "aren't", 'should', "should've", 'further', 'nor', 'this', 'to', 't', 'was', 'out', 'here', 'my', 'before', "didn't", 'because', 'ourselves', 'has', "mustn't", 'few', 'theirs', 'these', 'into', 'once', 'ain', "couldn't", 'too', 'so', 'up', 'there', 'both', 'wouldn', 'as', 'other', 'did', 'aren', 'their', 'between', 'm', 'each', 'very'}
)
    def __repr__(self):

        """
        Returns a string representation of the set of stop words.
        Takes no parameters.
        Returns a string.

        Usage

        ```python
        a = stopwords()
        print(a)

        Output:
        ```
        {'she', 'or', 'wouldn', 'here', 'they', 'same', 'isn', 'shan', "doesn't", 'haven', 'o', 'nor', 'weren', 'up', "haven't", 'above', 'until', 'doing', "shouldn't", 'my', 'what', 'between', "you'll", 'other', 'll', 'as', 'been', 'because', 's', "weren't", "you've", 'should', 'being', 'hasn', 'below', "shan't", 'ma', 'and', 'it', 've', "needn't", 'have', 'don', 'myself', 'into', 'doesn', 'your', 'out', 'each', 'will', 'at', "wouldn't", 'own', "couldn't", 'against', 'i', 'needn', 'now', 'an', 'hadn', 'm', 'those', 'only', 'shouldn', 'mightn', 'off', 'ain', 'such', 'couldn', "that'll", 'but', 'are', 'this', 'through', 'is', 'aren', 'when', "you're", 'there', 'were', 'theirs', 'more', 'why', 'has', 'most', 'he', 'during', 't', "it's", 'was', 'by', 'these', 'her', 'mustn', 'before', "she's", 'not', 'you', 'for', 'no', 'of', 'too', 're', 'having', 'me', 'we', 'hers', 'herself', 'the', "you'd", "hasn't", "isn't", 'then', 'does', 'ours', 'yours', 'didn', 'who', "mustn't", 'y', 'had', 'wasn', "don't", 'in', 'on', 'whom', 'its', 'under', "should've", 'if', 'than', 'about', "didn't", 'very', 'themselves', 'again', 'further', 'so', "aren't", 'just', 'do', 'won', 'them', 'from', 'once', 'that', 'both', "mightn't", 'how', 'down', "won't", 'while', 'to', 'd', 'after', 'all', 'where', 'some', 'can', 'yourselves', "hadn't", 'be', 'ourselves', 'yourself', 'itself', 'any', 'their', 'few', 'a', 'over', 'which', 'our', 'himself', "wasn't", 'did', 'am', 'him', 'his', 'with'}
        ```
        """

        return str(set(self.__stopwords))

    def get_stopwords(self):

        """
        Returns the set of stop words.
        Takes no parameters.
        Returns a set.

        Usage

        ```python
        a = stopwords.get_stopwords()
        print(a)

        Output:
        ```
        {'she', 'or', 'wouldn', 'here', 'they', 'same', 'isn', 'shan', "doesn't", 'haven', 'o', 'nor', 'weren', 'up', "haven't", 'above', 'until', 'doing', "shouldn't", 'my', 'what', 'between', "you'll", 'other', 'll', 'as', 'been', 'because', 's', "weren't", "you've", 'should', 'being', 'hasn', 'below', "shan't", 'ma', 'and', 'it', 've', "needn't", 'have', 'don', 'myself', 'into', 'doesn', 'your', 'out', 'each', 'will', 'at', "wouldn't", 'own', "couldn't", 'against', 'i', 'needn', 'now', 'an', 'hadn', 'm', 'those', 'only', 'shouldn', 'mightn', 'off', 'ain', 'such', 'couldn', "that'll", 'but', 'are', 'this', 'through', 'is', 'aren', 'when', "you're", 'there', 'were', 'theirs', 'more', 'why', 'has', 'most', 'he', 'during', 't', "it's", 'was', 'by', 'these', 'her', 'mustn', 'before', "she's", 'not', 'you', 'for', 'no', 'of', 'too', 're', 'having', 'me', 'we', 'hers', 'herself', 'the', "you'd", "hasn't", "isn't", 'then', 'does', 'ours', 'yours', 'didn', 'who', "mustn't", 'y', 'had', 'wasn', "don't", 'in', 'on', 'whom', 'its', 'under', "should've", 'if', 'than', 'about', "didn't", 'very', 'themselves', 'again', 'further', 'so', "aren't", 'just', 'do', 'won', 'them', 'from', 'once', 'that', 'both', "mightn't", 'how', 'down', "won't", 'while', 'to', 'd', 'after', 'all', 'where', 'some', 'can', 'yourselves', "hadn't", 'be', 'ourselves', 'yourself', 'itself', 'any', 'their', 'few', 'a', 'over', 'which', 'our', 'himself', "wasn't", 'did', 'am', 'him', 'his', 'with'}
        ```
        """

        return set(self.__stopwords)

    def add_stopwords(self,custom_stopwords):

        """
        Adds custom stopwords to the existing set of stop words.
        Parameters:
        `custom_stopwords` (set): A set of custom stopwords to add.
        Returns the updated set of stop words.
        Returns a set.

        Usage

        ```python
        a = stopwords.add_stopwords(custom_stopwords=['Hello'])
        print(a)

        Output:
        ```
        {'Hello', 'she', 'or', 'wouldn', 'here', 'they', 'same', 'isn', 'shan', "doesn't", 'haven', 'o', 'nor', 'weren', 'up', "haven't", 'above', 'until', 'doing', "shouldn't", 'my', 'what', 'between', "you'll", 'other', 'll', 'as', 'been', 'because', 's', "weren't", "you've", 'should', 'being', 'hasn', 'below', "shan't", 'ma', 'and', 'it', 've', "needn't", 'have', 'don', 'myself', 'into', 'doesn', 'your', 'out', 'each', 'will', 'at', "wouldn't", 'own', "couldn't", 'against', 'i', 'needn', 'now', 'an', 'hadn', 'm', 'those', 'only', 'shouldn', 'mightn', 'off', 'ain', 'such', 'couldn', "that'll", 'but', 'are', 'this', 'through', 'is', 'aren', 'when', "you're", 'there', 'were', 'theirs', 'more', 'why', 'has', 'most', 'he', 'during', 't', "it's", 'was', 'by', 'these', 'her', 'mustn', 'before', "she's", 'not', 'you', 'for', 'no', 'of', 'too', 're', 'having', 'me', 'we', 'hers', 'herself', 'the', "you'd", "hasn't", "isn't", 'then', 'does', 'ours', 'yours', 'didn', 'who', "mustn't", 'y', 'had', 'wasn', "don't", 'in', 'on', 'whom', 'its', 'under', "should've", 'if', 'than', 'about', "didn't", 'very', 'themselves', 'again', 'further', 'so', "aren't", 'just', 'do', 'won', 'them', 'from', 'once', 'that', 'both', "mightn't", 'how', 'down', "won't", 'while', 'to', 'd', 'after', 'all', 'where', 'some', 'can', 'yourselves', "hadn't", 'be', 'ourselves', 'yourself', 'itself', 'any', 'their', 'few', 'a', 'over', 'which', 'our', 'himself', "wasn't", 'did', 'am', 'him', 'his', 'with'}
        ```
        """

        new_stop_words = set(self.__stopwords.union(custom_stopwords))
        return new_stop_words

    def remove_stopwords(self,sentence,custom_stopwords = None):

        """
        Removes stop words from a given sentence.
        Parameters:
        `sentence` (str): The input sentence to remove stop words from.
        `custom_stopwords` (set): Optional set of additional stopwords to consider.
        Returns the filtered sentence with stopwords removed.
        Returns a string.
        """
        if custom_stopwords == None:
            custom_stopwords = set(self.__stopwords)
        else:
            stopwords = []
            for word in custom_stopwords:
                stopwords.append(word.lower())
            custom_stopwords = set(self.__stopwords.union(stopwords))
        filtered_sentence = [word for word in sentence.split() if word not in custom_stopwords]
        return ' '.join(filtered_sentence)


"""

Usage

```python
s = stopwords()
filtered_sentence = s.add_stopwords("Hello, world! How are you today")
print(filtered_sentence)

Output:
```
Hello, world! How today
```
"""