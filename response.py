import os
import openai
from openai import OpenAI

import pinecone
from langchain_community.vectorstores import Pinecone
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings

# from langchain.llms import OpenAI 
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain.document_loaders import DirectoryLoader
from langchain.chains.question_answering import load_qa_chain

from langchain.schema import Document 
import pandas as pd
import requests
from langchain.chains.summarize import load_summarize_chain
import numpy as np
import re

# ____________________________________________
# WILL BE USED IN FLASK APP IN FRONT END 

# host: https://arabic-bot-74438d8.svc.gcp-starter.pinecone.io
# pinecone_environment = "gcp-starter"
# pinecone_index_name  = "arabic-bot"
# pinecoy_api_key = "83ffe0ca-4d89-4d5e-9a46-75bf76d6106f"

# embeddings = OpenAIEmbeddings(model_name="ada")
# unique_id  = "aaa365fe031e4b5ab90aba54eaf6012e"

# if len(messages) == 0 :  
#     relevant_docs = get_relevant_docs(query, embeddings, unique_id, final_doc_list )
#     qa_chain = define_qa(relevant_docs)
# else : 
#     relevant_docs = get_relevant_docs(query, final_doc_list = None) 
  
# answer = get_answer(query, qa_chain, relevant_docs)


# messages.append( { "sender": f"{query}", "response": f"{answer}"   }  ) 

#  for message in messages: 
        # message.sender
        # message.response





def get_relevant_docs(query, embeddings, unique_id, final_doc_list = None ):
  
  document_count = 3
  pinecone_environment = "gcp-starter"
  pinecone_index_name  = "arabic-bot"
  pinecone_api_key = "83ffe0ca-4d89-4d5e-9a46-75bf76d6106f"
  
  relevant_docs = similar_docs(query, document_count ,pinecone_api_key, pinecone_environment, pinecone_index_name, embeddings, unique_id )
  
  return  relevant_docs
   
  # names =  metadata_filename(relevant_docs )
  # scores = get_score(relevant_docs)
  # content = docs_content(relevant_docs)
  
  # answer = get_answer(query, qa)
  # return answer 
# ____________________________________________

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
# from langchain.memory import ConversationSummaryMemory


def define_qa(): 
    
    # from langchain.llms import OpenAI 
    from langchain_community.chat_models import ChatOpenAI
    #  model_name = "text-davinci-003"
    model_name = "gpt-3.5-turbo"
    # model_name = "gpt-4"
    llm = ChatOpenAI()
    qa_chain =load_qa_chain(llm, chain_type="map_reduce")

    return qa_chain 



def get_answer(query, qa_chain, relevant_docs ):
    
    # qa =  load_qa_chain(llm, chain_type="stuff")
    # answer =  qa_chain.run(input_documents=relevant_docs, question=query)
    answer = qa_chain.invoke({'input_documents':relevant_docs, 'question':query})
    # answer =  qa_chain.invoke(input=relevant_docs, question=query)
    print(answer)
    
    return answer


   # similar_docs = get_similiar_docs(query)
   # answer = qa_chain.run(input_documents=similar_docs, question=query)


def get_api(hexcode):
    
 
    bytes_string = bytes.fromhex(hexcode)

    decoded_string = bytes_string.decode("utf-8")
    return  decoded_string
    





# directory = '/content/data'

def load_docs(directory):
  loader = DirectoryLoader(directory)
  documents = loader.load()
  return documents


def split_docs(documents, chunk_size=1000, chunk_overlap=0):
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
  docs = text_splitter.split_documents(documents)
  return docs

# PDF UPLOAD --> INTO TEXT DOCUMENT --> EMBEDDING FUNCTION -->  PUSH INTO PINECONE WITH THEIR EMBEDDINGS

# DOCUMENTS TO MATCH = 3

# QUERY MATCH --> SIMILAR SEARCH --> RELEVANT DOCS --> RELEVANT DOCS INTO SUMMARY 

def similar_docs(query,k,pinecone_api_key,pinecone_environment,pinecone_index_name,embeddings,unique_id):

    pinecone.init(
    api_key=pinecone_api_key,
    environment=pinecone_environment
    )

    index_name = pinecone_index_name

    index = pull_from_pinecone(pinecone_api_key,pinecone_environment,pinecone_index_name,embeddings)
    print(pinecone_api_key,pinecone_environment, pinecone_index_name )
    similar_docs = index.similarity_search_with_score(query, int(k),{"unique_id":unique_id})
    similar_docs = index.similarity_search(query, int(k) ,{"unique_id":unique_id}  )
    #print(similar_docs)
    return similar_docs


def create_docs_web(directory, unique_id, stop_idx= None):
  
  user_file_list = os.listdir(directory)
  docs = []
  for index, filename in enumerate(user_file_list):

      uploaded = []
      ext = filename.split(".")[-1]
      filepath = os.path.join(directory, filename)

      if stop_idx:  
            if index >= stop_idx : break  

      # Use PDFLoader for .pdf files
      if ext == "pdf":
          loader = PyPDFLoader(filepath)
          doc = loader.load()

      # Skip other file types
      else:
          continue
      docs.append(Document( page_content= doc[0].page_content , metadata={"name": f"{filename}" , "unique_id":unique_id } ) )
      uploaded.append(filename)

  print("Files Uploaded ", uploaded, len(uploaded))
  print("Files Not Uploaded", user_file_list[stop_idx:], len(user_file_list[stop_idx:]))
  return docs







def docs_content(relevant_docs):
    content = [] 
    for doc in relevant_docs:    
        content.append(doc[0].page_content)

    return content



#Create embeddings instance
def create_embeddings_load_data():
    # embeddings = OpenAIEmbeddings( model_name="ada")
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") #  384
    return embeddings


#Function to push data to Vector Store - Pinecone here
def push_to_pinecone(pinecone_api_key,pinecone_environment,pinecone_index_name,embeddings,docs):

    pinecone.init(
    api_key=pinecone_api_key,
    environment=pinecone_environment
    )
    print("done......2")
    Pinecone.from_documents(docs, embeddings, index_name=pinecone_index_name)
    

def get_response(user_input):

    from openai import OpenAI
    client = OpenAI()
    completion   = client.chat.completions.create(
        model    = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{user_input}"}
        ]
        )

    return  completion.choices[0].message.content



def pull_from_pinecone(pinecone_apikey,pinecone_environment,pinecone_index_name,embeddings):

    pinecone.init(
    api_key=pinecone_apikey,
    environment=pinecone_environment
    )

    index_name = pinecone_index_name

    index = Pinecone.from_existing_index(index_name, embeddings)
    return index

def get_score(relevant_docs):
  scores = []
  for doc in relevant_docs:
      scores.append(doc[1])

  return scores


def metadata_filename( document ) : 
   
   names = [ ]
   for doc in document: 
    
        text = str(doc[0].metadata["name"] )
        pattern = r"name=\'(.*?)\'"
        matches = re.findall(pattern, text)
        names.append(matches) 

   return names
