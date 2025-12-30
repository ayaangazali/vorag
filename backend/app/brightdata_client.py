"""
Bright Data client for web scraping.
Uses Bright Data's Data Collector API for better JavaScript rendering.
"""

import logging
import time
import requests
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class BrightDataScraper:
    """Client for scraping websites using Bright Data's Data Collector API."""
    
    def __init__(self):
        """Initialize Bright Data client."""
        if not settings.BRIGHTDATA_API_TOKEN:
            raise ValueError("BRIGHTDATA_API_TOKEN is required")
        
        self.api_token = settings.BRIGHTDATA_API_TOKEN
        self.collector_id = settings.BRIGHTDATA_COLLECTOR_ID or "c_mjsgl9011x823pu93h"
        self.base_url = "https://api.brightdata.com/dca"
        
        logger.info(f"Initialized Bright Data client with collector: {self.collector_id}")
    
    def scrape_url(self, url: str, timeout: int = 300) -> List[Dict[str, Any]]:
        """
        Scrape a URL using Bright Data's Data Collector API.
        
        Args:
            url: Target URL to scrape
            timeout: Maximum time to wait for scraping to complete in seconds (default: 300)
            
        Returns:
            List of scraped documents with text content
        """
        logger.info(f"Starting Bright Data scrape for: {url}")
        
        try:
            # Trigger the data collection
            trigger_url = f"{self.base_url}/trigger"
            params = {
                "collector": self.collector_id,
                "queue_next": "1"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = [{"url": url}]
            
            logger.info(f"Triggering Bright Data collector: {self.collector_id}")
            logger.info(f"URL: {url}")
            
            # Trigger the collection
            response = requests.post(
                trigger_url,
                params=params,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            trigger_result = response.json()
            
            logger.info(f"Collection triggered: {trigger_result}")
            
            # Get the snapshot ID or collection ID from response
            # Bright Data returns different response formats depending on collector setup
            if isinstance(trigger_result, dict):
                snapshot_id = trigger_result.get("snapshot_id") or trigger_result.get("response_id")
            elif isinstance(trigger_result, list) and len(trigger_result) > 0:
                snapshot_id = trigger_result[0].get("snapshot_id") or trigger_result[0].get("response_id")
            else:
                snapshot_id = None
            
            if not snapshot_id:
                logger.warning("No snapshot_id returned, waiting before fetching results...")
                time.sleep(10)  # Give it time to process
            
            # Wait for collection to complete and fetch results
            max_attempts = timeout // 5
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                logger.info(f"Attempt {attempt}/{max_attempts}: Fetching results...")
                
                # Fetch the collected data
                fetch_url = f"{self.base_url}/dataset"
                params = {
                    "collector": self.collector_id,
                    "format": "json"
                }
                
                fetch_response = requests.get(
                    fetch_url,
                    params=params,
                    headers={"Authorization": f"Bearer {self.api_token}"},
                    timeout=30
                )
                
                if fetch_response.status_code == 200:
                    results = fetch_response.json()
                    
                    if results and len(results) > 0:
                        logger.info(f"Retrieved {len(results)} items from Bright Data")
                        
                        # Convert to documents format
                        documents = []
                        for item in results:
                            # Extract text content from various possible fields
                            text = None
                            
                            # Try different common field names
                            for field in ["text", "content", "body", "html", "description", "text_content"]:
                                if field in item and item[field]:
                                    text = item[field]
                                    break
                            
                            # If still no text, try to extract from all string fields
                            if not text:
                                text_parts = []
                                for key, value in item.items():
                                    if isinstance(value, str) and len(value) > 50 and key not in ["url", "id"]:
                                        text_parts.append(value)
                                text = "\n\n".join(text_parts) if text_parts else None
                            
                            if text:
                                doc = {
                                    "text": text,
                                    "url": item.get("url", url),
                                    "title": item.get("title", "Scraped Content"),
                                    "metadata": {
                                        "source": "brightdata",
                                        **{k: v for k, v in item.items() if k not in ["text", "content", "body", "html"]}
                                    }
                                }
                                documents.append(doc)
                        
                        if documents:
                            logger.info(f"Successfully extracted {len(documents)} documents")
                            return documents
                        else:
                            logger.warning("No text content found in results")
                
                # Wait before next attempt
                if attempt < max_attempts:
                    wait_time = min(5 * attempt, 30)  # Exponential backoff, max 30s
                    logger.info(f"Waiting {wait_time}s before next attempt...")
                    time.sleep(wait_time)
            
            logger.error(f"Failed to retrieve results after {max_attempts} attempts")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bright Data request error: {str(e)}")
            raise Exception(f"Failed to scrape with Bright Data: {str(e)}")
        except Exception as e:
            logger.error(f"Bright Data scraping error: {str(e)}", exc_info=True)
            raise
