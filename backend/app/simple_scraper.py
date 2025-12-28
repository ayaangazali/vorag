"""
Simple web scraper using requests and BeautifulSoup.
No API keys needed - completely free!
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class SimpleScraper:
    """Simple scraper using requests + BeautifulSoup."""
    
    def __init__(self):
        """Initialize scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info("Simple scraper initialized")
    
    def scrape_url(self, url: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape a URL and extract text content.
        
        Args:
            url: Target URL to scrape
            max_pages: Maximum pages to crawl (default: 10, currently only scrapes the main page)
            
        Returns:
            List of scraped documents
        """
        logger.info(f"📥 Scraping: {url}")
        
        try:
            # Fetch the page
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"✅ Fetched page (status: {response.status_code})")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
                element.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "Untitled"
            
            # Extract main content
            # Try to find main content areas first
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main', 'container'])
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to body
                body = soup.find('body')
                text = body.get_text(separator='\n', strip=True) if body else ""
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            if not cleaned_text or len(cleaned_text) < 100:
                raise ValueError(f"No substantial content found on {url}")
            
            logger.info(f"✅ Extracted {len(cleaned_text)} characters")
            
            return [{
                "url": url,
                "title": title_text,
                "text": cleaned_text,
                "crawled_at": "",
                "metadata": {
                    "depth": 0,
                    "http_status": response.status_code,
                }
            }]
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape {url}: {str(e)}")
            raise Exception(f"Failed to scrape {url}: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test if scraper is working."""
        try:
            response = self.session.get('https://httpbin.org/get', timeout=10)
            return response.status_code == 200
        except:
            return False
