import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re


def scrape_panel_data(url, panel_name, category):
    """Scrape data from a single panel page"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all table-responsive divs
        table_divs = soup.find_all("div", class_="table-responsive")
        
        data = []
        
        for i, div in enumerate(table_divs):
            table = div.find("table")
            if not table:
                continue
                
            # Determine if this is coding or non-coding table
            is_coding = i == 0  # First table is coding, second is non-coding
            
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
                    row_data = {
                        'Category': category,
                        'Panel': panel_name,
                        'Table_Type': 'Coding' if is_coding else 'Non-coding'
                    }
                    
                    # Add data based on table type
                    if is_coding and len(cells) >= 5:
                        row_data.update({
                            'Gene': cells[0].get_text(strip=True),
                            'Associated_phenotypes': cells[1].get_text(strip=True),
                            'Inheritance': cells[2].get_text(strip=True),
                            'ClinVar': cells[3].get_text(strip=True),
                            'HGMD': cells[4].get_text(strip=True),
                            'Coding': 'Yes'
                        })
                    elif not is_coding and len(cells) >= 5:
                        row_data.update({
                            'Gene': cells[0].get_text(strip=True),
                            'Associated_phenotypes': '',  # Non-coding doesn't have phenotypes
                            'Inheritance': '',  # Non-coding doesn't have inheritance
                            'ClinVar': '',  # Non-coding doesn't have ClinVar
                            'HGMD': '',  # Non-coding doesn't have HGMD
                            'Coding': 'No'
                        })
                    
                    data.append(row_data)
        
        return data
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []


def main():
    # Read the existing CSV file with panel links
    panels_df = pd.read_csv("data.csv")
    
    all_data = []
    
    print(f"Starting to scrape {len(panels_df)} panels...")
    
    for index, row in panels_df.iterrows():
        category = row['category']
        panel_name = row['panel_name']
        panel_url = row['link']
        
        print(f"Scraping panel {index + 1}/{len(panels_df)}: {panel_name}")
        
        # Scrape data from this panel
        panel_data = scrape_panel_data(panel_url, panel_name, category)
        all_data.extend(panel_data)
        
        # Add a small delay to be respectful to the server
        time.sleep(1)
    
    # Convert to DataFrame
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Reorder columns to match requested format
        column_order = ['Category', 'Panel', 'Gene', 'Associated_phenotypes', 'Inheritance', 'ClinVar', 'HGMD', 'Coding', 'Table_Type']
        df = df[column_order]
        
        # Save to CSV
        df.to_csv("panel_data.csv", index=False)
        print(f"✅ Successfully scraped data for {len(df)} entries from {len(panels_df)} panels!")
        print(f"Data saved to panel_data.csv")
        
        # Print summary
        print(f"\nSummary:")
        print(f"Total entries: {len(df)}")
        print(f"Coding entries: {len(df[df['Coding'] == 'Yes'])}")
        print(f"Non-coding entries: {len(df[df['Coding'] == 'No'])}")
        print(f"Unique panels: {df['Panel'].nunique()}")
        print(f"Unique genes: {df['Gene'].nunique()}")
        
    else:
        print("❌ No data was scraped!")


if __name__ == "__main__":
    main()