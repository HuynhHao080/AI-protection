from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
from src.utils.logger import log_alert
import asyncio
from src.utils.notifier import notify_parent

router = APIRouter()

class URLInput(BaseModel):
    url: str

class URLAnalysisResult:
    def __init__(self):
        self.suspicious_keywords = [
            'porn', 'sex', 'adult', 'xxx', 'naked', 'nude', 'erotic',
            'casino', 'gambling', 'betting', 'lottery',
            'pharmacy', 'viagra', 'cialis', 'drugs',
            'hacking', 'cracking', 'warez', 'torrent',
            'scam', 'fraud', 'fake', 'phishing'
        ]

        self.malicious_domains = [
            'malware', 'virus', 'trojan', 'ransomware',
            'spyware', 'adware', 'botnet'
        ]

    def analyze_url_structure(self, url: str):
        """Analyze URL structure for suspicious patterns"""
        score = 0
        reasons = []

        # Check for suspicious keywords in URL
        url_lower = url.lower()
        for keyword in self.suspicious_keywords:
            if keyword in url_lower:
                score += 0.3
                reasons.append(f"Contains suspicious keyword: {keyword}")

        # Check for excessive subdomains
        parsed = urlparse(url)
        subdomains = parsed.netloc.split('.')
        if len(subdomains) > 3:
            score += 0.2
            reasons.append("Excessive subdomains")

        # Check for suspicious TLDs
        suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq']
        if any(url_lower.endswith(tld) for tld in suspicious_tlds):
            score += 0.2
            reasons.append("Suspicious top-level domain")

        # Check for IP address instead of domain
        if re.match(r'\d+\.\d+\.\d+\.\d+', parsed.netloc):
            score += 0.4
            reasons.append("Uses IP address instead of domain")

        # Check for URL shorteners
        shorteners = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly']
        if any(shortener in url_lower for shortener in shorteners):
            score += 0.1
            reasons.append("Uses URL shortener")

        return min(score, 1.0), reasons

    def analyze_content(self, url: str):
        """Analyze webpage content"""
        try:
            ua = UserAgent()
            headers = {'User-Agent': ua.random}

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text().lower()
            score = 0
            reasons = []

            # Check for adult content indicators
            adult_indicators = [
                'porn', 'sex', 'adult', 'xxx', 'naked', 'nude', 'erotic',
                'escort', 'massage', 'dating', 'hookup'
            ]

            for indicator in adult_indicators:
                if indicator in text:
                    score += 0.2
                    reasons.append(f"Adult content indicator: {indicator}")

            # Check for gambling content
            gambling_indicators = [
                'casino', 'bet', 'gambling', 'lottery', 'poker', 'blackjack'
            ]

            for indicator in gambling_indicators:
                if indicator in text:
                    score += 0.15
                    reasons.append(f"Gambling content: {indicator}")

            # Check for malware indicators
            malware_indicators = [
                'download', 'free software', 'crack', 'keygen', 'serial'
            ]

            for indicator in malware_indicators:
                if indicator in text:
                    score += 0.25
                    reasons.append(f"Potential malware: {indicator}")

            # Check for excessive external links (potential spam)
            links = soup.find_all('a', href=True)
            external_links = [link for link in links if link['href'].startswith('http')]
            if len(external_links) > 20:
                score += 0.1
                reasons.append("Excessive external links")

            return min(score, 1.0), reasons

        except Exception as e:
            return 0.0, [f"Could not analyze content: {str(e)}"]

def analyze_url_safety(url: str):
    """
    Comprehensive URL safety analysis
    """
    analyzer = URLAnalysisResult()

    # Analyze URL structure
    structure_score, structure_reasons = analyzer.analyze_url_structure(url)

    # Analyze content
    content_score, content_reasons = analyzer.analyze_content(url)

    # Combine scores
    total_score = (structure_score + content_score) / 2
    all_reasons = structure_reasons + content_reasons

    # Determine risk level
    if total_score > 0.7:
        risk_level = "high"
        label = "dangerous"
    elif total_score > 0.4:
        risk_level = "medium"
        label = "suspicious"
    else:
        risk_level = "low"
        label = "safe"

    return {
        "url": url,
        "label": label,
        "score": total_score,
        "risk_level": risk_level,
        "structure_analysis": {
            "score": structure_score,
            "reasons": structure_reasons
        },
        "content_analysis": {
            "score": content_score,
            "reasons": content_reasons
        },
        "recommendation": get_recommendation(total_score, all_reasons)
    }

def get_recommendation(score: float, reasons: list):
    """Get recommendation based on analysis"""
    if score > 0.7:
        return "BLOCKED: This URL appears to be dangerous and should not be accessed."
    elif score > 0.4:
        return "WARNING: This URL may contain inappropriate content. Parental supervision recommended."
    else:
        return "SAFE: This URL appears to be safe for access."

@router.post("/check_url")
async def check_url_api(data: URLInput):
    """
    Check URL for malicious or inappropriate content
    """
    try:
        result = analyze_url_safety(data.url)

        # Log if suspicious
        if result["score"] > 0.4:
            await log_alert("URL", data.url, result)
            notify_parent("URL", data.url, result)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")

@router.post("/check_urls_batch")
async def check_urls_batch_api(urls: dict):
    """
    Check multiple URLs for safety
    """
    url_list = urls.get("urls", [])

    if not url_list:
        raise HTTPException(status_code=400, detail="URLs list is required")

    results = []
    for url in url_list:
        try:
            result = analyze_url_safety(url)
            results.append(result)

            # Log if suspicious
            if result["score"] > 0.4:
                await log_alert("URL_BATCH", url, result)

        except Exception as e:
            results.append({
                "url": url,
                "error": str(e),
                "label": "error",
                "score": 0.0
            })

    return {"results": results}

@router.get("/url_threats")
async def get_url_threats():
    """
    Get known URL threats and patterns
    """
    return {
        "suspicious_keywords": [
            'porn', 'sex', 'adult', 'xxx', 'naked', 'nude', 'erotic',
            'casino', 'gambling', 'betting', 'lottery',
            'pharmacy', 'viagra', 'cialis', 'drugs',
            'hacking', 'cracking', 'warez', 'torrent',
            'scam', 'fraud', 'fake', 'phishing'
        ],
        "suspicious_tlds": ['.tk', '.ml', '.ga', '.cf', '.gq'],
        "url_shorteners": ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly'],
        "malicious_domains": [
            'malware', 'virus', 'trojan', 'ransomware',
            'spyware', 'adware', 'botnet'
        ]
    }
