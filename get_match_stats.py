import json
from bs4 import BeautifulSoup

def scrape_full_match_data(soup):
    """
    Comprehensive function that scrapes both match details and statistics
    Returns a single dictionary containing all match information
    """
    # Initialize the result dictionary
    match_data = {
        "match_details": {},
        "statistics": []
    }
    
    # Get match details
    header = soup.find('div', class_='css-1pf15hj-MFHeaderInfoBoxCSS')
    if header:
        # Get date and time
        date_element = header.find('time')
        if date_element:
            match_data["match_details"]["datetime"] = date_element.get('datetime')
            match_data["match_details"]["formatted_date"] = date_element.text.strip()
        
        # Get competition info
        competition = header.find('div', class_='css-6k5lms-TournamentCSS')
        if competition:
            league_link = competition.find('a')
            if league_link:
                match_data["match_details"]["competition"] = {
                    'name': league_link.text.strip(),
                    'url': league_link.get('href')
                }
    
    # Get teams info
    teams_section = soup.find('h1')
    if teams_section:
        teams_text = teams_section.text.strip()
        teams = teams_text.split(' vs ')
        if len(teams) == 2:
            match_data["match_details"]["teams"] = {
                'home': teams[0].split('(')[0].strip(),
                'away': teams[1].split('(')[0].strip()
            }
    
    # Find left column containing statistics
    main_content = soup.find('div', id='__next')
    match_css = main_content.find('div', class_='css-19auws2-MatchCSS edsvb150') if main_content else None
    inner_div = match_css.find('div') if match_css else None
    left_column = inner_div.find('div', class_='css-10wb1x-Column-LeftColumn edsvb152') if inner_div else None
    
    # Get statistics if left_column is found
    if left_column:
        stat_blocks = left_column.find_all("li", class_=lambda c: c and "Stat" in c)
        for block in stat_blocks:
            title_tag = block.find("span", class_=lambda c: c and "StatTitle" in c)
            stat_title = title_tag.text.strip() if title_tag else None
            
            value_tags = block.find_all("span", class_=lambda c: c and "StatValue" in c)
            if value_tags and stat_title:
                home_value = value_tags[0].text.strip() if len(value_tags) > 0 else None
                away_value = value_tags[1].text.strip() if len(value_tags) > 1 else None
                
                if home_value is not None or away_value is not None:
                    match_data["statistics"].append({
                        stat_title: {
                            "home": home_value,
                            "away": away_value
                        }
                    })
    
    return match_data
