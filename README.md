# digiprod-gen

[![PyPI - Version](https://img.shields.io/pypi/v/digiprod-gen.svg)](https://pypi.org/project/digiprod-gen)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/digiprod-gen.svg)](https://pypi.org/project/digiprod-gen)

-----

**Table of Contents**

- [Description](#description)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [License](#license)

## Description
Digital Product Generator is a [streamlit](https://streamlit.io) app that allows users to create digital products such a Print on Demand (POD) designs.
The designs are created with the help generative AI such as GPT-3.5 or Midjourney.


## Installation

```console
pip install digiprod-gen
```

## Prerequisites
Create a [streamlit secret](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management) TOML file before running this app locally.
```console
mkdir .streamlit
printf 'open_ai_api_key = ""
scrape_ops_api_key = ""
[proxy_perfect_privacy]
user_name = ""
password = ""' > .streamlit/secrets.toml
```
If it not exists yet, you have to create some credentials/api keys:
1. openai api key: https://platform.openai.com/account/api-keys
2. scrape ops api key: https://scrapeops.io/app/settings
3. perfect privacy credentials: https://www.perfect-privacy.com/en

## Local Setup
### Setup Docker Container similar to streamlit cloud container
```console
docker build --progress=plain --tag digiprod-gen:latest .
```

### Run custom Docker Container

```console
docker run -ti -p 8501:8501 --rm digiprod-gen:latest
docker run -ti -p 8501:8501 --rm digiprod-gen:latest /bin/bash
docker run -ti -p 8501:8501 -v $(pwd):/app --rm digiprod-gen:latest  # linux
docker run -ti -p 8501:8501 -v ${pwd}:/app --rm digiprod-gen:latest  # powershell
docker run -ti -p 8501:8501 -v %cd%:/app --rm digiprod-gen:latest  # cmd.exe
```


## Open TODOs:

- [ ] Add loading bar for image generation
- [ ] Remove python time wait with wait_until_element_exists()
- [ ] Place loading bar on right place
- [ ] Add session views (with st.empty) for all major frontend views
- [ ] Add more mba marketplaces
- [ ] Make publish button visible if product is ready for publishing
- [ ] Allow user to change tolerance and out pixels
- [x] Catch case, image already uploaded and user clicks a second time on upload
- [ ] Include xpaths, web scraping parser related codes to config
- [ ] Display mba warnings  after upload to user


## License

`digiprod-gen` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
