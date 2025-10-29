from google import genai
import requests
from bs4 import BeautifulSoup
import re
import time
url = "https://www.mountainproject.com/route/105725749/the-bloodline"
route_page = BeautifulSoup(requests.get(url).text, 'html.parser')
route_desc = route_page.find('div', class_="fr-view").get_text(strip = True)

scripts = route_page.find_all('script')
for script in scripts:
    if script.string and 'loadComments' in script.string:
        match = re.search(r"var objectId = '(\d+)'", script.string)
        if match:
            object_id = match.group(1)
            print("found objectId:", object_id)

if object_id:
    comments_url = f"https://www.mountainproject.com/comments/forObject/Climb-Lib-Models-Route/{object_id}"
    print(comments_url)
    comment_ajax = BeautifulSoup(requests.get(comments_url).text, 'html.parser')
    comments = comment_ajax.find_all('div', class_='comment-body')
    comment_str = ""
    for i in range(min(50, len(comments))):
        comment_str+= comments[i].get_text(strip=True)


    client = genai.Client(api_key="AIzaSyB5NLMa6KSupMRLNPYZe0zBgHwkNtrWU_0")

    response = client.models.generate_content_stream(
        model="gemini-2.5-flash-lite",
        contents=f"Formulate a five sentence summary of a climbing route given it's description and user comments. The summary should be detailed enough to allow someone to guess the route given a list of possible routes. Leave out any super specific information about the location, name, or type of anchor of the route. The route description and comments are as follows: {route_desc} {comment_str}"
    )
    for chunk in response:
        print(chunk.text)
        # if chunk.text:
        #     print(f"\n[CHUNK]: '{chunk.text}'")
        #     print(f"[LENGTH]: {len(chunk.text)} chars")
        #     time.sleep(0.5)  # Slow it down to observe




# contents=f"Formulate a indepth summary of the following climbing route description with the intention of your summary being used to guess what the route is: \n\n{route_desc}\n\n\n\n{comment_str}\n\n Leave out any specific information about the location, name of the route, type of anchor. Minimal to no description of approach / descent.",