from fastapi import FastAPI
from typing import AsyncGenerator
from pydantic import BaseModel
from helper.rag_helper_functions import construct_chain, validate_api_key
from langchain.memory import ConversationBufferWindowMemory
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableSerializable
from helper.prompts import system_message

app = FastAPI()


class Query(BaseModel):
    human_msg: str


class APIKeyValidation(BaseModel):
    api_key: str


class APIKeyValidationResponse(BaseModel):
    valid_api_key: bool


class LLMParamsValidation(BaseModel):
    temperature: float
    top_p: float
    max_tokens: int


llm_params = {}
api_key = ""

# Instantiate the memory
chat_history = ConversationBufferWindowMemory(k=5)


@app.post("/set_api_key")
def set_api_key(input: APIKeyValidation) -> APIKeyValidationResponse:
    """
    Set the OpenAI API key and validate it.

    Args:
        input (APIKeyValidation): Object containing the API key to validate

    Returns:
        APIKeyValidationResponse: Object containing boolean indicating if the API key is valid
    """
    global llm_params, api_key
    # global chain
    api_key = input.api_key
    api_key_is_valid = validate_api_key(api_key)
    llm_params = {"temperature": 0.3, "top_p": 0.3, "max_tokens": 1000}

    return {"valid_api_key": api_key_is_valid}


@app.post("/chat")
async def chat(query: Query) -> StreamingResponse:
    """
    Process chat messages and return streaming responses.

    Args:
        query (Query): Object containing the user's message

    Returns:
        StreamingResponse: Server-sent events stream of the model's response
    """
    global llm_params, api_key

    chain = construct_chain(api_key=api_key, llm_params=llm_params)

    async def token_generator(
        question: str,
        chat_history: ConversationBufferWindowMemory,
        chain: RunnableSerializable,
    ) -> AsyncGenerator[str, None]:
        """
        Generate tokens for streaming response.

        Args:
            question (str): The user's question
            chat_history (ConversationBufferWindowMemory): Memory object containing conversation history
            chain (RunnableSerializable): The LangChain chain for processing the query

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

    return StreamingResponse(
        token_generator(query.human_msg, chat_history, chain), media_type="text/plain"
    )


@app.post("/reset_memory")
async def reset_memory() -> dict[str, str]:
    """
    Reset the conversation memory.

    Returns:
        dict[str, str]: Status message confirming memory reset
    """
    global chat_history
    # Create a new memory instance to reset the history
    chat_history = ConversationBufferWindowMemory(k=5)
    return {"status": "success", "message": "Conversation memory has been reset"}


@app.post("/update_llm_params")
async def update_llm_params(input: LLMParamsValidation) -> LLMParamsValidation:
    """
    Update the language model parameters.

    Args:
        input (LLMParamsValidation): Object containing new parameter values for temperature, top_p, and max_tokens

    Returns:
        LLMParamsValidation: Updated language model parameters
    """
    global llm_params

    llm_params["temperature"] = input.temperature
    llm_params["top_p"] = input.top_p
    llm_params["max_tokens"] = input.max_tokens

    return llm_params





