'''
File: names.py
Author: Michael Lucky
Date: September 22, 2023
Description: Module to abstract the names used in the company_scraper project, this will allow for easier logic within the scraper and data handling. This module will be used as an interface for pulling company names and all associated alias's associated with them. This allows for separate data governance maintenance on a single module that can be used across the entire project without touching the logic of the scraper.

Copyright (c) 2023 Jelloow

For inquiries or permissions regarding the use of this code, please contact:
info@jelloow.com
'''

# ONLY CHANGE THIS IF THERE IS AN UPDATE TO THE NAMES OF A COMPANY OR BRAND. URL CHANGES SHOULD BE DONE IN THE URLS MODULE 

def agency_names() -> dict[str, list[str]]:

    # currently used for testing purposes

    # name used within the data warehouse as the key and all alias's used to scrape data as the values
    return {
        'webfx': {
            'linkedin' : ['webfxinc'],
            'goodfirms' : ['webfx'],
            'sortlist' : ['webfx'],
            'other' : ['web fx', 'web-fx', 'WebFx', 'Web Fx'],
        },
        'smartsites': {
            'linkedin' : ['smartsites'],
            'goodfirms' : ['smartsites'],
            'sortlist' : ['smartsites'],
            'other' : ['smart sites', 'smart-sites', 'SmartSites', 'Smart Sites'],
        },
        'publicis': {
            'linkedin' : ['publicis'],
            'goodfirms' : ['publicis-sapient', 'publicis-pixelpark', 'publicis-welcomm'],
            'sortlist' : ['publicis', 'publicis-291a3825-7544-4ea9-be3c-0f7f6c9c3981', 'publicis-138'],
            'other' : ['publicis sapient', 'publicis-sapient', 'Publicis Sapient', 'Publicis-Sapient'],
        },
        'OMD': {
            'linkedin' : ['omd', 'omd-usa', 'omd-emea'],
            'goodfirms' : ['omd'],
            'sortlist' : ['omd', 'omd-77362380-5c90-48f8-bc16-4541b112eabc'],
            'other' : ['OMD', 'omd', 'Omnicom Media Group', 'omnicom media group'],
        },
        'vmlyr': {
            'linkedin' : ['vmlyr'],
            'goodfirms' : ['vmly-r'],
            'sortlist' : ['vmly-r'],
            'other' : ['VMLY&R', 'vmlyr', 'VMLY&R Commerce', 'vmlyr commerce'],
        },
        'mindshare': {
            'linkedin' : ['mindshare'],
            'goodfirms' : ['mindshare'],
            'sortlist' : ['mindshare-be96cfc6-f8e5-474b-b1c0-62df64858739', 'mindshare-73'],
            'other' : ['Mindshare', 'mindshare'],
        },
        'bbdo': {
            'linkedin' : ['bbdo'],
            'goodfirms' : ['amv-bbdo', 'bbdo', 'bbdo-mexico', 'colenso-bbdo', 'r-k-swamy-bbdo'],
            'sortlist' : ['bbdo-44', 'bbdo', 'bbdo-43'],
            'other' : ['BBDO', 'bbdo'],
        },
        'oglivy': {
            'linkedin' : ['ogilvy'],
            'goodfirms' : ['ogilvy', 'ogilvy-brasil', 'ogilvypro-technologies'],
            'sortlist' : ['the-ogilvy-cross', 'ogilvy-65', 'ogilvy'],
            'other' : ['Ogilvy', 'ogilvy'],
        },
        'tbwa': {
            'linkedin' : ['tbwa'],
            'goodfirms' : ['friends-tbwa', 'tbwa-italy', 'tbwa-belgium', 'tbwa-moscow', 'tbwa-worldwide'],
            'sortlist' : ['tbwa-71', 'tbwa-70', 'tbwa-72', 'tbwa-interactive-c1fb50d0-9e48-41a3-846d-ea2e48887764', 'tbwa-69', 'tbwa-65'],
            'other' : ['TBWA', 'tbwa'],
        },
        'ddb': {
            'linkedin' : ['ddb'],
            'goodfirms' : ['ddb', 'lemon-ddb'],
            'sortlist' : ['ddb', 'ddb-germany', 'mw-ddb', 'ddb-azerbaijan'],
            'other' : ['DDB', 'ddb'],
        },
        'mccann': {
            'linkedin' : ['mccannworldgroup'],
            'goodfirms' : ['mccann'],
            'sortlist' : ['mccann-de', 'mccann-78', 'mccann-85', 'mccann-1409dff6-a249-4fb3-811c-c6490ff1767f', 'mccann-80', 'mccann-bristol-85c97f4e-f3d9-41b8-95b1-d7b138f403c8'],
            'other' : ['McCann', 'mccann'],
        },
        'epsilon': {
            'linkedin' : ['epsilon'],
            'goodfirms' : ['epsilon'],
            'sortlist' : ['epsilon', 'epsilon-15'],
            'other' : ['Epsilon', 'epsilon'],
        },
        'starcomm': {
            'linkedin' : ['starcom1'],
            'goodfirms' : ['starcomm'],
            'sortlist' : ['starcomm', 'starcom-gb'],
            'other' : ['Starcomm', 'starcomm'],
        },
        'mediacom': {
            'linkedin' : ['mediacom'],
            'goodfirms' : ['mediacom', 'mccann-bristol', 'mccann-prague'],
            'sortlist' : ['mediacom', 'mediacom-ar', 'mediacom-75', 'mediacom-77', 'mediacom-806f61ac-05a8-48ca-9488-7559d18e38c4'],
            'other' : ['MediaCom', 'mediacom'],
        },
        'leo_burnett': {
            'linkedin' : ['leo-burnett'],
            'goodfirms' : ['leo-burnett'],
            'sortlist' : ['leo-burnett-37', 'atelier-gb', 'leo-burnett-singapore', 'leo-burnett-7e2144c9-c4db-4c74-a59b-d583ae32f99b'],
            'other' : ['Leo Burnett', 'leo burnett'],
        },
        'edelman': {
            'linkedin' : ['edelman'],
            'goodfirms' : ['edelman', 'edelman-canada'],
            'sortlist' : ['edelman-17', 'edelman-19', 'edelman-16', 'edelman-gb', 'edelman-ba9fa969-e48b-4565-bc20-d53804f796f5', 'edelman'],
            'other' : ['Edelman', 'edelman'],
        },
        'grey_global_group': {
            'linkedin' : [],
            'goodfirms' : [],
            'sortlist' : [],
            'other' : ['Grey Global Group', 'grey global group'],
        },
        'merkle': {
            'linkedin' : ['merkle'],
            'goodfirms' : ['merkle'],
            'sortlist' : ['merkle', 'merkle-66948d16-9963-45bc-8ab7-06b190bf80d9', 'merkle-5'],
            'other' : ['Merkle', 'merkle'],
        },
        'universal_mccann': {
            'linkedin' : ['um-universal-mccann-gmbh', 'universal-mccann', 'universal-mccann-belgrade'],
            'goodfirms' : [],
            'sortlist' : ['universal-mccann'],
            'other' : ['Universal McCann', 'universal mccann'],
        },
        'fleishman_hillard': {
            'linkedin' : ['fleishmanhillard'],
            'goodfirms' : ['fleishman-hillard'],
            'sortlist' : ['fleishman-hillard-10', 'fleishman-hillard-italia-s-r-l-5aba62a0-1cad-4359-8e8a-bc64d840fb5d', 'fleishman-hillard-spain', 'fleishmanhillard-16', 'fleishmanhillard', 'fleishman-hillard-frankfurt', 'fleishman-hillard-inc', 'fleishman-hillard-link', 'fleishman-hillard-france', 'fleishman-hillard-italia-s-r-l', 'fleishman-hillard-hong-kong-ltd'],
            'other' : ['Fleishman Hillard', 'fleishman hillard'],
        },
        'rga': {
            'linkedin' : ['rga-limited'],
            'goodfirms' : [],
            'sortlist' : ['rga'],
            'other' : ['R/GA', 'rga'],
        },
        'huge': {
            'linkedin' : ['hugeinc'],
            'goodfirms' : ['huge'],
            'sortlist' : ['huge', 'huge-sg', 'huge-6'],
            'other' : ['Huge', 'huge'],
        },
        'razorfish': {
            'linkedin' : ['sapientrazorfish'],
            'goodfirms' : [],
            'sortlist' : ['razorfish-a732d444-e61d-433c-a4fb-eac8b16d917e', 'razorfish-china', 'razorfish', 'razorfish-india', 'razorfish-australia', 'razorfish-hong-kong', 'razorfish-france-paris'],
            'other' : ['Razorfish', 'razorfish'],
        },
        'wieden_kennedy': {
            'linkedin' : ['wieden---kennedy'],
            'goodfirms' : ['wieden-kennedy'],
            'sortlist' : ['wieden-kennedy-be492134-3e5e-4127-ac99-726fd1bb6a58'],
            'other' : ['Wieden Kennedy', 'wieden kennedy'],
        },
        'we_are_social': {
            'linkedin' : ['we-are-social'],
            'goodfirms' : ['we-are-social'],
            'sortlist' : [],
            'other' : ['We Are Social', 'we are social'],
        },
        'sid_lee': {
            'linkedin' : ['sid-lee'],
            'goodfirms' : ['sid-lee'],
            'sortlist' : ['sid-lee-6'],
            'other' : ['Sid Lee', 'sid lee'],
        },
        'crispin_porter_bogusky': {
            'linkedin' : ['crispinporterbogusky'],
            'goodfirms' : ['crispin-porter-bogusky'],
            'sortlist' : ['crispin-porter-bogusky-b7ef048f-3743-4262-9708-bea27f8f8777', 'crispin-porter-bogusky-3', 'crispin-porter-bogusky'],
            'other' : ['Crispin Porter Bogusky', 'crispin porter bogusky'],
        },
        'droga5': {
            'linkedin' : ['droga5', 'droga5dublin'],
            'goodfirms' : [],
            'sortlist' : ['droga5', 'droga5-5cb0ef4a-5751-4410-9107-81d2a7a0749c', 'droga5-gb', 'droga5-5', 'droga5-australia'],
            'other' : ['Droga5', 'droga5'],
        },
        'amp_agency': {
            'linkedin' : ['amp-agency'],
            'goodfirms' : ['amp-agency'],
            'sortlist' : [],
            'other' : ['AMP Agency', 'amp agency'],
        },
        'vaynermedia': {
            'linkedin' : ['vaynermedia'],
            'goodfirms' : [],
            'sortlist' : ['vaynermedia', 'vaynermedia-2'],
            'other' : ['VaynerMedia', 'vaynermedia'],
        },
    }

def brand_names() -> dict[str, list[str]]:

    # currently used for testing purposes

    # name used within the data warehouse as the key and all alias's used to scrape data as the values
    return {
        'webfx': {
            'linkedin' : ['webfxinc'],
            'goodfirms' : ['webfx'],
            'sortlist' : ['webfx'],
            'other' : ['web fx', 'web-fx', 'WebFx', 'Web Fx'],
        },
        'smartsites': {
            'linkedin' : ['smartsites'],
            'goodfirms' : ['smartsites'],
            'sortlist' : ['smartsites'],
            'other' : ['smart sites', 'smart-sites', 'SmartSites', 'Smart Sites'],
        },
    }