from tqdm import tqdm
import requests

def execute_remote_code(remote_code_url, headers=None):
    headers = headers or {}

    response = requests.get(remote_code_url, headers=headers, stream=True)

    if response.status_code == 200:
        # Retrieve the remote code length in bytes and create a tqdm progress bar
        content_length = response.headers.get('Content-Length')
        if content_length is not None:
            total_size = int(content_length.strip())
            progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f'Remote Code ({remote_code_url})')

        remote_code = ''
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                remote_code += chunk.decode('utf-8')
                if content_length is not None:
                    progress_bar.update(len(chunk))

        # End the progress bar and execute the remote code
        if content_length is not None:
            progress_bar.close()
        try:
            compiled_code = compile(remote_code, '<string>', 'exec')
            exec(compiled_code)
        except Exception as e:
            print(f"Error executing remote code: {e}")
    elif response.status_code == 401:
        print(f"Unauthorized for {remote_code_url}. Please provide a valid authentication token.")
    elif response.status_code == 403:
        print(f"Forbidden for {remote_code_url}. You do not have permission to access this resource.")
    elif response.status_code == 404:
        print(f"Not found for {remote_code_url}. The requested resource could not be found.")
    else:
        print(f"Failed to fetch remote code for {remote_code_url}. Status code: {response.status_code}")