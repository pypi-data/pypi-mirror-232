'''
File: urls.py
Author: Michael Lucky
Date: September 13, 2023
Description: Module to abstract the urls used in the company_scraper project, this will allow for easier maintenance, scalability, and integration. This module will be used as an interface for the urls to scrape from.

Copyright (c) 2023 Jelloow

For inquiries or permissions regarding the use of this code, please contact:
info@jelloow.com
'''

# ONLY CHANGE THIS IF A URL IS NO LONGER VALID AND NEEDS TO BE UPDATED. COMPANY NAME CHANGES SHOULD BE DONE IN THE NAMES MODULE

import jelloow_names.names as n

def agency_websites() -> list[str]:
    
    # currently used for testing purposes
    return ['https://www.jelloow.com']

def agency_goodfirms() -> list[str]:
    names = n.agency_names()
    urls = {}
    for agency in names:
        for alias in names[agency]['goodfirms']:
            urls[f'https://www.goodfirms.co/company/{alias}'] = agency

    return urls

def agency_sortlist() -> dict[str, str]:
    names = n.agency_names()
    urls = {}
    for agency in names:
        for alias in names[agency]['sortlist']:
            urls[f'https://www.sortlist.com/agency/{alias}'] = agency
    
    return urls

def agency_linkedin() -> list[str]:
    names = n.agency_names()
    urls = {}
    for agency in names:
        for alias in names[agency]['linkedin']:
            urls[f'https://www.linkedin.com/company/{alias}'] = agency

    return urls

def brand_urls() -> list[str]:
    
    # currently used for testing purposes
    return ['https://www.jelloow.com']