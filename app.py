from SlackAPI import SlackAPI
import streamlit as st
from store import create_directory_if_not_exists, store_file, store_raw_conversations_history
from print import print_conversation_history

def app():
    # Initialize session state
    if 'channel_name' not in st.session_state:
        st.session_state.channel_name = None
    if 'channel_id' not in st.session_state:
        st.session_state.channel_id = None
    if 'input_fields_ready' not in st.session_state:
        st.session_state.input_fields_ready = False
    if 'conversations_history' not in st.session_state:
        st.session_state.conversations_history = None
    if 'files_downloaded' not in st.session_state:
        st.session_state.files_downloaded = False
    if 'docx_created' not in st.session_state:
        st.session_state.docx_created = False

    st.title('Slack Data Exporter')

    # Input fields
    st.header('Configuration')
    st.markdown('You can find your Slack token [here](https://api.slack.com/apps). Go to Your app > OAuth & Permissions')

    slack_bot_user_oauth_token = st.text_input('Slack Bot User OAuth token')

    default_ignored_message_subtypes = ['thread_broadcast', 'bot_add', 'bot_message', 'channel_join', 'channel_leave', 'reminder_add', 'channel_name']
    ignored_message_subtypes_input = st.text_input('Ignored message subtypes', value=', '.join(default_ignored_message_subtypes))
    ignored_message_subtypes = ignored_message_subtypes_input.split(', ')

    st.header('Slack Channel')
    st.write('Click on the channel name in Slack to get the channel ID at the bottom of the About page.')
    col1, col2 = st.columns(2)
    channel_name = col1.text_input('Channel name')
    channel_id = col2.text_input('Channel ID')

    if channel_name != st.session_state.channel_name or channel_id != st.session_state.channel_id:
        st.session_state.conversations_history = None
        st.session_state.files_downloaded = False
        st.session_state.docx_created = False
    
    st.session_state.channel_name = channel_name
    st.session_state.channel_id = channel_id
    
    st.session_state.input_fields_ready = len(channel_name) > 0 and len(channel_id) > 0 and len(slack_bot_user_oauth_token) > 0

    if not st.session_state.input_fields_ready:
        st.write('⚠️ Please fill in the input fields above.')
    else:
        slack_api = SlackAPI(slack_bot_user_oauth_token)
        users = slack_api.get_users()

        st.header('Conversations history' + ('' if len(channel_name) == 0 else f' for #{channel_name}'))

        if st.session_state.conversations_history is None or len(st.session_state.conversations_history) == 0:
            st.write('🟢 Click on the button below to start')

        history_button = st.button('(1) Download conversations history (json)', disabled=not st.session_state.input_fields_ready)
        if history_button:
            create_directory_if_not_exists(f'Output/{channel_name}')

            st.session_state.conversations_history = slack_api.get_conversations_history(channel_id, ignored_message_subtypes)
            store_raw_conversations_history(st.session_state.conversations_history, channel_name)

        files_button = st.button('(2) Download all files', disabled=st.session_state.conversations_history is None)
        if files_button:
            files = []
            for message in st.session_state.conversations_history:
                if message.get('files'):
                    files.extend(message['files'])

            files_count = len(files)
            file_idx = 0
            download_progress_bar = st.progress(0, text=f'Downloading files...{file_idx + 1}/{files_count}')

            for file in files:
                download_progress_bar.progress(file_idx/files_count, text=f'Downloading files...{file_idx + 1}/{files_count}')

                file_data = slack_api.get_file(file)
                if file_data:
                    store_file(file_data, file["id"], file["name"], channel_name)

                file_idx += 1

            st.session_state.files_downloaded = True
            download_progress_bar.empty()

        docx_button = st.button('(3) Create docx', disabled=st.session_state.files_downloaded is False)
        if docx_button:
            print_conversation_history(st.session_state.conversations_history, users, channel_id, channel_name, slack_api)
            st.session_state.docx_created = True

            
        if st.session_state.docx_created:
            st.write('✅ Done! Go to the Output folder to see the results.')
