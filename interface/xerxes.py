from agentx.engine_websocket import generate
import streamlit as st

hostname = ""
USER_ROLE = "User"
ASSISTANT_ROLE = "Xerxes"
USER_AVATAR = "👨‍💻"
ASSISTANT_AVATAR = "🐋"
SYSTEM_PROMPT = (
    "You are an AI assistant Named Xerxes, a highly "
    "advanced Persian AI assistant developed by InstinctAI, "
    "a cutting-edge AI startup. My primary function is to assist users with their various needs, "
    "providing expert-level support in wide range of tasks."
)


def main():
    st.sidebar.title("Welcome to Instinct-AI/Xerxes")

    st.sidebar.markdown(
        "_Xerxes is a highly advanced Persian AI assistant developed by InstinctAI_, "
        "a cutting-edge AI startup. My primary function is to assist users "
        "with their various needs, providing expert-level support in wide range of tasks."
    )

    temperature = st.sidebar.slider("Temperature", min_value=0.001, max_value=5.0, value=0.4)
    top_p = st.sidebar.slider("Top P", min_value=0.001, max_value=1.0, value=0.95)
    top_k = st.sidebar.slider("Top K", min_value=1, max_value=100, value=50)
    max_new_tokens = st.sidebar.slider("Max New Tokens", min_value=1, max_value=8192, value=2048)
    max_sequence_length = st.sidebar.slider("Max Sequence Length", min_value=512, max_value=4096, value=4096)

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

        with st.chat_message(USER_ROLE, avatar=USER_AVATAR):
            st.markdown(prompt)
        with st.chat_message(ASSISTANT_ROLE, avatar=ASSISTANT_AVATAR):
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

            response = st.write_stream(_streamer)

            st.session_state.conversation.append({"role": "user", "content": prompt})
            st.session_state.conversation.append({"role": "assistant", "content": response})


if __name__ == '__main__':
    main()
