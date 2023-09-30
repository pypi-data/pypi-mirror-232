import re
"""Required libraries (re)"""
class specials:

    """
    This class provides functionality to remove special characters and emojis from a given sentence.
    """

    def __init__(self):

        """
        This method initializes the specials class.
        It compiles regular expressions for special characters and emojis.
        """

        self.__specials = re.compile(pattern = re.compile("[" "\U0001F600-\U0001F64F"  
                                   "\U0001F300-\U0001F5FF"  
                                   "\U0001F680-\U0001F6FF"  
                                   "\U0001F700-\U0001F77F"  
                                   "\U0001F780-\U0001F7FF" 
                                   "\U0001F800-\U0001F8FF" 
                                   "\U0001F900-\U0001F9FF"  
                                   "\U0001FA00-\U0001FA6F"  
                                   "\U00002702-\U000027B0"  
                                   "\U000024C2-\U0001F251"  
                                   "]", flags=re.UNICODE))
        self.__characters = re.compile(pattern="[^\w\s]")

    def remove_specials(self, sentence):

        """
        This method takes a sentence as input and removes special characters and emojis from it.
        It returns the filtered sentence.
        Arguments:
        `sentence` (str): the sentence from which special characters and emojis should be removed.
        Returns the sentence after removing special characters and emojis.
        Returns a string.
        """

        filtered_text = self.__specials.sub(repl=' ', string=sentence)
        filtered_sentence = self.__characters.sub(repl=' ', string=filtered_text)
        return filtered_sentence


"""
### Example Usage:

```python
s = specials()
filtered_sentence = s.remove_specials("Hello!👋 How are you?😊")
print(filtered_sentence)
```

Output:
```
Hello   How are you  
```
"""