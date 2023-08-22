# Copyright Lewis Anderson 2023

import gwiki
import unittest
import wikipull
from unittest.mock import patch, Mock


class GWikiTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("gwiki.wikipull.fetchInfoForPage")
    @patch("gwiki.wikipull.processPage")
    @patch("gwiki.wikipull.time.sleep")
    @patch('gwiki.openai.ChatCompletion.create')
    def test_main(self, createMock, sleepMock, processPageMock, fetchInfoForPageMock):
        startUrl = "https://en.wikipedia.org/wiki/Nicolas_Buendia" 
        endUrl = "https://en.wikipedia.org/wiki/Ashleworth_Ham"
        fetchInfoForPageMock.return_value = "some stuff about nicolas"
        processPageMock.return_value = (False, True, endUrl)

        createMock.return_value = {
            "id": "chatcmpl-7p3PAcrx2xS9e7vpucN7IQJXAQCyB",
            "object": "chat.completion",
            "created": 1692402172,
            "model": "gpt-4-0613",
            "choices": [
                {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I dont want to play the game anymore."
                },
                "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 2280,
                "completion_tokens": 118,
                "total_tokens": 2398
            }
        }
        self.assertTrue(gwiki.main())

        createMock.return_value = {
            "id": "chatcmpl-7p3PAcrx2xS9e7vpucN7IQJXAQCyB",
            "object": "chat.completion",
            "created": 1692402172,
            "model": "gpt-4-0613",
            "choices": [
                {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    'function_call': {'name': 'fetchInfoForPage',
                    'arguments': '{\n  "inputUrl": "https://en.wikipedia.org/wiki/Nicolas_Buendia"}'}
                },
                "finish_reason": "function_call"
                }
            ],
            "usage": {
                "prompt_tokens": 2280,
                "completion_tokens": 118,
                "total_tokens": 2398
            }
        }
        self.assertTrue(gwiki.main())
        



if __name__ == "__main__":
    unittest.main()
