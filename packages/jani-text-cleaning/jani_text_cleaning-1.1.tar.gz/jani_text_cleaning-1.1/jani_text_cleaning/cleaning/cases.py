class cases:

    """
    This class converts the case of sentence as per user needs.
    """

    def __init__(self,sentence):

        """
        Initializes a __sentence attribute which stores sentence given by user.
        Parameters:
        `sentence` (string): A sentence whose case to be changed.

        Usage
        ```python
        sen = cases('This iS A senTence.')
        """

        self.__sentence = sentence

    def to_lower(self):

        """
         returns the sentence in lower case.

        Usage

        ```python
        a = sen.to_lower()
        print(a)

        Output:
        ```
        this is a sentence.
        ```
        """

        return str(self.__sentence.lower())

    def to_upper(self):

        """
        returns the sentence in upper case.

        Usage

        ```python
        a = sen.to_lower()
        print(a)

        Output:
        ```
        THIS IS A SENTENCE.
        ```
        """

        return str(self.__sentence.upper())

    def to_title(self):

        """
        returns the sentence in title case.

        Usage

        ```python
        a = sen.to_lower()
        print(a)

        Output:
        ```
        This Is A Sentence.
        ```
        """

        return str(self.__sentence.title())

    def to_capitalize(self):

        """
        returns the sentence in capitalize case.

        Usage

        ```python
        a = sen.to_lower()
        print(a)

        Output:
        ```
        This is a sentence.
        ```
        """

        return str(self.__sentence.capitalize())