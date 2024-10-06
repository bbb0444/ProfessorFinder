from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import requests

new_line_break = 101
bar = "=" * new_line_break
line = "-" * new_line_break


def scrape_links(url, driver):
    driver.get(url)

    # Wait for the div with id="staffListContent" to be present
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "staffListContent"))
    )

    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find the div with id="staffListContent"
    staff_list_content = soup.find("div", id="staffListContent")

    if not staff_list_content:
        print("Div with id='staffListContent' not found.")
        return []

    # Print the HTML content of the div to debug
    print("HTML content of the div with id='staffListContent':")
    # print(staff_list_content.prettify())

    # Extract all links from the div
    links = []
    for link in staff_list_content.find_all("a"):
        name = link.text.strip()
        href = link.get("href")
        if href and href.startswith("http"):
            links.append([name, href])

    return links


def extract_p_tags(url, driver):
    driver.get(url)

    try:
        # Wait for the div with id="collapseprofileresearchinterest" to be present
        WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located(
                    (By.ID, "collapseprofileresearchinterest")
                ),
                EC.presence_of_element_located((By.ID, "collapseBio")),
                EC.presence_of_element_located((By.ID, "headingprofilethemes")),
                EC.presence_of_element_located((By.ID, "collapseReStudents")),
            )
        )
    except TimeoutException:
        print(
            f"Timeout while waiting for the element with id='collapseprofileresearchinterest' on {url}"
        )
        return ""

    # Parse the HTML content
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Find the div with id="collapseprofileresearchinterest"
    collapse_profiler_div = soup.find("div", id="collapseprofileresearchinterest")
    profile_biography_div = soup.find("div", id="collapseBio")
    themes_div = soup.find("div", id="collapseprofilethemes")
    students_div = soup.find("div", id="collapseReStudents")

    # p_tags_research = collapse_profiler_div.find_all("p")
    # p_tags_bio = profile_biography_div.find_all("p")
    # span_themes = themes_div.find_all("span")
    # p_tags = span_themes + p_tags_bio + p_tags_research
    # extracted_text = "\n".join([p_tag.text.strip() for p_tag in p_tags])

    def extract_text_from_div(div):
        return "\n".join(div.stripped_strings)

    extracted_text = "\n".join(
        filter(
            None,
            [
                (
                    extract_text_from_div(collapse_profiler_div)
                    if collapse_profiler_div
                    else ""
                ),
                (
                    extract_text_from_div(profile_biography_div)
                    if profile_biography_div
                    else ""
                ),
                extract_text_from_div(themes_div) if themes_div else "",
                extract_text_from_div(students_div) if students_div else "",
            ],
        )
    )

    if not extracted_text:
        print(f"No content found for {url}")
        return ""
    return extracted_text


# def save_to_file(name, text, filename):
#     # print(name, text[:100])
#     with open(filename, "w", encoding="utf-8") as f:
#         f.write("\n")
#         f.write(f"Name: {name}\n\n")
#         f.write(text)


# def insert_line_breaks(text, line_length):
#     return "\n".join(
#         text[i : i + line_length] for i in range(0, len(text), line_length)
#     )


def main():
    driver = webdriver.Chrome()
    url = "https://www.sydney.edu.au/engineering/about/our-people/academic-staff.html"  # Replace with the actual URL you want to scrape
    output_filename = "scraped_data.txt"

    try:
        links = scrape_links(url, driver)
        print(links)

        buffer = []

        count = 0
        if links:
            try:
                for link in links:
                    count += 1
                    print(f"Processing link: {link[0]}")
                    try:
                        content = extract_p_tags(link[1], driver)
                        # Save the content to a buffer
                        if content:
                            print("Content found.")
                            buffer.append(
                                f"{line}\nProfessor Name: {link[0]}\n{bar}\n{content}\n{line}\n\n"
                            )
                        else:
                            print("Null")
                    except Exception as e:
                        print(f"An error occurred while processing {link[0]}: {str(e)}")

                    # Add a small delay between iterations
                    time.sleep(1)

                    # if count > 3:
                    #     break

                # Write the buffer to the file once at the end
            except Exception as e:
                print(f"An error occurred while processing... {str(e)}")
            finally:
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write("\n".join(buffer))

        print("Scraping completed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the WebDriver
        driver.quit()


if __name__ == "__main__":
    main()
