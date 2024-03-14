""" hacker_news_scraping.py
"""
import json
import os
import re
from datetime import datetime, timedelta
from time import sleep

import requests
import urllib3
from bs4 import BeautifulSoup, NavigableString, Tag
from tqdm import tqdm

from logs.logger_config import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extract_year_month(title):
    match = re.search(r"\((\w+)\s(\d{4})\)", title)
    if match:
        month = match.group(1)
        year = match.group(2)
        return year, month
    else:
        return None, None


def get_proxies():
    SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")
    return {
        "http": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
        "https": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
    }


def is_within_last_n_years(n_years_ago, year, month):
    """Check if the given year and month are within the last two years from the current date."""
    post_date = datetime.strptime(f"{year} {month}", "%Y %B")
    n_years_ago = datetime.now() - timedelta(days=365 * n_years_ago)
    return post_date >= n_years_ago


def extract_headline_and_body(comment_span):
    elements = [element for element in comment_span.children if not hasattr(element, "name") or element.name != "div"]

    headline_elements = []
    body_elements = []
    found_p_tag = False

    for element in elements:
        if isinstance(element, Tag) and element.name == "p":
            found_p_tag = True

        if not found_p_tag:
            if isinstance(element, NavigableString) or (isinstance(element, Tag) and element.name == "a"):
                # Append text of the element, removing HTML tags for anchor elements
                headline_elements.append(element.get_text() if isinstance(element, Tag) else str(element))
        else:
            # Append the text of body elements, stripping away all HTML tags
            body_elements.append(element.get_text() if isinstance(element, Tag) else str(element))

    # Join the elements to form the headline and body text
    headline = " ".join(headline_elements).strip()
    body = " ".join(body_elements).strip()

    return headline, body


YEARS2SCRAPE = 2


def get_post_comments(post_url, proxies, max_retries=3):
    post_comments = []
    seen_comments = set()

    page_num = 1
    comments_exist = True

    while comments_exist:
        attempts = 0
        success = False
        current_page = f"{post_url}&p={page_num}"

        while attempts < max_retries and not success:
            try:
                logger.info(f"Fetching comments from page {page_num}, attempt {attempts + 1}")
                post_response = requests.get(current_page, proxies=proxies, verify=False, timeout=10)
                if post_response.status_code == 200:
                    post_soup = BeautifulSoup(post_response.text, "html.parser")
                    title_tag = post_soup.find("title")
                    if title_tag:
                        post_title = title_tag.text
                        year, month = extract_year_month(post_title)
                        if not is_within_last_n_years(YEARS2SCRAPE, year, month):
                            comments_exist = False
                            break
                        success = True  # Proceed to process comments
                    else:
                        logger.warning("No title tag found. Breaking out of retry loop.")
                        break  # Break out of the inner loop but try next page
                else:
                    logger.warning(f"Failed to fetch page: HTTP status code {post_response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Request failed: {e}")

            attempts += 1
            if not success:
                sleep_time = 15**attempts
                logger.info(f"Retrying after {sleep_time} seconds...")
                sleep(sleep_time)

        if success:
            comments = post_soup.find_all("tr", class_="comtr")
            logger.info(f"Found {len(comments)} comments on page {page_num}.")
            new_comments_found = False

            for comment in comments:
                indent_element = comment.find("td", class_="ind")
                indent = indent_element["indent"] if indent_element else None
                if indent == "0":
                    comment_span = comment.find("span", class_="commtext")
                    if comment_span:
                        headline, body = extract_headline_and_body(comment_span)
                        comment_hash = hash(year + month + headline + body)
                        if comment_hash not in seen_comments:
                            new_comments_found = True
                            seen_comments.add(comment_hash)
                            comment_info = {
                                "year": year,
                                "month": month,
                                "headline": headline.replace("\n", "\n\n"),
                                "body": body.replace("\n", "\n\n"),
                                "hash": comment_hash,
                            }
                            post_comments.append(comment_info)

            if not new_comments_found:
                logger.info("No new comments found on this page. Stopping pagination.")
                break

            page_num += 1
            sleep(32)  # Respectful delay between page fetches

        else:
            comments_exist = False  # No more comments to process or failed to fetch

    return post_comments


def scrape_and_save_comments():
    logger.info("Logger initialised.")

    base_url = "https://news.ycombinator.com/"
    user_submissions_url = f"{base_url}submitted?id=whoishiring"
    proxies = get_proxies()
    DATA_DIR = os.getenv("DATA_DIR", ".")
    filename = os.path.join(DATA_DIR, "hacker_news_comments.jsonl")

    while user_submissions_url:
        response = requests.get(user_submissions_url, proxies=proxies, verify=False)
        main_page_soup = BeautifulSoup(response.text, "html.parser")

        # Find all posts on the current page
        posts = main_page_soup.find_all("a", string=lambda text: "Ask HN: Who is hiring?" in str(text))

        with open(filename, "a", encoding="utf-8") as f:
            for post in tqdm(posts, desc="Processing job posts"):
                # Navigate to each post's comments page
                post_url = base_url + post["href"]
                logger.info(f"Post url:\t{post_url}")

                comments = get_post_comments(post_url, proxies)
                for comment_info in comments:
                    f.write(json.dumps(comment_info, ensure_ascii=False) + "\n")

        # Find the 'More' link to navigate to the next page
        more_link = main_page_soup.find("a", string="More")
        if more_link:
            user_submissions_url = base_url + more_link["href"]
        else:
            user_submissions_url = None

    print(f"\t💾 Saved comments to {filename}.")


if __name__ == "__main__":
    scrape_and_save_comments()
