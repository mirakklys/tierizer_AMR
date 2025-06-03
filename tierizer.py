# This script takes csv files of microorganisms to tierize, where tier 1 is the cause of pneumonia, tier 2 - possible causer
# Make sure you install munpy, pandas
# this code can be optimized, the column names "bacterium" and "relative_value_%" should be in your csv

import os
import numpy as np
import pandas as pd

original_list = []                                               # List of microorganisms in the csv file to set as Tier 1, 2
genus = [each.lower().split(" ")[0] for each in original_list]   # The genus is taken as Tier 2; some people already have the tier 2 microorganisms, so feel free to change this list
species = [each.lower() for each in original_list]               # The species known to cause pneumonia is set to Tier 1

directory_in = r"WGS_culture/"                                   # Input folder with csv files
directory_out = r"WGS_culture_tier/"                             # Output folder to store tierized csv files

def tierize(df, species, genus):
    """
    adds a 'tier' column:
      1 – exact species in `species`
      2 – genus in `genus`
      3 – none of the above
    """
    # change the list's elements to lowercase 
    species_set = {each.lower() for each in species}
    genus_set   = {each.lower() for each in genus}

    # start with tier 3
    df = df.copy()                # avoids mutating original df
    df["Tier"] = "3"

    # boolean masks
    genus_mask = (
        df["bacterium"]
          .str.split()            # splits into words
          .str[0]                 # first word = genus
          .str.lower()
          .isin(genus_set)
    )

    species_mask = (
        df["bacterium"]
          .str.split()            
          .str[:2]                # takes first two parts
          .str.join(" ")          # joins back to 'Genus species'
          .str.lower()
          .isin(species_set)
    )

    # applies tiers (order matters: Tier 2 first, then Tier 1 override)
    df.loc[genus_mask, "Tier"] = "2"
    df.loc[species_mask, "Tier"] = "1"
    return df

for each in os.listdir(directory_in):
    if each.endswith("csv"):
        filename_in = os.path.join(directory_in, each)
        filename_out = os.path.join(directory_out, each)
      
        df = pd.read_csv(filename_in)
        df = tierize(df, species, genus)
      
        # Sorts by tier first, then the relative value, then the species
        df = df.sort_values(by = ["Tier", "relative_value_%", "bacterium"], ascending = [True, False, True])

        # saves the dataset to csv in output folder
        df.to_csv("% s" % filename_out, index = False)
