"""
Apify client for web scraping.
Handles actor runs and data extraction.
"""

import logging
import time
from typing import List, Dict, Any, Optional
from apify_client import ApifyClient

from app.config import settings

logger = logging.getLogger(__name__)


class ApifyScraper:
    """Simple client for scraping websites using Apify's website content crawler."""
    
    def __init__(self):
        """Initialize Apify client."""
        if not settings.APIFY_TOKEN:
            raise ValueError("APIFY_TOKEN is required")
        
        self.client = ApifyClient(settings.APIFY_TOKEN)
        self.actor_name = settings.APIFY_ACTOR_NAME or "apify/website-content-crawler"
        logger.info(f"Initialized Apify client with actor: {self.actor_name}")
    
    def scrape_url(self, url: str, max_pages: int = 10, timeout: int = 300) -> List[Dict[str, Any]]:
        """
        Scrape a URL using Apify's website content crawler.
        
        Args:
            url: Target URL to scrape
            max_pages: Maximum number of pages to crawl (default: 10)
            timeout: Maximum time to wait for scraping to complete in seconds (default: 300)
            
        Returns:
            List of scraped documents with text content
        """
        logger.info(f"Starting Apify scrape for: {url}")
        
        try:
            # Configure the website content crawler with optimized settings from Apify
            run_input = {
                "startUrls": [{"url": url}],
                "maxCrawlPages": max_pages,
                
                # Core crawler settings - using Firefox for better compatibility
                "crawlerType": "playwright:firefox",
                "renderingTypeDetectionPercentage": 10,
                
                # Content extraction - save as markdown
                "saveMarkdown": True,
                "saveHtml": False,
                "saveHtmlAsFile": False,
                "saveFiles": False,
                "saveScreenshots": False,
                
                # Text quality settings
                "readableTextCharThreshold": 100,
                "clientSideMinChangePercentage": 15,
                
                # Cookie and popup handling
                "removeCookieWarnings": True,
                "clickElementsCssSelector": "[aria-expanded=\"false\"]",
                
                # Expand iframes to get embedded content
                "expandIframes": True,
                
                # Remove common navigation/UI elements but keep content
                "removeElementsCssSelector": "nav, footer, script, style, noscript, svg, img[src^='data:'],\n[role=\"alert\"],\n[role=\"banner\"],\n[role=\"dialog\"],\n[role=\"alertdialog\"],\n[role=\"region\"][aria-label*=\"skip\" i],\n[aria-modal=\"true\"]",
                
                # Content extraction settings
                "aggressivePrune": False,
                "blockMedia": True,
                "keepUrlFragments": False,
                "ignoreCanonicalUrl": False,
                "ignoreHttpsErrors": False,
                
                # Proxy configuration for better access
                "proxyConfiguration": {
                    "useApifyProxy": True
                },
                
                # Robots.txt and sitemap settings
                "respectRobotsTxtFile": True,
                "useSitemaps": False,
                "useLlmsTxt": False,
                
                # Debug and storage
                "debugLog": False,
                "debugMode": False,
                "storeSkippedUrls": False,
                "signHttpRequests": False,
            }
            
            logger.info(f"Starting actor run: {self.actor_name}")
            logger.info(f"Input: {run_input}")
            
            # Call the actor and wait for it to finish
            run = self.client.actor(self.actor_name).call(run_input=run_input)
            
            if not run:
                raise Exception("Actor run failed - no run object returned")
            
            logger.info(f"Actor run completed: {run.get('id')}")
            logger.info(f"Status: {run.get('status')}")
            
            # Get the results from the default dataset
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise Exception("No dataset ID in run result")
            
            logger.info(f"Fetching results from dataset: {dataset_id}")
            
            # Fetch all items from the dataset
            items = list(self.client.dataset(dataset_id).iterate_items())
            
            if not items:
                logger.warning("No items found in dataset")
                return []
            
            logger.info(f"Retrieved {len(items)} items from Apify")
            
            # Transform Apify results to our format
            documents = []
            for item in items:
                # Extract text content (Apify's website-content-crawler provides 'text' field)
                text = item.get("text", "")
                if not text or len(text.strip()) < 100:
                    # Skip items with no substantial text
                    continue
                
                doc = {
                    "url": item.get("url", url),
                    "title": item.get("metadata", {}).get("title", "") or "Untitled",
                    "text": text.strip(),
                    "crawled_at": item.get("crawl", {}).get("loadedTime", ""),
                    "metadata": {
                        "depth": item.get("crawl", {}).get("depth", 0),
                        "http_status": item.get("crawl", {}).get("httpStatusCode", 200),
                    }
                }
                documents.append(doc)
            
            logger.info(f"Processed {len(documents)} valid documents")
            return documents
            
        except Exception as e:
            logger.error(f"Apify scraping failed: {str(e)}", exc_info=True)
            raise Exception(f"Failed to scrape {url}: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test if Apify connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Get account info to verify token
            user = self.client.user().get()
            logger.info(f"Apify connection successful. User: {user.get('username')}")
            return True
        except Exception as e:
            logger.error(f"Apify connection failed: {str(e)}")
            return False

