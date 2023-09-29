import openai
import plotly.express as px
import requests
from bs4 import BeautifulSoup

import gandai as ts

openai.api_key = ts.secrets.access_secret_version("OPENAI_KEY")

## gpt4


def ask_gpt4(messages: list):
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=messages, temperature=0.0
    )
    return response.choices[0]["message"]["content"]


## gpt3


def ask_gpt(prompt: str, max_tokens: int = 60):
    response = openai.Completion.create(
        engine="text-davinci-003",  # or "text-curie-003" for a less expensive engine
        prompt=prompt,
        max_tokens=max_tokens,
    )

    return response.choices[0].text.strip()


def get_top_zip_codes(area: str, top_n: int = 25) -> list:
    resp = ask_gpt(
        f"As a python array List[str], the top {top_n} zip codes in {area} are:",
        max_tokens=1000,
    )
    return eval(resp)[0:top_n]  # top_n of 1 was giving me a ton of results


def get_company_summary(domain: str) -> str:
    resp = requests.get(f"http://www.{domain}")
    soup = BeautifulSoup(resp.text, "html.parser")
    homepage_text = soup.text.strip()
    PROMPT = f"""
    Summarize the products, services, and end markets of {domain}.

    Here is the homepage: {homepage_text}
    """
    resp = ask_gpt(PROMPT, max_tokens=120)
    return resp


# def get_suggested_search_phrase(search: models.Search) -> str:
#     # need up update this
#     targets = query.search_targets(search_uid=search.uid).query()
#     resp = ask_gpt(
#         f"What search phrase would you use to search Google Maps to find companies that look like this: {targets['description'].tolist()}",
#         max_tokens=60,
#     )
#     return resp


# def summarize_search_by(targets):
#     px.histogram(targets, x="employees", nbins=20, height=400, width=400).show()

#     print(targets["ownership"].value_counts())

#     GPT_PROMPT = f"""
#     The top three geographic areas, based on the {[desc for desc in targets['description'].dropna().sample(20)]} are:
#     """

#     print(ask_gpt(prompt=GPT_PROMPT))

#     GPT_PROMPT = f"""
#     Give me the company type, products and services, and end markets {[desc for desc in targets['description'].dropna().sample(20)]} are:
#     """

#     print(ask_gpt(prompt=GPT_PROMPT, max_tokens=100))
