import requests
from bs4 import BeautifulSoup as bs
import re
from connection2 import init_connection, append_data_rows, append_data_cells, upload_file
import string

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

def uploader():
    upload_directory = 'api/' 
    input("Select the API key file in JSON format, press any button to continue..")
    return upload_file(upload_directory)

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

    worksheet = init_connection(upload_file)

    append_data_cells(worksheet, "Company name", "A1")
    append_data_cells(worksheet, "Average rating", "A2")
    append_data_cells(worksheet, "Total reviews", "A3")

    #put the stars info into the table using for loop
    stars = 4
    count = 1
    for i in find_stars(soup):
        append_data_cells(worksheet, str(count)+" Stars", "A"+str(stars))
        count+=1
        stars+=1
    
    # Assuming find_stars(soup) returns a list of five elements
    data_values = [
        find_company_name(soup), 
        find_rating(soup),
        find_reviews(soup), 
    ] + find_stars(soup)

    # Check each column starting from 'A' to 'Z'
    for col_letter in string.ascii_uppercase:
        # Check if the first cell in the column is empty
        if not worksheet.acell(f'{col_letter}1').value:
            # If it's empty, this is the column we'll insert data into
            for index, value in enumerate(data_values, start=1):
                cell = f'{col_letter}{index}'
                worksheet.update_acell(cell, value)
            break  # Data has been inserted, no need to check further columns

if __name__ == "__main__":
    main() 
