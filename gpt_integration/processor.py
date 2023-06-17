
from docx import Document
import openai
import tiktoken
import os
from itertools import islice

# Embedding model. Currently recommended version. 
EMBEDDING_MODEL = 'text-embedding-ada-002'
CHAT_COMPLETION_CTX_LENGTH = 4096
# Define the query length in order to subtract from the maximum length the chunk can contain. 
QUERY_LENGTH = 200
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
    If the TXT file is larger than the maximum token length specified, it will be chunked in smaller txt files.  
    """
    def __init__(self, txt_file, output_dir):
        self.txt_file = txt_file
        self.output_dir = output_dir

    def chunk_text(self, encoding_name, max_token_length):
        with open(self.txt_file, 'r', encoding='utf-8') as file:
            text = file.read()

            # get encoding and the strings in token lengths
            encoding = tiktoken.get_encoding(encoding_name)

            # convert the text into tokens
            encoded_text = encoding.encode(text)

            # Split the text into chunks based on max_token_length
            # TODO: find a solution to chunk the document semantically, i.e. in semantic regions. 
            encoded_chunks = [encoded_text[i:i + max_token_length] for i in range(0, len(encoded_text), max_token_length)]

            print(len(encoded_chunks[2]))
            
            # Create the output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)

            for i, chunk in enumerate(encoded_chunks):
                print(f'chunk {i} is of length: {len(chunk)}\n')
                # decoded text
                decoded_text = encoding.decode(chunk)
                output_file = os.path.join(self.output_dir, f'report_chunk_{i}.txt')
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(decoded_text)  
    
    def embed_chunks(self):
        # TODO: Save the chunks that include the embeddings together with the texts they embed. Check out the part in the wikipedia notebook.  
        pass

# Chunk the data into txt files of token length
    
# Location where the txt format of the report should be saved. 
txt_file = 'data/sustainability_report.txt'
docx_file: str = 'data/FiBL-Bericht_Basiskonzept-KErn-final_en_preprocessed.docx'
chunked_txt_dir = 'data/sustainability_report_chunks'
preprocessor = Preprocessor(docx_file=docx_file)
# No preprocessing is needed.
# preprocessor.preprocess()

# chunk the report
embedder = TextEmbedder(txt_file=txt_file, output_dir='data/report_chunks')
# Setting the chunk size to be half of the max of the chat completion length. 
# The reason is because the max length is equal to query + knowledge base + response. 
chunk_size = int(CHAT_COMPLETION_CTX_LENGTH/2)
embedder.chunk_text(EMBEDDING_ENCODING, chunk_size)


    