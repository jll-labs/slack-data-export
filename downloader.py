import requests
import streamlit as st
import time

@st.cache_data(ttl="24h", show_spinner=False)
def download_file(url, token: str):
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.write(f"Failed to download file. HTTP Status Code: {response.status_code}\n{response.json()}")
        return None
    
    return response.content

@st.cache_data(ttl="24h", show_spinner=False)
def download(url, token: str, content_key: str, progress_label: str, query_params: list[str, str] = {}):
    download_progress_bar = st.progress(0, text=progress_label) if progress_label else None
    params = query_params or {}
    all_data = []  # To collect all the pages of data
    next_cursor: str = None
    max_results = 200  # Number of items per page
    page_number = 1
    
    while True:
        # Add pagination parameters to the request
        params['limit'] = max_results
        if next_cursor:
            params['cursor'] = next_cursor
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token
        }
        if download_progress_bar:
            download_progress_bar.progress(0, text=f'{progress_label}' + f' {len(all_data)}' if len(all_data) > 0 else '')
        response = __get_data(url, params, headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # store_as_test_data(url, data.get(content_key, []))
            all_data.extend(data.get(content_key, []))
            next_cursor = data.get('response_metadata', {}).get('next_cursor', None)

            if next_cursor is None or len(next_cursor) == 0:
                if download_progress_bar:
                    download_progress_bar.empty()
                return all_data  # All pages have been fetched, exit loop
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 10))
            for i in range(retry_after):
                if download_progress_bar:
                    download_progress_bar.progress((retry_after - i)/retry_after, f"Rate limit exceeded. Retrying after {retry_after - i} seconds...")
                time.sleep(1)
        else:
            data = response.json()
            st.write(f"Failed to download data. HTTP Status Code: {response.status_code}\n{data}")
            return None
        
        page_number += 1
        time.sleep(1)

def __get_data(url, params, headers):
    response = requests.get(url, params=params, headers=headers)
    return response

from datetime import datetime
import json
import os
from urllib.parse import urlparse

def store_as_test_data(url, data):
    parsed_url = urlparse(url)
    last_path = os.path.basename(parsed_url.path).replace('.', '_')
    timestamp_str = datetime.now().strftime("%Y-%m-%d")

    filename = f"{last_path}_{timestamp_str}.json"

    with open(f'TestData/{filename}', 'a+') as f:
        f.write(json.dumps(data) + '\m')