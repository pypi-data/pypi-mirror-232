import tiktoken
import openai
import requests
import arxiv
import urllib.request
from bs4 import BeautifulSoup
from termcolor import colored

def generate_literature_review(research_question, openai_key, length="short"):

    # Configure OpenAI
    openai.api_key = openai_key

    def get_citation_by_doi(doi):
        url = f"https://api.citeas.org/product/{doi}"
        response = requests.get(url)
        try:
            data = response.json()
            return data["citations"][0]["citation"]
        except ValueError:
            return response.text
        
    def fetch_and_sort_springer(query,answersCount,papersCount):
        answers = []
        API_key = "32af82cd661706262763f7d4941b0969"
        url = "http://api.springernature.com/"
        endpoint = "metadata/json"
        params = {
            "q": query,
            "api_key": API_key,
            "hl": "en"
        }

        response = requests.get(url + endpoint, params=params)

        if response.status_code == 200:
            data = response.json()

        for record in data["records"]:
                title = record.get("title")
                print(colored(f"Title: "+title, "yellow"))
                doi = record.get("identifier")
                doi = doi.replace('doi:','')
                citation = get_citation_by_doi(doi)
                citation = citation .replace('\n\n', '\n').strip()
                abstract = record.get("abstract")
                answer_with_citation = f"{abstract} \n SOURCE: {citation}"
                answers.append(answer_with_citation)
                print(colored(f"Answer found!", "green"))
                print(colored(f"{answer_with_citation}", "cyan"))
                answersCount+=1
                if answersCount >= papersCount:  #fetch certain numbers of papers only
                    break
        
        return answers
        
    def fetch_and_sort_papers(query,answersCount,papersCount):
        answers = []
        search = arxiv.Search(
        query = query,
        max_results = papersCount,
        sort_by = arxiv.SortCriterion.Relevance,
        sort_order = arxiv.SortOrder.Descending
        )
        arxiv_papers = list(search.results())
        
        for result in arxiv_papers:
            title = result.title
            print(colored(f"Title: "+title, "yellow"))
            abstract = result.summary
            url = result.pdf_url
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            req = urllib.request.Request(url, headers=headers)
            try:
                html = urllib.request.urlopen(req).read()
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    doi_link = soup.find("a", href=lambda href: href and "doi.org" in href)
                    if doi_link:
                        doi = doi_link.get("href")
                        doi_identifier = doi.replace("https://doi.org/", "")
                        citation = get_citation_by_doi(doi_identifier)
                    else:
                        citation = url
                        print("DOI link not found.")
                    
                    answer_with_citation = f"{abstract} \n SOURCE: {citation}"
                    print(colored(f"Answer found!", "green"))
                    print(colored(f"{answer_with_citation}", "cyan"))
                    answers.append(answer_with_citation)
                    answersCount+=1
                    if answersCount >= papersCount:  #fetch certain numbers of papers only
                        break
                except:
                    pass
            except urllib.error.HTTPError:
                pass
            except urllib.error.URLError:
                pass
        return answers
        
    def count_tokens(text):
        # encoding = tiktoken.get_encoding("cl100k_base")
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

        tokens = encoding.encode(text)
        return len(tokens)

    # Extract bibliographical citations from answers
    def extract_citations(answers):
        citations = []
        for answer in answers:
            citation_start = answer.rfind("SOURCE: ")
            if citation_start != -1:
                citation = answer[citation_start + len("SOURCE: ") :]
                citations.append(citation)
        return citations

    literature_review_prompt =  """"
    Using the provided research findings, synthesize a strictly concise literature review of almost {words_count} words addressing the research question "{research_question}". Incorporate appropriate APA in-text citations for each finding.

    Research Findings:

    {answer_list}
    """

    def openai_call(
        prompt: str, temperature: float = 0.5, max_tokens: int = 100,
    ):
        messages = [{"role": "user", "content": prompt}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return response.choices[0].message.content.strip()
    # Combine answers into a concise literature review using OpenAI API
    def combine_answers(answers, research_question, wordsCount, temperature=0.1):
        answer_list = "\n\n".join(answers)
        prompt = literature_review_prompt.format(
            words_count=wordsCount, research_question=research_question, answer_list=answer_list
        )

        # Calculate the tokens in the input
        input_tokens = count_tokens(prompt)

        # Calculate the remaining tokens for the response
        remaining_tokens = 4080 - input_tokens
        max_tokens = max(remaining_tokens, 0)

        literature_review = openai_call(
            prompt, temperature=temperature, max_tokens=max_tokens
        )

        return literature_review
    
    papersCount = 5
    wordsCount = 200
    if length == "long":
        papersCount = 10
        wordsCount = 400
    print(colored(f"Research question: {research_question}", "yellow", attrs=["bold", "blink"]))
    print(colored("Auto Researcher initiated!", "yellow"))

    print(colored("Fetching Springer research papers...", "yellow"))
    answers =fetch_and_sort_springer(research_question,0, papersCount)
    print(colored("Research findings extracted!", "green"))

    answersSize =len(answers)
    if answersSize < papersCount:
        print(colored("Fetching Arxiv research papers...", "yellow"))
        #feching papers from arxiv
        answers_1 = fetch_and_sort_papers(research_question,len(answers),papersCount)
        answers.extend(answers_1)

    # Combine answers into a concise academic literature review
    print(colored("Synthesizing answers...", "yellow"))
    literature_review = combine_answers(answers, research_question, wordsCount)
    print(colored("Literature review generated!", "green"))

    # Extract citations from answers and append a references list to the literature review
    citations = extract_citations(answers)
    references_list = "\n".join([f"{idx + 1}. {citation}" for idx, citation in enumerate(citations)])
    literature_review += "References:" + references_list
    
    print(colored("Literature review generated using "+str(len(answers))+" papers.", "yellow"),"\n")
    # Print the academic literature review
    print(colored("Academic Literature Review:", "cyan"), "Literature review generated using "+str(len(answers))+" papers.\n"+literature_review, "\n")

    return literature_review