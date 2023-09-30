import re
"""Required libraries (re)"""
class hyperlinks:

    """
    This class removes hyperlinks from a sentence.
    """

    def __init__(self):

        """
        This method initializes a __hyperlinks attribute.
        This attribute compiles regular expressions for hyperlinks.
        Takes no parameter.
        """

        self.__hyperlinks = re.compile(pattern=r'\(?\s?\{?\s?\[?\s?http[s]?://[^\s]+(?=[^\)\]\}]+)')

    def remove_hyperlinks(self,sentence):

        """
        This method takes a sentence as input and removes hyperlinks from it.
        It returns the filtered sentence.
        Arguments:
        `sentence` (str): The sentence from which hyperlinks should be removed.
        Returns the sentence after removing hyperlinks.
        Returns a string.
        """

        filtered_sentence = self.__hyperlinks.sub(repl='',string = sentence)
        return filtered_sentence


"""
#Usage

```python
s = hyperlinks()
filtered_sentence = s.remove_hyperlinks(sentence="This is a sentence with a hyperlink: https://www.google.com. This is another sentence with a hyperlink: https://www.example.com.")
print(filtered_sentence)

Output:
```
This is a sentence with a hyperlink: This is another sentence with a hyperlink:.
```
"""