import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re


load_dotenv()

TYPE_TITLE = 0
TYPE_CONTENT = 1

class ContentLine:
    """Class to represent a line of content in a character's page."""
    def __init__(self, content_type:int ,text:str, level:int):
        self.text = text
        self.content_type = content_type
        self.level = level

    def __repr__(self):
        return f"(type={self.content_type}, text={self.text}, level={self.level})"


URL_BASE = "https://onepiece.fandom.com"
URL_CANON = URL_BASE + "/es/wiki/Lista_de_personajes_canon#Individuos"
SECTION_TITLE_INICIAL="Sumari"
def create_beautiful_object(url:str):
    """Create a JSON file with One Piece characters and their information.
    information will come from one piece wiki and will scrap the information into a json file
    """
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return None

def get_one_piece_characters():
    result = []
    canon = create_beautiful_object(URL_CANON)
    # read characters table
    tables = canon.find_all("table","wikitable sortable")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("a")
            if cells is not None and len(cells) >= 4:
                personatge = {}
                personatge['name'] = cells[0].text.strip()
                personatge['page_link'] = cells[0]['href']
                personatge['capitol'] = cells[1].text.strip()
                personatge['episodi'] = cells[2].text.strip()
                result.append(personatge)
    return result

def from_dict_to_json(data, file_name):
    """Save a list of dictionaries to a JSON file."""
    import json
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)




def get_character_content(url:str):
    """
    Get the content of a character's page via beautiful soup.
    TOC --> Div[Id=toc"].ul.li.a
    Content div class = mw-content-ltr mw-parser-output
        all childs
        Section start with h2.span[class='mw-headline' id=TOC.section]
        subsection starts with h3.span[class='mw-headline' id=TOC.subsection]
        Content start with p

    """
    content = create_beautiful_object(URL_BASE + url)
    main_content = content.find("div", "mw-content-ltr mw-parser-output")
    if not main_content:
        return "Content not found."
    all_childs = main_content.find_all(recursive=False)
    character_info = [ContentLine(TYPE_TITLE, "Summary", 1)]
    for child in all_childs:
        if child.name == 'h2' or child.name == 'h3' or child.name == 'h4':
            section_title = child.find("span", class_="mw-headline").text.strip()
            #level = last character of chid.name
            level = int(child.name[-1]) if child.name[-1].isdigit() else -1
            character_info.append(ContentLine(TYPE_TITLE, section_title, level))
        if child.name=='p':
            text = child.get_text(strip=False)
            if text:
                character_info.append(ContentLine(TYPE_CONTENT,filter_string_references(text),0 ))
    return character_info

def filter_string_references(text:str)->str:
    """
    Removes all occirences of  [x] in a string and reduce "  " to " " and trainling references " ." to ".
    :param text:
    :return: filtered text
    """
    # Remove all occurrences of [x] where x is any character or number
    filtered_text = re.sub(r'\[\w+\]', '', text)
    # Remove extra spaces
    filtered_text = filtered_text.replace("  ", " ")
    # remove trailing spaces and dots
    filtered_text = filtered_text.replace(" .", ".")
    return filtered_text.strip()


def content_to_markdaown_file(content:list[ContentLine], file_name:str):
    """
    Convert the content to markdown format and save it to a file.
    :param content: List of ContentLine objects
    :param file_name: Name of the file to save the markdown content
    """
    markdown_content = content_to_markdown(content)
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def content_to_markdown(content:list[ContentLine]):
    """
    Convert the content to markdown format and save it to a file.
    :param content: List of ContentLine objects
    :return: Markdown formatted string
    """
    result =""
    for line in content:
        if line.content_type == TYPE_TITLE:
            result = result + f"{'#' * line.level} {line.text}\n"
        elif line.content_type == TYPE_CONTENT:
            result = result + f"{line.text}\n\n"
    return result

if __name__ == "__main__":
    res = get_one_piece_characters()
    #from_dict_to_json(res, "one_piece_characters.json")
    character = get_character_content("/es/wiki/Bartholomew_Kuma")
    content_to_markdaown_file(character, "bartholomew_kuma.md")
    print(res)

