
import requests

API_URL = "http://127.0.0.1:8000/simplify"


def simplify_text(text, level="simpler", timeout=60):

    payload = {
        "text": text,
        "user_action": True,
        "level": level
    }

    response = None

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=timeout
        )

        response.raise_for_status()

        result = response.json()

        if isinstance(result, str):
            simplified_text = result

        elif isinstance(result, dict):
            simplified_text = (
                result.get("simplified_text")
                or result.get("result")
                or result.get("text")
            )
        else:
            simplified_text = None

        if not isinstance(simplified_text, str):
            raise ValueError(
                f"Unexpected API response: {result}"
            )

        simplified_text = simplified_text.strip()

        if not simplified_text:
            raise ValueError("API returned empty text")

        return {
            "success": True,
            "generated_text": simplified_text,
            "simplified_text": simplified_text,
            "status_code": response.status_code,
            "error": None
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "generated_text": None,
            "simplified_text": None,
            "status_code": getattr(
                getattr(e, "response", None),
                "status_code",
                None
            ),
            "error": str(e)
        }

    except (ValueError, TypeError) as e:

        return {
            "success": False,
            "generated_text": None,
            "simplified_text": None,
            "status_code": (
                response.status_code if response is not None else None
            ),
            "error": str(e)
        }


if __name__ == "__main__":

    sample = (
        "Machine learning is a field of artificial "
        "intelligence that enables computers to learn from data."
    )

    result = simplify_text(sample)

    print(result)
