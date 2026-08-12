import os 
from dotenv import load_dotenv
from groq import Groq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, convert_to_messages

load_dotenv()
my_api_key = os.getenv('groq_api_key')
if not my_api_key:
    raise ValueError('Could not find Groq API Key')


client = Groq(api_key=my_api_key)
model = "llama-3.3-70b-versatile"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'vector_db')

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
RETRIEVAL_K = 5

SYSTEM_PROMPT = """
You are a knowledgeable, friendly assistant representing the company llm.
You are chatting with a user about its doubts regarding Company details.
If relevant, use the given context to answer any question.
If you don't know the answer, say so.
Context:
{context}
"""

vectorstore = Chroma(embedding_function=embeddings, persist_directory=DB_NAME)
retrieval = vectorstore.as_retriever()
llm = ChatGroq(temperature=0, model_name=model, groq_api_key=my_api_key)


def fetch_content(question):
    return retrieval.invoke(question, k=RETRIEVAL_K)

def answer_question(question: str, history: list[dict] = []) -> tuple[str, list[Document]]:
    docs = fetch_content(question)
    context = "\n\n".join(doc.page_content for doc in docs)
    system_prompt = SYSTEM_PROMPT.format(context=context)
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(convert_to_messages(history))
    messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    return response.content, docs
        
    