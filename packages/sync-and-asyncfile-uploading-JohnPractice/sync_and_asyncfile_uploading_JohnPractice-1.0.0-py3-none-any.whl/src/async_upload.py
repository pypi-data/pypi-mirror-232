from typing import Optional
from aiohttp import ClientSession


async def upload_file(
    method_name: str,
    data,
    upload_url: str,
    headers: Optional[dict[str, str]],
    *args,
    **kwargs,
) -> ClientSession:
    """_summary_

    Args:
        method_name (str): _description_
        data (_type_): _description_
        upload_url (str): _description_
        headers (Optional[dict[str, str]]): _description_

    Returns:
        ClientSession: _description_
    """
    async with ClientSession() as session:
        async with session.request(
            method=method_name, url=upload_url, data=data, headers=headers, **kwargs
        ) as response:
            return response
