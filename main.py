import asyncio
import os
import argparse
from scraper import BlueprintgeneicsScraper
from panels_database_manager import PanelsDatabaseManager
from tqdm import tqdm


async def scrape_panel_content(scraper, db_manager, category, panel_name, panel_link, pbar):
    """
    Scrape content for a single panel and update the database.
    """
    try:
        # Scrape the panel content
        panel_content = await scraper.scrape_test_panel_content(panel_link)
        
        if not panel_content.empty:
            # Update the database with the panel content
            db_manager.update_panel_content(category, panel_name, panel_content)
            # Save database after each update
            db_manager.save_database()
            pbar.set_description(f"✓ {panel_name} ({len(panel_content)} genes)")
            return True
        else:
            pbar.set_description(f"⚠ {panel_name} (no content)")
            return False
            
    except Exception as e:
        pbar.set_description(f"✗ {panel_name} (error)")
        print(f"\nError scraping {panel_name}: {str(e)}")
        return False


async def main():
    """
    Main function to scrape Blueprint Genetics test panels and update the database.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape Blueprint Genetics test panels and update the database.')
    parser.add_argument('--database-path', 
                       default="data/blueprint_panels_database.csv",
                       help='Path to the database CSV file (default: data/blueprint_panels_database.csv)')
    
    args = parser.parse_args()
    
    # Initialize the database manager
    database_path = args.database_path
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    
    db_manager = PanelsDatabaseManager(database_path)
    
    # Initialize the scraper
    scraper = BlueprintgeneicsScraper()
    
    print("Starting Blueprint Genetics panel scraping...")
    
    try:
        # Step 1: Scrape all test panels
        print("Scraping test panels list...")
        panels_df = await scraper.scrape_test_panels()
        print(f"Found {len(panels_df)} panels across {panels_df['category'].nunique()} categories")
        
        # Step 2: Update database with new panels
        print("Updating database with new panels...")
        db_manager.update_panels(panels_df)

        db_manager.save_database()
        
        # Step 3: Get panels that don't have content yet
        panels_without_content = db_manager.get_panels(has_not_content=True)
        print(f"Found {len(panels_without_content)} panels without content")
        
        if len(panels_without_content) == 0:
            print("All panels already have content. No scraping needed.")
            return
        
        # Step 4: Scrape content for panels that don't have it (concurrent in batches of 4)
        print("Scraping panel content (concurrent in batches of 4)...")
        
        # Process panels in batches of 4
        batch_size = 4
        total_panels = len(panels_without_content)
        
        with tqdm(total=total_panels, desc="Scraping panels") as pbar:
            for i in range(0, total_panels, batch_size):
                # Get current batch of panels
                batch = panels_without_content.iloc[i:i+batch_size]
                
                # Create tasks for current batch
                tasks = []
                for _, panel in batch.iterrows():
                    panel_name = panel['panel_name']
                    category = panel['category']
                    panel_link = panel['link']
                    
                    # Create task for this panel
                    task = scrape_panel_content(scraper, db_manager, category, panel_name, panel_link, pbar)
                    tasks.append(task)
                
                # Execute current batch concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update progress bar for this batch
                for _ in results:
                    pbar.update(1)
        
        # Step 5: Print summary
        print("\n=== SCRAPING SUMMARY ===")
        total_panels = len(db_manager.get_panels())
        panels_with_content = len(db_manager.get_panels()) - len(db_manager.get_panels(has_not_content=True))
        total_genes = len(db_manager.database[db_manager.database['gene'].notna()])
        
        print(f"Total panels: {total_panels}")
        print(f"Panels with content: {panels_with_content}")
        print(f"Total genes: {total_genes}")
        print(f"Database saved to: {database_path}")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 