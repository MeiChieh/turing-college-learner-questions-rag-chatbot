from typing import Dict, Any, List
import requests
import streamlit as st


def set_initial_st_state(
    state: Dict[str, Any], initial_vals_dict: Dict[str, Any]
) -> None:
    """
    Sets initial values in the state dictionary if they do not already exist.

    Args:
        state (Dict[str, Any]): The state dictionary to update.
        initial_vals_dict (Dict[str, Any]): Dictionary containing initial key-value pairs to set in state.
    """
    for key, val in initial_vals_dict.items():
        if key not in state:
            state[key] = val

    return state


def restart_chat(state: Dict[str, Any]) -> None:
    """
    Resets the chat state by clearing messages and resetting parameters.

    Args:
        state (Dict[str, Any]): The state dictionary containing chat configurations.
    """
    state["messages"] = []
    state["is_first_msg"] = True
    state["llm_params_curr"]["temperature"] = 0.3
    state["llm_params_curr"]["top_p"] = 0.3
    state["llm_params_curr"]["max_tokens"] = 1000
    state["llm_params_prev"]["temperature"] = 0.3
    state["llm_params_prev"]["top_p"] = 0.3
    state["llm_params_prev"]["max_tokens"] = 1000


def clean_chat_history(state: dict):
    """
    Cleans both frontend and backend chat history by resetting UI state and making a request to reset backend memory.

    Args:
        state (Dict[str, Any]): The Streamlit session state containing chat configurations and message history.

    Returns:
        None
    """
    # Rest the chat in ui memory
    restart_chat(state)
    # Make a request to reset backend memory
    response = requests.post("http://127.0.0.1:8000/reset_memory")
    if response.status_code == 200:
        print("Chat history has been reset.")


def send_first_message(message_state: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sends the first assistant message to initialize the conversation.

    Args:
        message_state (List[Dict[str, Any]]): List representing the message history.

    Returns:
        List[Dict[str, Any]]: Updated message state including the first message.
    """
    first_msg_1 = """
    Hey, do you have any question with your Turing College learning journey ?
    """

    message_state.append({"role": "assistant", "content": first_msg_1, "avatar": "🤖"})

    return message_state


def has_param_changed(
    param_name: str, param_val: float, llm_params_curr: dict, llm_params_prev: dict
):
    """
    Check if a parameter has changed and update the backend and ui state if it has.

    Args:
        param_name (str): Name of the parameter (e.g., "temperature", "top_p", "max_tokens")
        param_val (float): Current value of the parameter
        llm_params_curr (dict): Current LLM parameters dictionary
        llm_params_prev (dict): Previous LLM parameters dictionary

    Returns:
        dict: Updated LLM parameters dictionary

    """

    if param_val != llm_params_prev[param_name]:
        
        # Update the current params
        llm_params_curr[param_name] = param_val

        # Send request to backend with all current params
        response = requests.post(
            "http://127.0.0.1:8000/update_llm_params",
            json=llm_params_curr,
            timeout=5,
        )

        # Inspect status code
        if response.status_code == 200:

            st.sidebar.success(f"{param_name} updated successfully!", icon="✅")
            return response.json()
        else:
            st.sidebar.error(
                f"Failed to update {param_name}: {response.status_code}", icon="🚨"
            )
    return llm_params_prev
