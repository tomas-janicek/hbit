from url_normalize import url_normalize  # type: ignore


def create_url(base: str, path: str) -> str:
    url = f"{base}/{path}"
    return url_normalize(url)  # type: ignore
