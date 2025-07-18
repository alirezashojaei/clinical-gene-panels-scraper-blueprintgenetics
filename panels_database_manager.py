import os
import pandas as pd


class PanelsDatabaseManager:
    def __init__(self, database_path: str = None):
        self.database_path = database_path
        self.panel_columns = ['category', 'panel_name', 'link']
        self.panel_content_columns = ['gene', 'genomic_location_hg19', 'hgvs', 'refseq', 'associated_phenotypes', 'inheritance', 'clinvar', 'hgmd', 'coding']
        self.columns = self.panel_columns + self.panel_content_columns
        
        self._initialize_database(database_path)

    def _initialize_database(self, database_path: str):
        if database_path and os.path.exists(database_path):
            self.database = pd.read_csv(database_path, usecols=self.columns, sep='\t')
        else:
            self.database = pd.DataFrame(columns=self.columns)

    def update_panels(self, panels: pd.DataFrame):
        """
        Update the database with new panels. 

        Args:
            panels (pd.DataFrame): A pandas DataFrame containing the panels to update.
                The columns must be the same as the panel_columns.

        Raises:
            ValueError: If the panels are not a pandas DataFrame or do not have the same columns as the database.
        """
        if not isinstance(panels, pd.DataFrame):
            raise ValueError("Panels must be a pandas DataFrame")
        
        if not all(col in self.panel_columns for col in panels.columns):
            raise ValueError(f"Panels must have the required columns: {self.panel_columns}")
        
        # Make a backup of the database before making changes
        database_backup = self.database.copy(deep=True)
        try:
            # Check each panel one by one
            for _, panel in panels.iterrows():
                # Check if this panel already exists in the database
                existing_panel = self.database[
                    (self.database['category'] == panel['category']) &
                    (self.database['panel_name'] == panel['panel_name']) &
                    (self.database['link'] == panel['link'])
                ]

                # If panel doesn't exist, add it to the database
                if existing_panel.empty:
                    # Create a new row with the panel data and empty values for gene-related columns
                    new_row = panel.copy()
                    # Use pandas' reindex to ensure all columns are present and fill missing ones with empty string
                    new_row = new_row.reindex(self.columns, fill_value='')

                    # Add the new panel to the database
                    self.database = pd.concat([self.database, pd.DataFrame([new_row])], ignore_index=True)
        except Exception as e:
            # Rollback to the backup if any error occurs
            self.database = database_backup
            raise e

    def update_panel_content(self, category: str, panel_name: str, panel_content: pd.DataFrame):
        """
        Add or update panel content to the database.

        Args:
            category (str): The category of the panel to add content to.
            panel_name (str): The name of the panel to add content to.
            panel_content (pd.DataFrame): A pandas DataFrame containing the panel content to add. Should have the same columns as the self.panel_content_columns.
        """
        if not isinstance(panel_content, pd.DataFrame):
            raise ValueError("Panel content must be a pandas DataFrame")
        
        if not all(col in self.panel_content_columns for col in panel_content.columns):
            raise ValueError(f"Panel content must have the required columns: {self.panel_content_columns}")
            
        database_backup = self.database.copy(deep=True)
        try:
            # Check if the panel exists
            panel = self.database[
                (self.database['category'] == category) &
                (self.database['panel_name'] == panel_name)
            ]
            if panel.empty:
                raise ValueError(f"Panel {panel_name} does not exist")
            
            # Fill three empty columns: category, panel_name, link from the existing panel info
            panel_row = self.database[
                (self.database['category'] == category) &
                (self.database['panel_name'] == panel_name)
            ]

            # Delete only the records that match both category and panel_name to avoid duplicates
            self.database = self.database[
                ~((self.database['category'] == category) & (self.database['panel_name'] == panel_name))
            ]
            
            panel_content['category'] = panel_row['category'].values[0]
            panel_content['panel_name'] = panel_row['panel_name'].values[0]
            panel_content['link'] = panel_row['link'].values[0]

            self.database = pd.concat([self.database, panel_content], ignore_index=True)
        except Exception as e:
            self.database = database_backup
            raise e

    def get_panels(self, has_not_content: bool = False):
        """
        Get all unique panels from the database using only the panel_columns.
        If has_not_content is True, return only panels that do NOT have content (i.e., no gene records).
        """
        if has_not_content:
            # Find panels that do NOT have content (i.e., no gene records)
            panels_with_content = self.database[self.database['gene'].notna()][self.panel_columns].drop_duplicates()
            # Return only panels that are NOT in panels_with_content
            panels = self.database[~self.database.set_index(self.panel_columns).index.isin(
                panels_with_content.set_index(self.panel_columns).index
            )]
            
        else:
            # Select only the panel_columns and drop duplicates
            panels = self.database[self.panel_columns].drop_duplicates()

        return panels

    def get_panel_content(self, panel_name: str):
        """
        Get the content of a panel.

        Args:
            panel_name (str): The name of the panel to get the content of.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the content of the panel.
        """
        return self.database[self.database['panel_name'] == panel_name][self.panel_content_columns]

    def save_database(self, database_path: str = None):
        """
        Save the database to a file.

        Args:
            database_path (str): The path to the database file. If not provided, the database will be saved to the path provided in the constructor.
        """
        if self.database_path:
            self.database.to_csv(self.database_path, index=False, sep='\t')
        elif database_path:
            self.database.to_csv(database_path, index=False, sep='\t')
        else:
            raise ValueError("No database path provided")
        