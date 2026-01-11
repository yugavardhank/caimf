"""
Netlify Function: CAIMF API Proxy
Routes API requests to FastAPI backend
"""

import json
import os
from urllib.parse import urlencode
import requests

# Backend API URL (update based on deployment)
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000")


async def handler(event, context):
    """Handle API requests and route to FastAPI backend"""
    
    try:
        # Extract request details
        http_method = event["httpMethod"]
        path = event["path"].replace("/.netlify/functions/api", "")
        headers = event.get("headers", {})
        body = event.get("body", "")
        query_string = event.get("rawQueryString", "")
        
        # Build full URL
        full_url = f"{API_BASE_URL}{path}"
        if query_string:
            full_url += f"?{query_string}"
        
        # Prepare headers (remove host/origin headers)
        proxy_headers = {
            k: v for k, v in headers.items()
            if k.lower() not in ["host", "connection", "content-length"]
        }
        proxy_headers["X-Forwarded-For"] = event.get("requestContext", {}).get("identity", {}).get("sourceIp", "")
        
        # Make request to backend
        if http_method in ["GET", "HEAD"]:
            response = requests.request(http_method, full_url, headers=proxy_headers)
        else:
            response = requests.request(
                http_method,
                full_url,
                headers=proxy_headers,
                data=body
            )
        
        # Return response
        return {
            "statusCode": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "isBase64Encoded": False
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e), "message": "API proxy error"})
        }
