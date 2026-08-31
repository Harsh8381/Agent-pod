import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import COFORGE_API_KEY, COFORGE_API_URL, COFORGE_MODEL


def call_llm(prompt, system_prompt=None, temperature=0.3):
    """
    Call Coforge LLM Router API.
    """

    if not COFORGE_API_KEY:
        raise ValueError("COFORGE_API_KEY not found in .env file.")

    if not COFORGE_API_URL:
        raise ValueError("COFORGE_API_URL not found in .env file.")

    clean_api_url = COFORGE_API_URL.strip().replace('"', '').replace("%22", "")
    clean_api_key = COFORGE_API_KEY.strip()

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": clean_api_key
    }

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    body = {
        "model": COFORGE_MODEL,
        "messages": messages,
        "temperature": temperature
    }

    retry_policy = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods=["POST"],
        raise_on_status=False,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_policy))
    session.mount("http://", HTTPAdapter(max_retries=retry_policy))

    try:
        response = session.post(
            clean_api_url,
            headers=headers,
            json=body,
            timeout=(15, 120),
        )
    except requests.exceptions.RequestException as error:
        raise ConnectionError(
            "Unable to connect to the configured Coforge LLM service after retries."
        ) from error

    if response.status_code != 200:
        raise RuntimeError(
            f"Coforge API error: {response.status_code} - {response.text}"
        )

    data = response.json()

    return data["choices"][0]["message"]["content"]
