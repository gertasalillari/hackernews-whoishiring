# Hacker News “*Who is hiring*”

This project scrapes the job postings from [Hacker News “Who is hiring”](https://news.ycombinator.com/submitted?id=whoishiring), extracts and enriches relevant features from Hacker News comments, focusing on identifying early-stage companies, extracts their locations (Europe/ USA/ Other), as well as the company name and the company URL.

1. Scraping Hacker News Comments:

    - Retrieves past comments (last 2 years) using [ScraperAPI](https://www.scraperapi.com).
    - Stores them as a JSON Lines file for further processing.

2. Feature Selection

- **Company name**: for company identification. \
A combined approach of string matching, model analysis (spaCy & Flair), and reconciliation for high accuracy. This includes filtering out potentially incorrect names based on length and token count (e.g., excluding names longer than 20 characters or with more than 4 tokens).
- **Region/location**: key indicator for specific landscape focus.\
Identification of company locations using NER models and classifies them as "Europe", "USA", "Other" or "Unknown" matching them against [geonames data](https://public.opendatasoft.com/explore/dataset/geonames-all-cities-with-a-population-1000/). Only cities with a population exceeding 120,000 are considered for this analysis.
- **Company URL**: associates extracted companies with their respective URLs.\
Further analysis would likely involve enriching the data by directly scraping company websites or using other data enrichment platforms.


Regular expressions and basic text analysis have been prioritised for quick identification of key entities.
Once key features have been identified, more complex models like [spaCy](https://spacy.io/models/en#en_core_web_trf) and [Flair](https://flairnlp.github.io/) have been used to further increase the accuracy and the depth of the analysis.

In terms of packaging, although the project is very simple, Docker ensures consistent environments.

> [!NOTE]
> Optional Enrichment with [Apollo.io](https://www.apollo.io/) (Demo):\
This additional step, uses the apollo.io API to enrich the data with more comprehensive information about identified companies.
A limited demonstration script `apollo_example.py` retrieves additional fields like website URLs, social media links, founding year, funding details, and more, showcased in `data/outputs/apollo_example.csv`.

## Getting Started

### Dependencies:

- Docker and Docker Compose
- ScraperAPI key
- Apollo.io API key
> [!NOTE]
> Apollo offers free limited credits.


### Setup
1. Copy the sample environment file. SCRAPERAPI_KEY is necessary for the scraping part, which I can provide if necessary.
```
cp sample.env .env
```

2. Build image and up the server:
```bash
docker-compose up --build
```

3. Run the scripts with Python:
HAcker News posts scraping:
```bash
docker-compose exec app python scraper/app/hacker_news_scraping.py
```
Outputs a JSON Lines file containing the scraped comments of Hacker News “Who is hiring” posts.\
`scraper/data/hacker_news_comments.jsonl`

The second part of the project is a Jupyter Notebook which can be run from localhost:
`scraper/app/feature_extraction.ipynb`

Outputs a CSV file with the initial posts' data, and additional features, including:
- year of the post
- month of the post
- post headline
- post body
- company name
- region
- company url.

`scraper/data/outputs/output.csv`

## Next steps

Further features can be extracted from the job posts:
- Job titles can be extracted from the text with the [find-job-titles package](https://pypi.org/project/find-job-titles/).
- Employee count trend
- Frequency and trends of job posts per company. This analysis could be expanded if the data were enriched from other sources to keep into account the employee counts ect.
- Technologies used by the company: found technologies could be compared and matched against emerging trends in tech (eg LLMs) flagging companies with high growth potential, or that are developing innovative solutions in traditional markets.
- Funding Stage: this information is not always mentioned in the HN job posts, but easily accessible from other sources.
- Funding information (Apollo, Pitchbook...)
