import requests
from bs4 import BeautifulSoup


# Make a request to the Blueprint Genetics panels page
url = "https://blueprintgenetics.com/tests/panels/neurology/amyotrophic-lateral-sclerosis-panel/"
response = requests.get(url)

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

with open("blueprint.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())
    