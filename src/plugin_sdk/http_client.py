from typing import Any, Dict

import httpx
from fastapi import HTTPException


class AsyncHttpClient:
    """Async HTTP client wrapper using httpx"""

    @staticmethod
    async def request(
        method: str,
        url: str,
        headers: Dict[str, str] = {},
        params: Dict[str, Any] = {},
        json: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """Make an async HTTP request"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    params=params or {},
                    json=json or {},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"API Error: {e.response.text}",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
