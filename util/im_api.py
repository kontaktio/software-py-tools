from util.common import post, get_config, Config, API_KEY

HEADERS = {
    "Accept": "application/vnd.com.kontakt+json;version=10",
}

# Configuration
def create_config(config, api_key: str):
    augmented_header = HEADERS.copy()
    augmented_header[API_KEY] = api_key
    post(
        f"{get_config(Config.IM_API_URL)}/config/create",
        params=config,
        headers=augmented_header,
    )
