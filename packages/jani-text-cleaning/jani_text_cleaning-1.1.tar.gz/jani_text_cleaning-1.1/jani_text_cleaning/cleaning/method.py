import nltk
"""Required libraries (nltk)"""
class stemmer:

    """
    This class will stem words in a sentence.
    """

    def __init__(self):
        """
        Initializes a `PorterStemmer` object and stores it in __stemmer attribute.
        Takes no parameters.
        Initializes the `__stemmed_text` attribute to a list.
        """

        self.__stemmer = nltk.stem.PorterStemmer()
        self.__stemmed_text = []
    def stems(self,sentence):

        """
        Stems a string into list of words.
        Parameters:
        `sentence` (list): A tokenized list which needs to be stemmed.
        Returns the list of stemmed words.
        Returns a list.
        """

        for text in sentence:
            self.__stemmed_text.append(self.__stemmer.stem(text))
        return self.__stemmed_text


class lemmetizer:

    """
    This class will lemmetize words in a sentence.
    """

    def __init__(self):

        """
        Initializes a `WordNetLemmatizer` object and stores it in __lemmetize attribute.
        Takes no parameters.
        Initializes the `__lemmtized_text` attribute to a list.
        """

        self.__lemmetize = nltk.stem.WordNetLemmatizer()
        self.__lemmtized_text = []
    def word_net(self,sentence):

        """
        Lemmetizes a string into list of words.
        Parameters:
        `sentence` (list): A tokenize list which needs to be lemmetize.
        Returns the list of lemmetized words.
        Returns a list.
        """

        for text in sentence:
            self.__lemmtized_text.append(self.__lemmetize.lemmatize(text,'v'))
        return self.__lemmtized_text


"""
### Example Usage stemmer:

```python
s = stemmer()
stemmed_sentence = s.stems(['A','man','is','running','around','a','swimming','pool','.'])
print(stemmed_sentence)
```

Output:
```
['a', 'man', 'is', 'run', 'around', 'a', 'swim', 'pool', '.']
```
"""

"""
### Example Usage lemmetizer:

```python
s = lemmetizer()
lemmtized_sentence = s.word_net(['A','man','is','running','around','a','swimming','pool','.'])
print(lemmtized_sentence)
```

Output:
```
['A', 'man', 'be', 'run', 'around', 'a', 'swim', 'pool', '.']
```
"""