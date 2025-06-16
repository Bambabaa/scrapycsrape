import json
from bs4 import BeautifulSoup

def full_match_data(soup):
    """
    Comprehensive function that scrapes both match details and statistics
    Returns a single dictionary containing all match information
    """
    # Initialize the result dictionary with proper nesting
    match_data = {
        "match_details": {
            "teams": {},
            "score": {},
            "status": None
        },
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

    # Get teams info and score from the header section
    header_section = soup.find('section', class_='css-154n3ly-MFHeaderFullscreenSection')
    if header_section:
        # Get teams
        team_sections = header_section.find_all('div', class_=lambda x: x and 'TeamMarkup' in x)
        if len(team_sections) == 2:
            # Process home team
            home_section = team_sections[0]
            home_name = home_section.find('span', class_=lambda x: x and 'TeamNameOnTabletUp' in x)
            home_link = home_section.find_parent('a')
            home_img = home_section.find('img')
            
            match_data["match_details"]["teams"]["home"] = {
                'name': home_name.text.strip() if home_name else None,
                # 'url': home_link.get('href') if home_link else None,
                # 'logo': home_img.get('src') if home_img else None
            }
            
            # Process away team
            away_section = team_sections[1]
            away_name = away_section.find('span', class_=lambda x: x and 'TeamNameOnTabletUp' in x)
            away_link = away_section.find_parent('a')
            away_img = away_section.find('img')
            
            match_data["match_details"]["teams"]["away"] = {
                'name': away_name.text.strip() if away_name else None,
                # 'url': away_link.get('href') if away_link else None,
                # 'logo': away_img.get('src') if away_img else None
            }

        # Get score and status
        score_wrapper = header_section.find('div', class_='css-1cf82ng-MFHeaderStatusWrapper')
        if score_wrapper:
            score_element = score_wrapper.find('span', class_=lambda x: x and 'Score' in x)
            if score_element:
                scores = score_element.text.strip().split(' - ')
                match_data["match_details"]["score"] = {
                    'home': scores[0] if len(scores) > 0 else None,
                    'away': scores[1] if len(scores) > 1 else None
                }
            
            status_element = score_wrapper.find('span', class_=lambda x: x and 'StatusReason' in x)
            if status_element:
                match_data["match_details"]["status"] = status_element.text.strip()

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
