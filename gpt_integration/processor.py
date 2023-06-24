from docx import Document
import openai
import tiktoken
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from openai.embeddings_utils import get_embedding, cosine_similarity

load_dotenv('.env')
openai.api_key=os.environ.get('OPENAI_API_KEY')

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
            # TODO: find a solution to chunk the document semantically, i.e. semantic segmentations. 
            encoded_chunks = [encoded_text[i:i + max_token_length] for i in range(0, len(encoded_text), max_token_length)]
            
            # Create the output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)

            for i, chunk in enumerate(encoded_chunks):
                print(f'chunk {i} is of length: {len(chunk)}\n')
                # decoded text
                decoded_text = encoding.decode(chunk)
                output_file = os.path.join(self.output_dir, f'report_chunk_{i}.txt')
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(decoded_text)  

    def embed_chunks(self, embeddings_file):
        df = pd.DataFrame(columns=["text", "embedding"])
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()

                    embedding = openai.Embedding.create(
                        input=text, 
                        model=EMBEDDING_MODEL
                    )['data'][0]['embedding']

                    # append new embedding
                    print(f'the text: {text}\n')
                    print(f'The embedding: {embedding}')
                    df = df.append({'text': text, 'embedding': embedding}, ignore_index=True)

        # save the embedding with the corresponding text
        df.to_csv(embeddings_file, index=False, mode='w')

    def search_chunks(self, embeddings_file, query, k=3, pprint=True):
        """
        This function provides semantic search using embeddings.
        Search the chunks and find the k most similar chunks based on the query.
        """
        df = pd.read_csv(embeddings_file)
        df["embedding"] = df.embedding.apply(eval).apply(np.array)
        query_embedding = get_embedding(
            query, 
            engine=EMBEDDING_MODEL
        )

        # Apply cosine similarity to find the k most similar chunks. 
        df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, query_embedding))
        
        results = (
        df.sort_values("similarity", ascending=False)
        .head(k)
        # .combined.str.replace("Title: ", "")
        # .str.replace("; Content:", ": ")
        )

        # todo: combine the strings
        
        # print results
        if pprint:
            for r in results:
                print(r[:200])
                print()
        
        return results




    