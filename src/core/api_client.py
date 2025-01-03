<<<<<<< ours
import aiohttp
import os
from dotenv import load_dotenv

class APIClient:
    def __init__(self, is_test_mode=False):
        self.is_test_mode = is_test_mode
        load_dotenv()  # Load environment variables
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"

    def set_api_key(self, api_key=None):
        ###"""Override API key if provided, otherwise use from .env###"""
        if api_key:
            self.api_key = api_key

    async def search(self, query, max_results=10):
        ###"""Perform an OpenAI API call###"""
        if self.is_test_mode:
            return {
                "results": [
                    {"id": 1, "title": "Test Result 1", "content": "This is a test result"},
                    {"id": 2, "title": "Test Result 2", "content": "This is another test result"}
                ],
                "total": 2,
                "query": query
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Using GPT-3.5-turbo for the API call
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "results": [{
                            "id": 1,
                            "content": result['choices'][0]['message']['content'],
                            "model": result['model']
                        }],
                        "total": 1,
                        "query": query
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}: {error_text}")


||||||| base
=======
import aiohttp
import os
from dotenv import load_dotenv

class APIClient:
    def __init__(self, is_test_mode=False):
        self.is_test_mode = is_test_mode
        load_dotenv()  # Load environment variables
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = "https://api.openai.com/v1"

    def set_api_key(self, api_key=None):
        """Override API key if provided, otherwise use from .env"""
        if api_key:
            self.api_key = api_key

    async def search(self, query, max_results=10):
        """Perform an OpenAI API call"""
        if self.is_test_mode:
            return {
                "results": [
                    {"id": 1, "title": "Test Result 1", "content": "This is a test result"},
                    {"id": 2, "title": "Test Result 2", "content": "This is another test result"}
                ],
                "total": 2,
                "query": query
            }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Using GPT-3.5-turbo for the API call
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "results": [{
                            "id": 1,
                            "content": result['choices'][0]['message']['content'],
                            "model": result['model']
                        }],
                        "total": 1,
                        "query": query
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"API call failed with status {response.status}: {error_text}")
>>>>>>> theirs
