#!/usr/bin/env python3
"""Fetch all blog posts from myfinancejournal.com and generate static HTML pages."""

import urllib.request
import re
import os
from html.parser import HTMLParser

BLOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog')
TEMPLATE_PATH = os.path.join(BLOG_DIR, 'post-template.html')

POSTS = [
    # (slug, title, date, category, url)
    ("optimizing-cash-flow", "Optimizing Cash Flow", "July 9, 2021", "Cash Flow", "https://myfinancejournal.com/optimizing-cash-flow/"),
    ("leveraging-cash-flow", "Leveraging Cash Flow", "July 20, 2021", "Cash Flow", "https://myfinancejournal.com/leveraging-cash-flow/"),
    ("factors-influencing-spending-investing", "Factors Influencing Spending & Investing", "July 9, 2021", "Cash Flow", "https://myfinancejournal.com/factors-influencing-spending-investing/"),
    ("expense-trending-budgeting", "Expense Trending & Budgeting", "July 20, 2021", "Expenses", "https://myfinancejournal.com/expense-trending-budgeting/"),
    ("factors-influencing-budget-trends", "Factors Influencing Budget Trends", "July 14, 2021", "Expenses", "https://myfinancejournal.com/factors-influencing-budget-trends/"),
    ("taxes-fees", "Taxes & Fees", "July 20, 2021", "Expenses", "https://myfinancejournal.com/taxes-fees/"),
    ("all-you-need-to-know-about-credit-score", "All You Need to Know About Credit Score", "July 20, 2021", "Savings", "https://myfinancejournal.com/all-you-need-to-know-about-credit-score/"),
    ("correlation-between-low-credit-score-and-financial-habits", "Correlation Between Low Credit Score and Financial Habits", "July 20, 2021", "Savings", "https://myfinancejournal.com/correlation-between-low-credit-score-and-financial-habits/"),
    ("maintain-minimum-balance-in-your-savings-checking-accounts", "Maintain Minimum Balance in Your Savings & Checking Accounts", "July 9, 2021", "Savings", "https://myfinancejournal.com/maintain-minimum-balance-in-your-savings-checking-accounts/"),
    ("when-not-to-take-a-line-of-credit", "When Not to Take a Line of Credit", "July 9, 2021", "Savings", "https://myfinancejournal.com/when-not-to-take-a-line-of-credit/"),
    ("save-even-more-with-balance-transfer-card-and-heloc-account", "Save Even More with Balance Transfer Card and HELOC Account", "July 9, 2021", "Savings", "https://myfinancejournal.com/save-even-more-with-balance-transfer-card-and-heloc-account/"),
    ("demystifying-investments", "Demystifying Investments", "July 9, 2021", "Investments", "https://myfinancejournal.com/demystifying-investments/"),
    ("investment-avenues", "Investment Avenues", "July 9, 2021", "Investments", "https://myfinancejournal.com/investment-avenues/"),
    ("recommended-allocation", "Recommended Allocation", "July 9, 2021", "Investments", "https://myfinancejournal.com/recommended-allocation/"),
    ("common-investor-biases", "Common Investor Biases", "July 9, 2021", "Investments", "https://myfinancejournal.com/common-investor-biases/"),
    ("introduction-to-asset-classes", "Introduction to Asset Classes", "July 20, 2021", "Investments", "https://myfinancejournal.com/introduction-to-asset-classes/"),
    ("investment-considerations", "Investment Considerations", "July 20, 2021", "Investments", "https://myfinancejournal.com/investment-considerations/"),
    ("importance-of-regular-investments", "Importance of Regular Investments", "July 20, 2021", "Investments", "https://myfinancejournal.com/importance-of-regular-investments/"),
    ("comparing-401k-and-equity-investment", "Comparing 401k and Equity Investment", "July 9, 2021", "Investments", "https://myfinancejournal.com/comparing-401k-and-equity-investment/"),
    ("special-purpose-investments", "Special Purpose Investments", "July 9, 2021", "Investments", "https://myfinancejournal.com/special-purpose-investments/"),
    ("individual-controlled-retirement-schemes", "Individual Controlled Retirement Schemes", "July 9, 2021", "Investments", "https://myfinancejournal.com/individual-controlled-retirement-schemes/"),
    ("investment-in-foreign-countries", "Investment in Foreign Countries", "July 14, 2021", "Investments", "https://myfinancejournal.com/investment-in-foreign-countries/"),
    ("debt-mortgages", "Debt & Mortgages", "July 9, 2021", "Alternate Investments", "https://myfinancejournal.com/debt-mortgages/"),
    ("mortgage-basics", "Mortgage Basics", "July 9, 2021", "Alternate Investments", "https://myfinancejournal.com/mortgage-basics/"),
    ("selecting-the-right-mortgage", "Selecting the Right Mortgage", "July 9, 2021", "Alternate Investments", "https://myfinancejournal.com/selecting-the-right-mortgage/"),
    ("should-i-refinance", "Should I Refinance?", "July 9, 2021", "Alternate Investments", "https://myfinancejournal.com/should-i-refinance/"),
    ("caveat-emptor-for-mortgage-shoppers", "Caveat Emptor for Mortgage Shoppers", "July 9, 2021", "Alternate Investments", "https://myfinancejournal.com/caveat-emptor-for-mortgage-shoppers/"),
    ("how-to-reduce-overall-mortgage-cost", "How to Reduce Overall Mortgage Cost", "July 9, 2021", "Alternate Investments", "https://myfinancejournal.com/how-to-reduce-overall-mortgage-cost/"),
    ("how-to-determine-budget-for-a-new-home", "How to Determine Budget for a New Home", "July 9, 2021", "Alternate Investments", "https://myfinancejournal.com/how-to-determine-budget-for-a-new-home/"),
    ("should-i-rent-or-buy-a-home", "Should I Rent or Buy a Home?", "July 10, 2021", "Alternate Investments", "https://myfinancejournal.com/should-i-rent-or-buy-a-home/"),
    ("impact-of-home-purchase-on-future-expenses", "Impact of Home Purchase on Future Expenses", "July 14, 2021", "Alternate Investments", "https://myfinancejournal.com/impact-of-home-purchase-on-future-expenses/"),
    ("home-as-an-investment", "Home as an Investment", "July 20, 2021", "Alternate Investments", "https://myfinancejournal.com/home-as-an-investment/"),
]


