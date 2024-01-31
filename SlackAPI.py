from User import User
from downloader import download, download_file
import streamlit as st

class SlackAPI:
    def __init__(self, slack_bot_user_oauth_token: str):
        self.slack_bot_user_oauth_token = slack_bot_user_oauth_token

    def get_users(self) -> list[str, User]:
        users_list = download(
            url='https://slack.com/api/users.list', 
            token=self.slack_bot_user_oauth_token, 
            content_key='members',
            progress_label='Downloading all workspace users...'
        )
        users = {}
        for user in users_list:
            users[user['id']] = User(user['id'], user['name'], user.get('real_name', None))
        return users

    def get_conversations_history(self, channel_id, ignored_message_subtypes):
        channel_history = download(
            url='https://slack.com/api/conversations.history', 
            query_params={'channel': channel_id}, 
            token=self.slack_bot_user_oauth_token, 
            content_key='messages',
            progress_label=f'Downloading conversations history...'
        )
        
        total_count = len(channel_history)
        channel_history_with_replies = []
        download_progress_bar = st.progress(0/total_count, text=f'Downloading replies for 1/{total_count}')
        for idx in range(0,len(channel_history)-1, 1):
            download_progress_bar.progress(idx/total_count, text=f'Downloading replies for {idx+1}/{total_count}')
            message = channel_history[idx]
            if message.get('type', None) != 'message' or message.get('subtype', None) in ignored_message_subtypes or message.get('bot_profile') is not None:
                continue

            channel_history_with_replies.append(message)
            
            if message.get('thread_ts'):
                # downloads replies
                replies = self.get_replies(channel_id, message['thread_ts'], idx + 1, total_count)
                channel_history_with_replies.extend(replies[1:])
                
        download_progress_bar.empty()
        return channel_history_with_replies

    def get_replies(self, channel_id, thread_ts, position, total_count):
        return download(
            url='https://slack.com/api/conversations.replies', 
            query_params={'channel': channel_id, 'ts': thread_ts}, 
            token=self.slack_bot_user_oauth_token, 
            content_key='messages',
            progress_label=None
        )

    def get_file(self, file):
        return download_file(file["url_private_download"], self.slack_bot_user_oauth_token)