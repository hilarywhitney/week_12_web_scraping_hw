#!/usr/bin/env python
# coding: utf-8


#Set up
from bs4 import BeautifulSoup
from splinter import Browser
import pandas as pd
import datetime as dt


# In[56]:


#Visit Mars News Site
def scrape_mars_news(browser):
    # Visit URL
    url = 'https://mars.nasa.gov/news'
    browser.visit(url)

    # get first list item and wait half a second if not immediately
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=0.5)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    slide_element = news_soup.select_one('ul.item_list li.slide')

    try:
        news_title = slide_element.find('div', class_='content_title').get_text()
        news_title

        news_paragraph = slide_element.find('div', class_='article_teaser_body').get_text()
        news_paragraph
    except AttributeError:
        return None, None
    return news_title, news_paragraph


# ### JPL Mars Space Images - Featured Image
def get_jpl_images(browser):
    # Visit URL
    featured_image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(featured_image_url)

    full_image_element = browser.find_by_id('full_image')
    full_image_element.click()

    browser.is_element_present_by_text('more info', wait_time = 1)
    more_info_element = browser.find_link_by_partial_text('more info')
    more_info_element.click()

    html = browser.html
    image_soup = BeautifulSoup(html, 'html.parser')

    img = image_soup.select_one('figure.lede a img')
    try:
        img_url = img.get('src')
    except AttributeError:
        return None
    
    img_url = f'https://www.jpl.nasa.gov{img_url}'

    return img_url

# ### Mars Weather
def mars_weather_twitter(browser):

    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)

    html = browser.html
    weather_soup = BeautifulSoup(html, 'html.parser')

    mars_weather_tweet = weather_soup.find('div', attrs={'class':'tweet','data-name':'Mars Weather'})
    mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()

    return mars_weather


# In[60]:

def hemisphere(browser):
    astro_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(astro_url)
    hemisphere_image_urls = []
    
    links = browser.find_by_css('a.product-item h3')

    for link in range(len(links)):
        hemisphere = {}
        browser.find_by_css('a.product-item h3')[link].click()
        sample_element = browser.find_link_by_text('Sample')
        hemisphere['img_url'] = sample_element['href']
        hemisphere['title'] = browser.find_by_css('h2.title').text
        
        hemisphere_image_urls.append(hemisphere)
        
        browser.back()

    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    hemisphere_soup = BeautifulSoup(html_text, 'html.parser')
    try:
        title_element = hemisphere_soup.find('h2', class_='title').get_text()
        sample_element = hemisphere_soup.find('a', text="Sample").get('href')
    except AttributeError:
        title_element = None
        sample_element = None
    hemisphere = {"title": title_element, "img_url": sample_element}
    return hemisphere

def space_facts(browser):
    try:
        space_df = pd.read_html('https://space-facts.com/mars/')[0]
    except BaseException:
        return None

    space_df.columns = ['description','values']
    space_df.set_index('description', inplace = True)

    return space_df.to_html(classes = "table table-striped")


def scrape_all():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless = False)
    news_title, news_paragraph = scrape_mars_news(browser)
    img_url = get_jpl_images(browser)
    mars_weather = mars_weather_twitter(browser)
    hemisphere_image_urls = hemisphere(browser)
    space_table = space_facts(browser)
    #get a datetime of scrape
    timestamp = dt.datetime.now()

    data = {'news_title': news_title,
            'news_paragraph': news_paragraph,
            'jpl_image': img_url,
            'mars_weather': mars_weather,
            'hemisphere': hemisphere_image_urls,
            'mars_facts':space_table,
            'last_modified': timestamp}

    browser.quit()
    return data
if __name__ == "__main__":
    print(scrape_all())


