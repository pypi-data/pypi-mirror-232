from .cleaning import hyperlinks
from .cleaning import htmls
from .cleaning import stopwords
from .cleaning import cases
from .cleaning import specials
from .cleaning import punctuations
from .cleaning import method
from .cleaning import tokenize


class NLPCleaning:

    """
    This class cleans and tokenizes text by removing hyperlinks, HTML codes, punctuation,
    special characters like emojis, and stopwords (which can be user-defined).
    The class then converts all text to lowercase and tokenizes it.
    Finally, it returns a list of lemmatized, stemmed, or tokenized words, depending on the user's preference.
    """

    def __init__(self,input_text,custom_stopwords = [], method = 'l'):

        """
        Takes 3 parameters.
        Parameters:
        `input_text` (string): Text which needs to be cleaned.
        `custom_stopwords` (set): A set of custom stopwords to add.
         `method` (string): Method which user wants to apply in tokenized text.
                            Default:
                                    'l'-->      lemmatize the tokenized text and returns it.
                                    's'-->      stemms the tokenized text and returns it.
                                    'none'-->   just returns the tokenized text.
        This method initializes __input text, ____custom_stopwords and __method(in lowercase) attributes to their respective inputs.
        """

        if not isinstance(input_text,str):
            raise TypeError("Input text must be in string format")
        if isinstance(custom_stopwords,list):
            if not len(custom_stopwords) <= 0:
                for val in custom_stopwords:
                    if not isinstance(val,str):
                        raise TypeError('Custom Stopwords must be a list of strings')
        else:
            raise TypeError('Custom Stopwords must be a list')
        if not isinstance(method,str):
            raise TypeError('Method parameter must be a string')
        else:
            if method.lower() != 'l' and method.lower() != 's' and method.lower() != 'none':
                raise ValueError('Method parameter must be "l"(lemmetizer) or "s"(stemmer) or "none"')

        self.__input = input_text
        self.__custom_stopwords = custom_stopwords
        self.__method = method.lower()
    def __repr__(self):

        """"
        Returns a string representation of the input text.
        Takes no parameters.
        Returns a string.

        Usage

        ```python
        a = NLPCleaning(input_text="This is a sentence.")
        print(a)

        Output:
        ```
        This is a sentence.
        ```
        """

        return str(self.__input)

    def clean(self):

        """
        Returns a clean list of tokenized words.
        Takes no parameters.
        Returns a list.
        """
        lowercase_filter = cases.cases(sentence=self.__input).to_lower()
        hyperlink_filter = hyperlinks.hyperlinks().remove_hyperlinks(sentence=lowercase_filter)
        html_filter = htmls.htmls().remove_htmls(sentence=hyperlink_filter)
        punctuation_filter = punctuations.punctuations().remove_punctuation(sentence=html_filter)
        special_filter = specials.specials().remove_specials(sentence=punctuation_filter)
        stopwords_filter = stopwords.stopwords()
        if len(self.__custom_stopwords) != 0:
            self.__custom_stopwords = stopwords_filter.add_stopwords(custom_stopwords=self.__custom_stopwords)
        stopwords_filter = stopwords_filter.remove_stopwords(sentence=special_filter,custom_stopwords=self.__custom_stopwords)
        tokenize_text = tokenize.tokenize().word_tokenize(sentence=stopwords_filter)
        if self.__method.lower() == 'l':
            output_text = method.lemmetizer().word_net(sentence=tokenize_text)
            return output_text
        elif self.__method.lower() == 's':
            output_text = method.stemmer().stems(sentence=tokenize_text)
            return output_text
        elif self.__method.lower() == 'none':
            return tokenize_text
        else:
            raise ValueError('Method parameter must be "l"(lemmetizer) or "s"(stemmer)')



"""
Usage

```python
a = NLPCleaning(input_text="This is a sentence with some verbs like running, dancing,etc,... and a hyperlink: https://www.google.com.Punctuations like?.,.!!! emoji👋👋😊😊😊 some html <html><head></body><h1><p></html?> some custom stopwords which we wont need like alpha,beta,gamma,etc...,.,",custom_stopwords=['alpha','beta','Gamma'],method='l')
clean = a.clean()
print(clean)

Output:
```
['sentence', 'verbs', 'like', 'run', 'dance', 'etc', 'hyperlink', 'like', 'emoji', 'html', 'custom', 'stopwords', 'wont', 'need', 'like', 'etc']
```
"""