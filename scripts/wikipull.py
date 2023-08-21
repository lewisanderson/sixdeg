# Copyright Lewis Anderson 2023
import openai
import random
import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADER_DIV_ID = "mw-content-text"


def main():
    openai.organization = "org-RfxFQjm7zizJjdQRALbJZaZB"
    # WARNING: remove before publishing code on github
    openai.api_key = "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"

    randomUrl = "https://en.wikipedia.org/wiki/Special:Random"
    startUrl = requests.get(randomUrl).url
    endUrl = requests.get(randomUrl).url

    endDescription = fetchInfoForEnd(endUrl)

    currentUrl = startUrl
    hopTrain = [startUrl]
    maxHops = 20
    for hopCount in range(maxHops):
        if currentUrl == endUrl:
            break
        didFailGame, didMatchGoal, nextUrl = processPage(currentUrl, endUrl, endDescription)
        if didFailGame:
            return False

        print(f"idx {hopCount} -> {nextUrl}")
        currentUrl = nextUrl
        hopTrain.append(currentUrl)
        if didMatchGoal:
            break
        time.sleep(1)
    else:
        print(f"Failed to get from \n\t{startUrl} to \n\t{endUrl}. ended at \n\t{currentUrl}, with train {hopTrain}")
        return False

    printSuccess(startUrl, endUrl, hopTrain)
    return True


def fetchInfoForEnd(endUrl):
    outputText = ""
    response = requests.get(endUrl)
    soup = BeautifulSoup(response.content, 'html.parser')
    contentDiv = soup.find('div', id=HEADER_DIV_ID)
    paragraphs = contentDiv.find_all('p')
    outputText = ".  ".join([p.text for p in paragraphs[:2]])
    return outputText


def processPage(currentUrl, endUrl, endDescription):
    didFailGame = False
    didMatchGoal = False
    nextUrl = None
    # modelToUse = "gpt-3.5-turbo"
    modelToUse = "gpt-4"

    response = requests.get(currentUrl)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        didFailGame = True
        return didFailGame, didMatchGoal, nextUrl

    soup = BeautifulSoup(response.content, 'html.parser')
    contentDiv = soup.find('div', id=HEADER_DIV_ID)

    links = {}
    for link in contentDiv.find_all('a', href=True):
        theUrl = link['href']
        if not theUrl.startswith("/"):
            continue

        if (link.text in["edit", "link"] or 
            theUrl.lower().endswith(".jpg") or 
            theUrl.lower().endswith(".png") or 
            theUrl.lower().endswith(".xvg")):
            continue

        links[urljoin(currentUrl, theUrl)] = link.text
        # print(linkDescription)

    if endUrl in links:
        didMatchGoal = True
        nextUrl = endUrl
        return didFailGame, didMatchGoal, nextUrl

    urls = list(links.keys())
    maxLength = 100
    if len(urls) > maxLength:
        urls = random.sample(urls, k=maxLength)

    instructionText = f"""
We are playing the "six degrees of kevin bacon" game on wikipedia. The goal is to go from a starting page to an ending page by clicking on links. We are currently at "{currentUrl}", and trying to get to "{endUrl}". I am going to show you a list of links and ask you which one to pick. I am going to give you extra information about the links in parentheses, but that extra information should not be printed back to me.

- Give an explanation of your reasoning, then provide the url by itself in the last line of your output.
- Make sure to print the url on a line by itself. DO NOT put any additional text on the same line as the url.

Here is a description of the ending page: {endDescription}

which of the following links is most likely to take us to our goal?

""" + "\n\n"

    for i, linkUrl in enumerate(sorted(urls)):
        linkDescription = f"{linkUrl} ({links[linkUrl]})"
        instructionText += f"{linkDescription}\n"

    print(instructionText)
    result = openai.ChatCompletion.create(
        model=modelToUse,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": instructionText}
        ]
    )
    print(result)
    # nextUrlOutput = result["choices"][0]["message"]["content"]
    splits = re.split("\\n", result["choices"][0]["message"]["content"])

    splits = [a for a in splits if len(a) > 5]
    nextUrlOutput = splits[-1]
    nextUrlOutput = nextUrlOutput.removesuffix("\n")
    nextUrl = nextUrlOutput.split()[-1]
    if not nextUrl in links:
        nextUrl = nextUrlOutput.split()[0]
        if not nextUrl in links:
            print(f"Bad robot! it lied to us")
            didFailGame = True
            return didFailGame, didMatchGoal, nextUrl
    return didFailGame, didMatchGoal, nextUrl


def printSuccess(startUrl, endUrl, hopTrain):
    print(f"Success! got from {startUrl} to {endUrl}.\n\nTrain:")
    for hop in hopTrain:
        print(f"\n\t{hop}")



if __name__ == "__main__":
    for i in range(1):
        print(f"\n\n\n\n\nSTARTING round {i}")
        main()