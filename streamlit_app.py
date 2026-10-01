import os
import requests
import streamlit as st

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Enterprise Knowledge & Support Agent",
    page_icon="🤖",
    layout="wide",
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

DEFAULT_STATE = {
    "access_token": None,
    "user_email": None,
    "active_thread_id": None,
    "active_conversation_id": None,
    "messages": [],
    "page": "chat",
    "upload_success": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------
# API helpers
# ---------------------------------------------------------


def auth_headers():
    token = st.session_state.access_token

    if not token:
        return {}

    return {"Authorization": f"Bearer {token}"}


def api_request(method, endpoint, **kwargs):
    url = f"{API_BASE_URL}{endpoint}"

    headers = kwargs.pop("headers", {})
    headers.update(auth_headers())

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=120,
            **kwargs,
        )

        return response

    except requests.RequestException as exc:
        st.error(f"Could not connect to backend: {exc}")

        return None


# ---------------------------------------------------------
# Auth API
# ---------------------------------------------------------


def register_user(email, password):
    return api_request(
        "POST",
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )


def login_user(email, password):
    return api_request(
        "POST",
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )


# ---------------------------------------------------------
# Conversation API
# ---------------------------------------------------------


def create_conversation():
    return api_request(
        "POST",
        "/conversations",
    )


def get_conversations():
    return api_request(
        "GET",
        "/conversations",
    )


def get_conversation(thread_id):
    return api_request(
        "GET",
        f"/conversations/{thread_id}",
    )


# ---------------------------------------------------------
# Document API
# ---------------------------------------------------------


def get_documents():
    return api_request(
        "GET",
        "/documents",
    )


def upload_document(uploaded_file):

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }

    return api_request(
        "POST",
        "/documents/upload",
        files=files,
    )


# ---------------------------------------------------------
# Chat API
# ---------------------------------------------------------


def send_chat_message(query, thread_id):

    return api_request(
        "POST",
        "/chat",
        json={
            "query": query,
            "thread_id": thread_id,
        },
    )


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------


def logout():

    st.session_state.access_token = None
    st.session_state.user_email = None
    st.session_state.active_thread_id = None
    st.session_state.active_conversation_id = None
    st.session_state.messages = []

    st.rerun()


def render_auth():

    st.title("Enterprise Knowledge & Support Agent")

    st.caption("Sign in to access your enterprise knowledge assistant.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    # ---------------- LOGIN ----------------

    with login_tab:

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                key="login_email",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password",
            )

            submitted = st.form_submit_button(
                "Login",
                use_container_width=True,
            )

        if submitted:

            if not email or not password:
                st.warning("Enter both email and password.")
                return

            with st.spinner("Signing in..."):

                response = login_user(email, password)

            if response is None:
                return

            if response.ok:

                payload = response.json()

                st.session_state.access_token = payload["access_token"]

                st.session_state.user_email = email

                st.session_state.messages = []

                st.session_state.active_thread_id = None

                st.session_state.active_conversation_id = None

                st.success("Logged in successfully.")

                st.rerun()

            else:

                try:
                    detail = response.json().get("detail", "Login failed.")

                except ValueError:
                    detail = response.text or "Login failed."

                st.error(detail)

    # ---------------- REGISTER ----------------

    with register_tab:

        with st.form("register_form"):

            email = st.text_input(
                "Email",
                key="register_email",
                placeholder="you@example.com",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="register_password",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="register_confirm_password",
            )

            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True,
            )

        if submitted:

            if not email or not password:

                st.warning("Enter an email and password.")

                return

            if password != confirm_password:

                st.error("Passwords do not match.")

                return

            with st.spinner("Creating account..."):

                response = register_user(email, password)

            if response is None:
                return

            if response.ok:

                st.success("Account created. You can now log in.")

            else:

                try:

                    detail = response.json().get("detail", "Registration failed.")

                except ValueError:

                    detail = response.text or "Registration failed."

                st.error(detail)


# ---------------------------------------------------------
# Conversation helpers
# ---------------------------------------------------------


def ensure_conversation():

    if st.session_state.active_thread_id:
        return True

    response = create_conversation()

    if response is None:
        return False

    if not response.ok:

        try:

            detail = response.json().get("detail", "Could not create conversation.")

        except ValueError:

            detail = response.text or "Could not create conversation."

        st.error(detail)

        return False

    data = response.json()

    st.session_state.active_thread_id = data["thread_id"]

    st.session_state.active_conversation_id = data.get("conversation_id")

    return True


def new_chat():

    st.session_state.active_thread_id = None
    st.session_state.active_conversation_id = None
    st.session_state.messages = []
    st.session_state.page = "chat"

    st.rerun()


def open_conversation(thread_id):

    response = get_conversation(thread_id)

    if response is None:
        return

    if not response.ok:

        try:

            detail = response.json().get("detail", "Could not load conversation.")

        except ValueError:

            detail = response.text or "Could not load conversation."

        st.error(detail)

        return

    data = response.json()

    st.session_state.active_thread_id = data["thread_id"]

    st.session_state.active_conversation_id = data["conversation_id"]

    st.session_state.messages = data.get("messages", [])

    st.session_state.page = "chat"

    st.rerun()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------


