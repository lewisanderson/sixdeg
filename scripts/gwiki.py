
# Copyright Lewis Anderson 2023
import json
import openai
import os
import random
import requests
import time
import traceback
import wikipull
from urllib.parse import urljoin


HEADER_DIV_ID = "mw-content-text"


def main():
    openai.organization = "org-RfxFQjm7zizJjdQRALbJZaZB"
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    # modelToUse = "gpt-3.5-turbo-0613"
    modelToUse = "gpt-4-0613"

    wikiFetcher = WikiFetcher()
    instructions = """
        You are playing the "six degrees of kevin bacon" game on wikipedia. 

        You start out by selecting random start and end urls. 

        The goal is to go from the starting page to the ending page by clicking on links within each page. When you start on a page, you can fetch the links on that page, then select one of those links to click on. You can repeat this process until you reach the end page.

        If you'd like, you can fetch the first two paragraphs of text from the ending page, and use that as a hint to decide which link to click on.

        You must not fetch links for a page that you havent seen yet. You can only fetch links for the starting page or current page.

        Use the provided functions to play the game.
    """

    messages = [{"role": "user", "content": instructions}]
    maxHops = 20
    result = runConversation(messages, maxHops, modelToUse, wikiFetcher)
    return result


def runConversation(messages, maxHops, modelToUse, wikiFetcher):
    for i in range(maxHops):
        response = openai.ChatCompletion.create(
            model=modelToUse,
            messages=messages,
            functions=list(wikiFetcher.functions.values()),
            function_call="auto"
        )
        responseMessage = response["choices"][0]["message"]
        messages.append(responseMessage)
        print(f"idx {i} -> {responseMessage}")
        if not responseMessage.get("function_call"):
            print(f"No function call in response. Game has ended.")
            break
        functionName = responseMessage["function_call"]["name"]
        fuctionToCall = wikiFetcher.functions[functionName]
        functionArgs = json.loads(responseMessage["function_call"]["arguments"])
        functionResponse = wikiFetcher.callFunction(functionName, functionArgs)

        print(f"functionResponse: {functionResponse}")
        messages.append(
            {
                "role": "function",
                "name": functionName,
                "content": json.dumps(functionResponse),
            }
        )
        time.sleep(1)
    return True


class WikiFetcher:
    def __init__(self):
        self.startUrl = None
        self.endUrl = None
        self.previousLinks = set()
        self.functions = {
            "selectRandomLinks": {
                "name": "selectRandomLinks",
                "description": "Select two random wikipedia pages which form the start and end of a game.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            "fetchInfoForPage": {
                "name": "fetchInfoForPage",
                "description": "Fetch the first two paragraphs of text from a wikipedia page.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "inputUrl": {
                            "type": "string",
                            "description": "The url of the wikipedia page to fetch."
                        }
                    },
                    "required": ["inputUrl"],
                },
            },
            "fetchLinksForPage": {
                "name": "fetchLinksForPage",
                "description": "Fetch the links from a wikipedia page. This will return a tuple of (didSucceed, links, reason). If didSucceed is false, then the function did not succesfully fetch links, in which case the reason will tell you why. You can retry with a different input if you'd like. If didSucceed is true, then links will be a list of links from the page.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "inputUrl": {
                            "type": "string",
                            "description": "The url of the wikipedia page to fetch."
                        }
                    },
                    "required": ["inputUrl"],
                },
            }
        }
    
    def callFunction(self, functionName, args):
        if functionName == "selectRandomLinks":
            return self.selectRandomLinks()
        elif functionName == "fetchInfoForPage":
            return self.fetchInfoForPage(args["inputUrl"])
        elif functionName == "fetchLinksForPage":
            return self.fetchLinksForPage(args["inputUrl"])

    def selectRandomLinks(self) -> (str, str):
        randomUrl = "https://en.wikipedia.org/wiki/Special:Random"
        
        self.startUrl = requests.get(randomUrl).url
        self.endUrl = requests.get(randomUrl).url

        return self.startUrl, self.endUrl

    def fetchInfoForPage(self, inputUrl: str) -> str:
        if inputUrl != self.endUrl:
            print(f"WARNING: fetching page other than endUrl. fetching {inputUrl}, not {self.endUrl}")
        
        return wikipull.fetchInfoForPage(inputUrl)

    def fetchLinksForPage(self, inputUrl: str) -> (bool, list, str):
        if inputUrl not in self.previousLinks and inputUrl != self.startUrl:
            errorMessage = f"ERROR: fetching links for page {inputUrl} not in {self.previousLinks}, {self.startUrl}"
            print(errorMessage)
            return False, [], errorMessage
        
        didSucceed, links, reason = wikipull.fetchLinksForPage(inputUrl)
        if didSucceed:
            maxLength = 50
            if len(links) > maxLength:
                sampledKeys = random.sample(list(links.keys()), k=maxLength)
                links = {key: links[key] for key in sampledKeys}
            
            self.previousLinks = set(links.keys())
        return didSucceed, links, reason


if __name__ == "__main__":
    numRounds = 1
    for i in range(numRounds):
        try:
            print(f"\n\n\n\n\nSTARTING round {i}")
            main()
        except Exception as e:
            print(f"Failed round {i}. {e}\n{traceback.format_exc()}")
            time.sleep(1)
            continue
