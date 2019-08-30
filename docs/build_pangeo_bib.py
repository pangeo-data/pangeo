import pandas as pd
import requests
from time import sleep

fname = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQDdsyiuh00D7PGFQ5HHUjtYIqhSnBt96vltbuMJUbkNRch6Nm6fhJjYwvUn9auOzr8-obG3owlyBUU/pub?gid=1350682285&single=true&output=csv'

df = pd.read_csv(fname)
split_dois = df.DOI.str.split(pat='[,|\s]+')
all_dois = pd.Series([i for items in split_dois.values for i in items])
clean_dois = all_dois.str.replace('http://|https://', '').str.replace('dx.doi.org/|doi.org/', '').unique()

headers = {'User-Agent':
           'pangeo-bib-bot (https://pangeo.io; mailto:rpa@ldeo.columbia.edu)'}

def get_with_retries(url, ntries=5):
    for n in range(ntries):
        try:
            sleep(0.2)
            r = requests.request('GET', api_url, headers=headers)
            r.raise_for_status()
            return r.text
        except requests.exceptions.HTTPError:
            pass


with open('pangeo_publications.bib', mode='w') as f:
    for doi in clean_dois:
        api_url = f'http://api.crossref.org/works/{doi}/transform/application/x-bibtex'
        text = get_with_retries(api_url)
        if text:
            print(text, file=f)