class ContentExtractor(HTMLParser):
    """Extract article content from WordPress HTML."""

    def __init__(self):
        super().__init__()
        self.in_content = False
        self.in_skip = 0
        self.tag_stack = []
        self.content_parts = []
        self.current_text = ""
        self.skip_tags = {'script', 'style', 'nav', 'header', 'footer', 'noscript', 'svg'}
        self.content_tags = {'h1','h2','h3','h4','h5','h6','p','li','blockquote',
                            'strong','em','b','i','a','ul','ol','table','tr','td','th',
                            'thead','tbody','br','sup','sub','span'}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')

        if tag in self.skip_tags:
            self.in_skip += 1
            return

        if 'entry-content' in cls:
            self.in_content = True
            return

        if self.in_content and self.in_skip <= 0:
            if tag in self.content_tags:
                href = attrs_dict.get('href', '')
                if tag == 'a' and href:
                    self.content_parts.append(f'<{tag} href="{href}">')
                elif tag == 'br':
                    self.content_parts.append('<br>')
                else:
                    self.content_parts.append(f'<{tag}>')
                self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.in_skip -= 1
            return

        if tag == 'div':
            cls_check = ''.join(str(p) for p in self.content_parts[-5:]) if len(self.content_parts) > 5 else ''
            # Don't close content prematurely

        if self.in_content and self.in_skip <= 0:
            if tag in self.content_tags and self.tag_stack and self.tag_stack[-1] == tag:
                self.content_parts.append(f'</{tag}>')
                self.tag_stack.pop()

    def handle_data(self, data):
        if self.in_content and self.in_skip <= 0:
            text = data.strip()
            if text:
                self.content_parts.append(text)


def fetch_content(url):
    """Fetch and extract article content from a URL."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='replace')

        parser = ContentExtractor()
        parser.feed(html)

        # Join and clean the content
        content = '\n'.join(parser.content_parts)

        # Clean up whitespace between tags
        content = re.sub(r'>\s+<', '>\n<', content)

        # Remove empty tags
        content = re.sub(r'<(\w+)>\s*</\1>', '', content)

        # Ensure proper paragraph wrapping for orphaned text
        lines = content.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned.append(line)

        return '\n'.join(cleaned)
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}")
        return f"<p>Article content is being updated. Please check back soon.</p>"


def generate_post(template, slug, title, date, category, url):
    """Generate a blog post HTML page."""
    print(f"  Fetching: {slug}...")
    content = fetch_content(url)

    excerpt = f"{title} - Personal finance article from My Finance Journal"

    page = template.replace('{{TITLE}}', title)
    page = page.replace('{{CATEGORY}}', category)
    page = page.replace('{{DATE}}', date)
    page = page.replace('{{EXCERPT}}', excerpt)
    page = page.replace('{{CONTENT}}', content)

    out_path = os.path.join(BLOG_DIR, f'{slug}.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page)

    content_len = len(content)
    print(f"  ✓ {slug}.html ({content_len} chars)")


def main():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    print(f"Generating {len(POSTS)} blog post pages...\n")

    for slug, title, date, category, url in POSTS:
        generate_post(template, slug, title, date, category, url)

    print(f"\nDone! Generated {len(POSTS)} blog post pages in {BLOG_DIR}/")


if __name__ == '__main__':
    main()
