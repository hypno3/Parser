import requests
from bs4 import BeautifulSoup as bs
import re
from connection import init_connection, append_data

#Define the needed page
def get_soup(url):
    try:
        r = requests.get(url)
        return bs(r.text, 'html.parser')
    except requests.exceptions.HTTPError as e:
        return("HTTP Error {e}")

#print("Page availability, status: ", r.status_code)

#find and check the company name (google)
def find_company_name(soup):

    company_tag = soup.find('span', class_='typography_display-s__qOjh6 typography_appearance-default__AAY17 title_displayName__TtDDM')
    return company_tag.get_text(strip=True) if company_tag else ''

#find the average rating of the company
def find_rating(soup):
    rating_tag = soup.find('span', class_='typography_heading-m__T_L_X typography_appearance-default__AAY17')
    return rating_tag.text.strip() if rating_tag else None

#find the number of all reviews 
def find_reviews(soup):
    reviews_tag = soup.find('p', class_='typography_body-l__KUYFJ typography_appearance-default__AAY17')
    reviews = reviews_tag.text.strip() if reviews_tag else None
    return re.search(r'\d+\,\d{3,}', reviews).group() if re.search(r'\d+\,\d{3,}', reviews) else '0%' 

#Find the stars container
def find_stars(soup):
    review_container = soup.find('div', class_='styles_container__z2XKR')
    # Define the scores of the rating
    score = ["one", "two", "three", "four", "five"]
    stars_percentages = []
    # Check if the reviews container is found
    if review_container:
        for i in score:
            star_tag = soup.find('label', attrs={"data-star-rating": i})
            star = star_tag.text.strip() if star_tag else None
            # Use regular expression to find the only values with percentage
            percentage = re.search(r'\d+%', star).group() if re.search(r'\d+%', star) else '0%'  # 0 if the value was not found
            stars_percentages.append(percentage)
    else:
        #The container with reviews is not found
        stars_percentages = ['0%', '0%', '0%', '0%', '0%'] 

    return stars_percentages

def main():

    URL_TEMPLATE = "https://www.trustpilot.com/review/www.google.com"
    soup = get_soup(URL_TEMPLATE)
    
    worksheet = init_connection()

    #append data to google sheets, in the column B
    append_data(worksheet, find_company_name(soup), "B1")
    append_data(worksheet, find_rating(soup), "B2")
    append_data(worksheet, find_reviews(soup), "B3")

    #put the stars info into the table using for loop
    count = 4

    for i in find_stars(soup):
        append_data(worksheet, i, "B"+str(count))
        count+=1

if __name__ == "__main__":
    main() 
