import pandas as pd
import requests

fname = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQDdsyiuh00D7PGFQ5HHUjtYIqhSnBt96vltbuMJUbkNRch6Nm6fhJjYwvUn9auOzr8-obG3owlyBUU/pub?gid=1350682285&single=true&output=csv'

df = pd.read_csv(fname)
split_dois = df.DOI.str.split(pat='[,|\s]+')
all_dois = pd.Series([i for items in split_dois.values for i in items])
clean_dois = all_dois.str.replace('http://|https://', '').str.replace('dx.doi.org/|doi.org/', '').unique()

with open('pangeo_publications.bib', mode='w') as f:
    for doi in clean_dois:
        api_url = f'http://api.crossref.org/works/{doi}/transform/application/x-bibtex'
        r = requests.request('GET', api_url)
        r.raise_for_status()
        print(r.text, file=f)