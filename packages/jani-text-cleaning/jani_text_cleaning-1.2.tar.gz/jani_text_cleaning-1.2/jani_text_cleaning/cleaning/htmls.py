import re
"""Required libraries (re)"""
class htmls:

    """
    This class removes html codes from a sentence.
    """

    def __init__(self):

        """
        This method initializes a __htmls attribute.
        This attribute compiles regular expressions for html.
        Takes no parameter.
        """

        self.__htmls = re.compile(pattern=r'<[^>]+>')

    def remove_htmls(self,sentence):

        """
        This method takes a sentence as input and removes html code from it.
        It returns the filtered sentence.
        Arguments:
        `sentence` (str): The sentence from which html code should be removed.
        Returns the sentence after removing html code.
        Returns a string.
        """

        filtered_sentence = self.__htmls.sub(repl=' ',string=sentence)
        return filtered_sentence


"""

Usage

```python
s = htmls()
filtered_sentence = s.remove_htmls("<!DOCTYPE html><html><head><title>My First HTML Page</title></head><body><h1>This is my first HTML page!</h1><p>This is a paragraph.</p></body></html>")
print(filtered_sentence)

Output:
```
My First HTML Page    This is my first HTML page!  This is a paragraph.   
```
"""