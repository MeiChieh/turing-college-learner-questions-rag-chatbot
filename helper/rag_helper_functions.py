from upstash_vector import Index
import dotenv, os
from typing import Dict, Any, AsyncGenerator
from langchain.schema import BaseMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables import RunnableParallel, RunnableSerializable
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
from helper.prompts import response_prompt, system_message
import openai


dotenv.load_dotenv()
UPSTASH_TC_HYBRID_CHAT_TOKEN = os.getenv("UPSTASH_TC_HYBRID_CHAT_TOKEN")
UPSTASH_TC_HYBRID_INDEX_ENDPOINT = os.getenv("UPSTASH_TC_HYBRID_INDEX_ENDPOINT")
openai_api_key = os.getenv("OPENAI_API_KEYy")


def retrieve_ref(query_str, top_k=5) -> list[Dict | None]:
    """
    Retrieve relevant reference documents from the Upstash vector index.

    Args:
        query_str (str): The query string to search for
        top_k (int, optional): Number of top results to return. Defaults to 5.

    Returns:
        list[Dict | None]: List of metadata from matched documents
    """
    index = Index(
        url=UPSTASH_TC_HYBRID_INDEX_ENDPOINT, token=UPSTASH_TC_HYBRID_CHAT_TOKEN
    )

    ref_ls = index.query(
        data=query_str,
        top_k=top_k,
        include_metadata=True,
    )
    metadata_ls = [ref.metadata for ref in ref_ls]
    return metadata_ls


retrieve_ref_func = lambda params: retrieve_ref(params["question"], top_k=5)


def construct_chain(
    api_key: str, llm_params: dict
) -> RunnableSerializable[Any, BaseMessage]:
    """
    Construct a LangChain processing chain with the specified parameters.

    Args:
        api_key (str): OpenAI API key
        llm_params (dict): Dictionary containing LLM parameters (temperature, top_p, max_tokens)

    Returns:
        RunnableSerializable: Configured LangChain processing chain
    """
    temperature = llm_params["temperature"]
    top_p = llm_params["top_p"]
    max_tokens = llm_params["max_tokens"]

    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        streaming=True,
        max_retries=3,
    )

    input_mapping = {
        "chat_history": lambda input: input["chat_history"],
        "question": lambda input: input["question"],
        "context": retrieve_ref_func,
    }

    chain = RunnableParallel(input_mapping) | response_prompt | llm
    return chain


async def token_generator(
    question: str,
    chat_history: ConversationBufferWindowMemory,
    chain: RunnableSerializable,
) -> AsyncGenerator[str, None]:
    """
    Generate response tokens asynchronously from the LLM.

    Args:
        question (str): User's input question
        chat_history (ConversationBufferWindowMemory): Conversation memory buffer
        chain (RunnableSerializable): LangChain processing chain

    Yields:
        str: Generated response tokens
    """
    full_answer = ""
    chat_history_with_system_message = (
        system_message + "\n" + chat_history.load_memory_variables({})["history"]
    )
    for chunk in chain.stream(
        {
            "chat_history": chat_history_with_system_message,
            "question": question,
        }
    ):
        chunk_content = chunk.content
        full_answer += chunk_content
        yield chunk_content

    chat_history.save_context({"input": question}, {"output": "full_answer"})


def validate_api_key(api_key: str) -> bool:
    """
    Validates the OpenAI API key by attempting to list models.

    Args:
        api_key (str): The API key to validate

    Returns:
        bool: True if the API key is valid, False otherwise
    """
    api_key_is_valid = False

    try:
        client = openai.Client(api_key=api_key)
        _ = client.models.list()
        api_key_is_valid = True
    except Exception as e:
        api_key_is_valid = False
        print(f"Error validating API key: {e}")

    return api_key_is_valid
