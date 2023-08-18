# Copyright Lewis Anderson 2023

import unittest
import wikipull
from unittest.mock import patch, Mock


class WikiPullTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_printSuccess(self):
        startUrl = "https://en.wikipedia.org/wiki/Nicolas_Buendia" 
        endUrl = "https://en.wikipedia.org/wiki/Ashleworth_Ham"
        hopTrain = [startUrl, "https://en.wikipedia.org/wiki/2020", "https://en.wikipedia.org/wiki/2021"]
        wikipull.printSuccess(startUrl, endUrl, hopTrain)

    @patch("wikipull.requests.get")
    def test_fetchInfoForEnd(self, getMock):
        endUrl = "https://en.wikipedia.org/wiki/2020"

        with open("testdata/wiki2020.html", "r") as f:
            wiki2020Html = f.read()
        getMock.return_value = Mock(
            url = endUrl,
            status_code = 200,
            content = wiki2020Html
        )
        endDescription = wikipull.fetchInfoForEnd(endUrl)
        self.assertTrue(len(endDescription) > 0)

    @patch('wikipull.openai.ChatCompletion.create')
    @patch("wikipull.requests.get")
    def test_processPage(self, getMock, createMock):

        with open("testdata/wiki2020.html", "r") as f:
            wiki2020Html = f.read()
        currentUrl = "https://en.wikipedia.org/wiki/2020"
        getMock.return_value = Mock(
            url = currentUrl,
            status_code = 200,
            content = wiki2020Html
        )
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
                    "content": "To navigate from Halifax Regional Council to Debaies Cove in Nova Scotia, a link with a strong relation to the Nova Scotia region, especially Halifax, could be useful. The link to \"Nova Scotia Federation of Municipalities\" should be relevant and may, via related topics and internal links, bring us closer to our destination of Debaies Cove, since it likely contains more specific information about various parts of the region, including rural communities.\n\nhttps://en.wikipedia.org/wiki/Nova_Scotia_Federation_of_Municipalities"
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
        endUrl = "https://en.wikipedia.org/wiki/Nicolas_Buendia"
        endDescription = "some stuff about nicolas"
        didFailGame, didMatchGoal, nextUrl = wikipull.processPage(currentUrl, endUrl, endDescription)
        self.assertFalse(didFailGame)
        self.assertFalse(didMatchGoal)
        self.assertEqual(nextUrl, "https://en.wikipedia.org/wiki/Nova_Scotia_Federation_of_Municipalities")


if __name__ == "__main__":
    unittest.main()
