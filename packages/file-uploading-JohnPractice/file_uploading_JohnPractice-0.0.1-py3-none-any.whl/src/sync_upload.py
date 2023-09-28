import requests
from typing import Optional


def upload_file(
    method_name: str,
    data,
    upload_url: str,
    headers: Optional[dict[str, str]],
    *args,
    **kwargs,
) -> requests.request:
    """_summary_

    Args:
        method_name (str): _description_
        data (_type_): _description_
        upload_url (str): _description_
        headers (Optional[dict[str, str]]): _description_

    Returns:
        requests.request: _
    """
    return requests.request(
        method=method_name, url=upload_url, data=data, headers=headers, **kwargs
    )
