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
    @patch("gwiki.openai.ChatCompletion.create")
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

        fetchInfoForPageMock.return_value = "some stuff about nicolas"*50
        self.assertTrue(gwiki.main())
    
    @patch("gwiki.wikipull.fetchLinksForPage")
    def test_fetchLinksForPage(self, fetchLinksForPageMock):
        startUrl = "https://en.wikipedia.org/wiki/Nicolas_Buendia"
        fetchLinksForPageMock.return_value = (True, {"https://en.wikipedia.org/wiki/2020": "2020", "https://en.wikipedia.org/wiki/2021": "2021"}, None)
        fetcher = gwiki.WikiFetcher()
        fetcher.startUrl = startUrl
        didGetLinks, links, reason = fetcher.fetchLinksForPage(startUrl)
        self.assertTrue(didGetLinks)
        self.assertEqual(len(links), 2)

        fullLinks = {f"https://en.wikipedia.org/wiki/{idx}": idx for idx in range(150)}
        fetchLinksForPageMock.return_value = (True, fullLinks, None)
        didGetLinks, links, reason = fetcher.fetchLinksForPage(startUrl)
        self.assertTrue(didGetLinks)
        self.assertLessEqual(len(links), 101)



if __name__ == "__main__":
    unittest.main()
