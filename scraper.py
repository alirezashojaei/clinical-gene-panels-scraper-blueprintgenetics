import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

class BlueprintgeneicsScraper:
    def __init__(self):
        self.blueprintgenetics_test_panels_url = "https://blueprintgenetics.com/tests/panels/"

    async def fetch_soup(self, url: str):
        """
        Fetch the HTML content from the given URL and parse it with BeautifulSoup.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return soup
    
    async def scrape_test_panels(self):
        soup = await self.fetch_soup(self.blueprintgenetics_test_panels_url)

        # Find all collapse sections
        collapse_sections = soup.select("div.collapse-section")
        data = []
        for category in collapse_sections:
            # Find the toggle-collapse link to get category name
            toggle_link = category.select_one("a.toggle-collapse")
            if toggle_link:
                category_name = toggle_link.get_text(strip=True)
                
                # Find all test-list-item divs within this section
                test_items = category.select("div.test-list-item")
                
                for item in test_items:
                    # Find the link within the test-list-item
                    link_tag = item.select_one("a")
                    if link_tag:
                        panel_name = link_tag.get_text(strip=True)
                        href = link_tag.get("href")
                        
                        # Clean up panel name (remove any extra text like "New" badges)
                        if "New" in panel_name:
                            panel_name = panel_name.replace("New", "").strip()
                        
                        data.append([category_name, panel_name, href])

        return pd.DataFrame(data, columns=['category', 'panel_name', 'link'])
    
    async def scrape_test_panel_content(self, panel_link: str):
        """
        Scrape the content of a test panel.
        """
        soup = await self.fetch_soup(panel_link)
        
        # Find all table-responsive divs
        table_divs = soup.find_all("div", class_="table-responsive")
        
        data = []
        
        for i, div in enumerate(table_divs):
            table = div.find("table")
            if not table:
                continue

            # Determine if this is coding or non-coding table
            is_coding = i == 0  # First table is coding, second is non-coding # TODO: check if this is correct
            
            # Get table headers
            headers = []
            header_row = table.find("thead").find("tr") if table.find("thead") else None
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all("th")]
            
            # Get table rows
            rows = table.find("tbody").find_all("tr") if table.find("tbody") else []
            
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= len(headers):
                    
                    # Add data based on table type
                    if is_coding and len(cells) >= 5:
                        row_data = {
                            'gene': cells[0].get_text(strip=True),
                            'genomic_location_hg19': '',
                            'hgvs': '',
                            'refseq': '',
                            'associated_phenotypes': cells[1].get_text(strip=True),
                            'inheritance': cells[2].get_text(strip=True),
                            'clinvar': cells[3].get_text(strip=True),
                            'hgmd': cells[4].get_text(strip=True),
                            'coding': True
                        }
                    elif not is_coding and len(cells) >= 5:
                        row_data = {
                            'gene': cells[0].get_text(strip=True),
                            'genomic_location_hg19': cells[1].get_text(strip=True),
                            'hgvs': cells[2].get_text(strip=True),
                            'refseq': cells[3].get_text(strip=True),
                            'associated_phenotypes': '', 
                            'inheritance': '', 
                            'clinvar': '', 
                            'hgmd': '', 
                            'coding': False
                        }
                    
                    data.append(row_data)
        
        return pd.DataFrame(data)
