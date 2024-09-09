import feedparser
import requests
from prettytable import PrettyTable
import re
from datetime import datetime
import argparse

def is_valid_url(url):
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

def fetch_rss_feed(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except requests.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None

def display_feed_items(feed, limit=None):
    if 'title' in feed.feed:
        print(f"Feed Title: {feed.feed.title}")
    else:
        print("Feed Title: Not available")
    
    if 'description' in feed.feed:
        print(f"Feed Description: {feed.feed.description}\n")
    else:
        print("Feed Description: Not available\n")

    if not feed.entries:
        print("No entries found in this feed.")
        return

    for i, entry in enumerate(feed.entries):
        if limit and i >= limit:
            break
        
        table = PrettyTable()
        table.field_names = ["Field", "Content"]
        table.align["Field"] = "r"
        table.align["Content"] = "l"
        table.max_width["Content"] = 60

        table.add_row(["Title", entry.get('title', 'No title')])
        table.add_row(["Description", entry.get('description', 'No description')])
        table.add_row(["Link", entry.get('link', 'No link')])
        
        # Add date information
        if 'published' in entry:
            date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            table.add_row(["Date", date.strftime("%Y-%m-%d %H:%M:%S")])

        print(table)
        print()

def main():
    parser = argparse.ArgumentParser(description="RSS Feed Reader")
    parser.add_argument("url", nargs="?", help="RSS feed URL")
    parser.add_argument("-l", "--limit", type=int, help="Limit the number of entries to display")
    args = parser.parse_args()

    url = args.url or input("Enter the RSS feed URL: ")
    if not is_valid_url(url):
        print("Invalid URL. Please enter a valid URL.")
        return

    feed = fetch_rss_feed(url)
    if not feed:
        return
    
    if feed.bozo:
        print(f"Error: {feed.bozo_exception}")
        print("Please check the URL and try again.")
    else:
        limit = args.limit
        if limit is None and not args.url:
            limit_input = input("Enter the number of entries to display (leave blank for all): ")
            limit = int(limit_input) if limit_input.isdigit() else None
        display_feed_items(feed, limit)

if __name__ == "__main__":
    main()
