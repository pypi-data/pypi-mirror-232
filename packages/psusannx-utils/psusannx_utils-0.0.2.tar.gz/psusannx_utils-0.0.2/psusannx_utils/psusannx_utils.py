"""Useful functions to be used throughout the psusannx packages"""
import unidecode
import pandas as pd
from datetime import datetime

def standardize_name(name):
    """
    Decode the special characters within a player's 
    name and make the name all lower case characters

    Parameters
    ----------
    name: str
        The raw sting containing the name of the player.

    Returns
    -------
    The clean & standardised player name.
    """
    
    return unidecode.unidecode(name).lower().replace("-"," ")


def number_position_suffix(number):
    """
    Suffix a number with either st, nd, rd or th.

    Parameters
    ----------
    number: The number (integer) that should be suffixed

    Returns
    -------
    if 1 is input, will return '1st'. If 2 is input will return '2nd' etc.
    """

    # Set up a liast for each possible suffix
    date_suffix = ["th", "st", "nd", "rd"]

    # Use modular arithmetic to figure out which suffix to use
    if number % 10 in [1, 2, 3] and number not in [11, 12, 13]:
        return str(number) + date_suffix[number % 10]
    else:
        return str(number) + date_suffix[0]
    

def sort_season_data(df):
    """
    Put the matches in chronological order (Must be a 'Date' field)
    & also in alphabetical order of the home team.
    Also delete duplicate rows of data to keep it clean.

    Parameters
    ----------
    df: The season data with the "Date" & "Home_team" columns to sort the data with.
    
    Returns
    -------
    The same dataframe that was entered, sorted by the ascending Date & Home_team columns.
    """

    # Make a copy of the input dataframe
    df_ = df.copy()

    # Make the date field a datetime
    df_["Date"] = pd.to_datetime(df.Date)

    # Sort the values
    df_sorted = df_.sort_values(by=["Date", "Home_team"]).reset_index(drop=True)

    # Make sure to just keep the date
    df_sorted["Date"] = pd.to_datetime(df_sorted["Date"]).dt.date

    # Make sure the 'Date' column is just a string
    df_sorted = df_sorted.astype({"Date": str})

    return df_sorted


def get_season_from_date(date):
    """
    Return the season in the format yyyy_yyyy from a date argument.
    The date can be a datetime.datetime object or a string date with the format 
    yyyy-mm-dd. 

    Parameters
    ----------
    date: Either a valid datetime object or a date string in the format %Y-%m-%d.

    Returns
    -------
    The season that the date falls in, in the format yyyy_yyyy.
    """

    # If the entered argument is a datetime object then nothing needs to be done
    if isinstance(date, datetime):
        date_datetime = date

    # If it is a string then it needs to be processed as a datetime for calculations
    else:
        # Create a datetime object from the string provided
        date_datetime = datetime(int(date[:4]), int(date[5:7]), int(date[8:10]))

    # Figure out what season the game belongs to in the form yyyy_yyyy
    if date_datetime.month <= 7:

        # If the month is before August then it is in the 2nd half of the season, and the season began last year
        season = f"{date_datetime.year-1}_{date_datetime.year}"

    else:

        # If the month is after August, then it is in the 1st half of the season, and the season began this year
        season = f"{date_datetime.year}_{date_datetime.year+1}"
        
    return season