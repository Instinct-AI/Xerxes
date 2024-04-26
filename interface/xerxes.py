from agentx.engine_websocket import generate
import streamlit as st

USER_ROLE = "User"
ASSISTANT_ROLE = "Xerxes"
USER_AVATAR = "👨‍💻"
ASSISTANT_AVATAR = "🐋"
SYSTEM_PROMPT = (
    "You are an AI assistant Named Xerxes, a highly "
    "advanced Persian AI assistant developed by InstinctAI, "
    "a cutting-edge AI startup. which primary function is to assist users with their various needs, "
    "providing expert-level support in wide range of tasks."
)


def clear_conversation():
    st.session_state.conversation = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]


def re_generate(
        hostname: str,
        top_p: float,
        top_k: int,
        temperature: float,
        max_new_tokens: int,
        max_sequence_length: int,
):
    def _streamer():

        conversation = st.session_state.conversation
        if len(conversation) == 1:
            st.warning("No conversation found!")
        else:
            if len(conversation) > 12:
                system = conversation[0]
                conversation = conversation[-10:]
                conversation = [system, *conversation]
            prompt = conversation[-2]["content"]
            conversation = conversation[0:-2]
            for res in generate(
                    hostname=hostname,
                    prompt=prompt,
                    conversation=conversation,
                    top_p=top_p,
                    top_k=top_k,
                    temperature=temperature,
                    max_new_tokens=max_new_tokens,
                    max_sequence_length=max_sequence_length,
                    stream=True
            ):
                yield res.response

    with st.chat_message(ASSISTANT_ROLE, avatar=ASSISTANT_AVATAR):
        st.write_stream(_streamer)


def create_streamer(
        hostname: str,
        prompt: str,
        top_p: float,
        top_k: int,
        temperature: float,
        max_new_tokens: int,
        max_sequence_length: int,
):
    def _streamer():
        conversation = st.session_state.conversation
        if len(conversation) > 12:
            system = conversation[0]
            conversation = conversation[-10:]
            conversation = [system, *conversation]
        for res in generate(
                hostname=hostname,
                prompt=prompt,
                conversation=conversation,
                top_p=top_p,
                top_k=top_k,
                temperature=temperature,
                max_new_tokens=max_new_tokens,
                max_sequence_length=max_sequence_length,
                stream=True
        ):
            yield res.response

    return _streamer


def main():
    st.sidebar.title("Welcome to [Instinct-AI/Xerxes](https://github.com/Instinct-AI/Xerxes)")

    st.sidebar.markdown(
        "_Xerxes is a highly advanced Persian AI assistant developed by InstinctAI_, "
        "a cutting-edge AI startup.\n"
    )
    hostname = st.sidebar.text_input("Hostname", value="")
    temperature = st.sidebar.slider("Temperature", min_value=0.001, max_value=5.0, value=0.4)
    top_p = st.sidebar.slider("Top P", min_value=0.001, max_value=1.0, value=0.95)
    top_k = st.sidebar.slider("Top K", min_value=1, max_value=100, value=50)
    max_new_tokens = st.sidebar.slider("Max New Tokens", min_value=1, max_value=8192, value=2048)
    max_sequence_length = st.sidebar.slider("Max Sequence Length", min_value=512, max_value=4096, value=4096)

    st.sidebar.button("Clear Conversation History", on_click=clear_conversation)
    st.sidebar.button(
        "Re-Generate", on_click=re_generate, kwargs={
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_new_tokens": max_new_tokens,
            "max_sequence_length": max_sequence_length,
            "hostname": hostname
        }
    )

    if "conversation" not in st.session_state:
        st.session_state.conversation = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    for message in st.session_state.conversation:
        if message["role"] != "system":
            with st.chat_message(
                    message["role"],
                    avatar=ASSISTANT_AVATAR if message["role"] == "assistant" else USER_AVATAR
            ):
                st.markdown(message["content"])

    if prompt := st.chat_input("Your Prompt Here ... "):
        if hostname != "":
            with st.chat_message(USER_ROLE, avatar=USER_AVATAR):
                st.markdown(prompt)
            with st.chat_message(ASSISTANT_ROLE, avatar=ASSISTANT_AVATAR):

                response = st.write_stream(
                    create_streamer(
                        hostname=hostname,
                        prompt=prompt,
                        max_new_tokens=max_new_tokens,
                        max_sequence_length=max_sequence_length,
                        top_p=top_p,
                        top_k=top_k,
                        temperature=temperature
                    )
                )

                st.session_state.conversation.append({"role": "user", "content": prompt})
                st.session_state.conversation.append({"role": "assistant", "content": response})
        else:
            st.warning("Please enter a valid Hostname for AgentX ServeEngine")


if __name__ == '__main__':
    main()
