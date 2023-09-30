import re
"""Required libraries (re)"""
class tokenize:
    """This class is used to tokenize sentences and words from a given text."""
    def __init__(self):
        self.__sent_tokenize = []
        self.__word_tokenize = []
    def sent_tokenize(self,sentence):
        """
        This method takes a sentence as input and returns a list of tokenized sentences.
        Parameters:
        `sentence` (str): The input sentence to be tokenized.
        Returns a list of tokenized sentences.
        Returns a list.
        """

        self.__sent_tokenize = re.split(pattern=r'[.!?]\s', string=sentence)
        return self.__sent_tokenize

    def word_tokenize(self,sentence):
        """
        This method takes a sentence as input and returns a list of tokenized words.
        Parameters:
        `sentence` (str): The input sentence to be tokenized.
        Returns a list of tokenized words.
        Returns a list.
        """
        self.__word_tokenize = re.split(r'\W+', sentence)
        return self.__word_tokenize


"""
### Example Usage:

```python
sentences = tokenize().sent_tokenize("This is a sentence. This is another sentence.")
print(sentences)
```

Output:
```
['This is a sentence', 'This is another sentence.']
```
"""


"""
### Example Usage:

```python
sentences = tokenize().word_tokenize("This is a sentence. This is another sentence.")
print(sentences)
```

Output:
```
['This', 'is', 'a', 'sentence', 'This', 'is', 'another', 'sentence', '']
```
"""