def render_sidebar():

    with st.sidebar:

        st.title("Enterprise AI")

        if st.session_state.user_email:

            st.caption(st.session_state.user_email)

        st.button(
            "＋ New Chat",
            use_container_width=True,
            on_click=new_chat,
        )

        st.divider()

        # ---------------- NAVIGATION ----------------

        if st.button(
            "💬 Chat",
            use_container_width=True,
        ):

            st.session_state.page = "chat"

            st.rerun()

        if st.button(
            "📄 Documents",
            use_container_width=True,
        ):

            st.session_state.page = "documents"

            st.rerun()

        st.divider()

        # ---------------- CONVERSATIONS ----------------

        st.subheader("Conversations")

        response = get_conversations()

        if response is None:

            st.caption("Could not load conversations.")

        elif response.ok:

            conversations = response.json()

            if not conversations:

                st.caption("No conversations yet.")

            else:

                for conversation in conversations:

                    conversation_id = conversation["id"]

                    thread_id = conversation["thread_id"]

                    # For now:
                    # Chat 10
                    # Chat 9
                    # Chat 8
                    #
                    # Later we can replace this
                    # with generated conversation titles.

                    label = conversation.get("title") or f"Chat {conversation_id}"

                    is_active = thread_id == st.session_state.active_thread_id

                    if is_active:

                        label = f"🟢 {label}"

                    if st.button(
                        label,
                        key=(f"conversation_" f"{conversation_id}"),
                        use_container_width=True,
                    ):

                        open_conversation(thread_id)

        else:

            try:

                detail = response.json().get("detail", "Could not load conversations.")

            except ValueError:

                detail = response.text or "Could not load conversations."

            st.caption(detail)

        st.divider()

        if st.button(
            "Logout",
            use_container_width=True,
        ):

            logout()


# ---------------------------------------------------------
# Citations
# ---------------------------------------------------------


def render_citations(citations):

    if not citations:
        return

    with st.expander("Sources"):

        for index, citation in enumerate(citations, start=1):

            filename = citation.get("filename") or "Unknown document"

            page = citation.get("page")

            chunk_index = citation.get("chunk_index")

            document_id = citation.get("document_id")

            # PyPDFLoader pages are 0 indexed.
            if isinstance(page, int):
                page_display = page + 1
            else:
                page_display = page

            st.markdown(f"""
**{index}. {filename}**

- Document ID: `{document_id}`
- Page: `{page_display}`
- Chunk: `{chunk_index}`
""")


# ---------------------------------------------------------
# Chat page
# ---------------------------------------------------------


def render_chat():

    st.title("Knowledge Assistant")

    st.caption(
        "Ask questions about your uploaded enterprise documents or general topics."
    )

    # ---------------- DISPLAY HISTORY ----------------

    for message in st.session_state.messages:

        role = message["role"]

        with st.chat_message(role):

            st.markdown(message["content"])

            if role == "assistant":

                render_citations(message.get("citations", []))

    # ---------------- USER INPUT ----------------

    prompt = st.chat_input("Ask a question...")

    if not prompt:
        return

    # Add user message to frontend immediately

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # Create conversation if this is new chat

    if not ensure_conversation():
        return

    # ---------------- CALL BACKEND ----------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            response = send_chat_message(
                prompt,
                st.session_state.active_thread_id,
            )

        if response is None:
            return

        if not response.ok:

            try:

                detail = response.json().get("detail", "Chat request failed.")

            except ValueError:

                detail = response.text or "Chat request failed."

            st.error(detail)

            return

        data = response.json()

        answer = data["answer"]

        citations = data.get("citations", [])

        st.markdown(answer)

        render_citations(citations)

        # Save assistant response in frontend state

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "citations": citations,
            }
        )


# ---------------------------------------------------------
# Documents page
# ---------------------------------------------------------


def render_documents():

    st.title("Documents")

    st.caption("Upload PDF or DOCX files to your enterprise knowledge base.")

    # ---------------- FLASH MESSAGE ----------------

    if st.session_state.upload_success:

        st.success(st.session_state.upload_success)

        st.session_state.upload_success = None

    # ---------------- UPLOAD ----------------

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "docx"],
    )

    if uploaded_file is not None:

        st.write(f"Selected: **{uploaded_file.name}**")

        if st.button(
            "Upload and ingest",
            type="primary",
        ):

            with st.spinner("Uploading, chunking, embedding, and indexing..."):

                response = upload_document(uploaded_file)

            if response is None:
                return

            if response.ok:

                data = response.json()

                filename = data.get("filename", uploaded_file.name)

                chunks = data.get("chunks_created")

                message = f"{filename} uploaded successfully."

                if chunks is not None:

                    message += f" Chunks created: {chunks}"

                st.session_state.upload_success = message

                st.rerun()

            else:

                try:

                    detail = response.json().get("detail", "Upload failed.")

                except ValueError:

                    detail = response.text or "Upload failed."

                st.error(detail)

    # ---------------- DOCUMENT LIST ----------------

    st.divider()

    st.subheader("Your documents")

    response = get_documents()

    if response is None:
        return

    if not response.ok:

        try:

            detail = response.json().get("detail", "Could not load documents.")

        except ValueError:

            detail = response.text or "Could not load documents."

        st.error(f"Could not load documents: {detail}")

        return

    documents = response.json()

    if not documents:

        st.info("No documents uploaded yet.")

        return

    for document in documents:

        with st.container(border=True):

            col1, col2, col3 = st.columns([4, 2, 2])

            with col1:

                st.markdown(f"**{document.get('filename', 'Untitled')}**")

            with col2:

                st.caption(f"Type: {document.get('file_type', '-')}")

            with col3:

                status = document.get("status", "unknown")

                st.caption(f"Status: {status}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------


def main():

    # Not authenticated
    if not st.session_state.access_token:

        render_auth()

        return

    # Authenticated

    render_sidebar()

    if st.session_state.page == "documents":

        render_documents()

    else:

        render_chat()


if __name__ == "__main__":
    main()
