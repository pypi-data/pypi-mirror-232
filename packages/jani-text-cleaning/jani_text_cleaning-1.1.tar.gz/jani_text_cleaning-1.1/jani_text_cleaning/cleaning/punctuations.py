import re
import string
"""Required libraries (re,string)"""
class punctuations:

    """
    This class provides the functionality to remove punctuations from a given sentence.
    """

    def __init__(self):

        """
        This method initializes a __puncts attribute which is a set of string punctuations.
        Takes no parameter.
        """

        self.__puncts = set(string.punctuation)

    def __repr__(self):

        """
        Returns a string representation of the set of punctuations.
        Takes no parameters.
        Returns a string.
        """

        return str(self.__puncts)

    def remove_punctuation(self,sentence):

        """
        Removes punctuations from a given sentence.
        Parameters:
        `sentence` (str): The input sentence to remove punctuations from.
        Returns the filtered sentence with punctuations removed.
        Returns a string.
        """

        filtered_sentence = re.sub(pattern='[%s]' % re.escape(str(self.__puncts)),string = sentence,repl=' ')
        filtered_sentence = re.sub(pattern=r'\s+', repl=' ', string=filtered_sentence)
        return filtered_sentence


"""
### Example Usage:

```python
s = punctuations()
filtered_sentence = s.remove_punctuation("Wow!!!This is a sentence with multiple punctuations,isn't it?")
print(filtered_sentence)
```

Output:
```
Wow This is a sentence with multiple punctuations isn t it
```
"""