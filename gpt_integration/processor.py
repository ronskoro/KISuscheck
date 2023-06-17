
from docx import Document
import openai
import tiktoken
from itertools import islice

# Embedding model. Currently recommended version. 
EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_CTX_LENGTH = 8191
EMBEDDING_ENCODING = 'cl100k_base'

class Preprocessor:
    """
    This class is used for preprocessing DOCX documents and chunking them into separate text files.
    """
    def __init__(self, docx_file):
        self.docx_file = docx_file

    def convert_docx_to_txt(self, txt_file='data/sustainability_report.txt'):
        # Open the DOCX file
        doc = Document(self.docx_file)

        # Extract the text from paragraphs
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])

        # Write the text to a TXT file
        with open(txt_file, 'w', encoding='utf-8') as file:
            file.write(text)
    
    def preprocess(self):
        """
        The method preprocesses the data. 
        The preprocessing pipeline can be expanded by adding additional function calls. 
        """
        print(f'Preprocessing  of {self.docx_file} initiated...')
        self.convert_docx_to_txt()
        print('Preprocessing done.')

class TextEmbedder:
    """
    This class is used for embedding TXT files. 
    If the TXT file is larger than the maximum token length, it will be chunked in smaller txt files.  
    """
    def __init__(self, txt_file):
        self.txt_file = txt_file

    def __batched(iterable, n):
        """Batch data into tuples of length n. The last batch may be shorter."""
        # batched('ABCDEFG', 3) --> ABC DEF G
        if n < 1:
            raise ValueError('n must be at least one')
        it = iter(iterable)
        while (batch := tuple(islice(it, n))):
            yield batch
    
    def chunked_tokens(self, encoding_name, chunk_length):
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(self.txt_file)
        chunks_iterator = self.__batched(tokens, chunk_length)
        yield from chunks_iterator
    
# Location where the txt format of the report should be saved. 
txt_file = 'data/sustainability_report.txt'
docx_file: str = 'data/FiBL-Bericht_Basiskonzept-KErn-final_en.docx'
preprocessor = Preprocessor(docx_file=docx_file)
preprocessor.preprocess()
    