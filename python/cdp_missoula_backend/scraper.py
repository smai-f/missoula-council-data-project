#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from bs4 import BeautifulSoup
from cdp_backend.pipeline import ingestion_models
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import List

###############################################################################

# TODO: Handle the sad paths
def get_scraped_data() -> List:
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.add_argument("--headless")
    # Chrome Driver v99 - there is a known issue with Chrome v98 and Selenium's is_displayed()
    driver = webdriver.Chrome("./chromedriver", options=options)

    msla_url = "https://pub-missoula.escribemeetings.com/"
    driver.get(msla_url)

    # expand the page's list view to render past meetings
    list_button = driver.find_element(
        by=By.CLASS_NAME, value="fc-mergedListViewButton-button"
    )
    driver.execute_script("arguments[0].click();", list_button)
    # TODO: Update to wait for the relevant element to be displayed instead
    time.sleep(3)

    # common ancestor of the anchor that expands the meeting type to display all the meetings,
    # and the meeting-headers themselves
    meeting_type_ancestors = driver.find_elements(
                               by=By.XPATH, value="//div[@class='MeetingTypeList']"
                             )

    meetings_info = []
    for meeting_type_ancestor in meeting_type_ancestors:
        # WARNING: this is very necessary and important - ALL years of meetings are rendered but
        # the committee titles are hidden, this would be a very expensive line of code to delete
        if meeting_type_ancestor.is_displayed():
            # expand this meeting type to render meetings
            anchor = meeting_type_ancestor.find_element(
                by=By.XPATH, value=".//a[contains(@class, 'PastMeetingTypesName')]"
            )
            driver.execute_script("arguments[0].click();", anchor)

            # wait until the meeting-headers are visible
            ancestor_id = meeting_type_ancestor.get_attribute("id")
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, f"//div[@id='{ancestor_id}']//div[@class='meeting-header']"))
            )

            # get all the info we're interested from from each meeting header
            meetings = meeting_type_ancestor.find_elements(
                by=By.XPATH, value=".//div[@class='meeting-header']"
            )
            for meeting in meetings:
                if meeting.is_displayed():
                    _meeting_data = {}
                    title = meeting.find_element(
                        by=By.XPATH, value=".//div[@class='meeting-title']"
                    )
                    _meeting_data["title"] = title.text

                    date = meeting.find_element(
                        by=By.XPATH, value=".//div[@class='meeting-date']"
                    )
                    _meeting_data["date"] = date.text
                    meetings_info.append(_meeting_data)
                
    return [len(meetings_info), meetings_info]


def get_events(
    from_dt: datetime,
    to_dt: datetime,
    **kwargs,
) -> List[ingestion_models.EventIngestionModel]:
    """
    Get all events for the provided timespan.

    Parameters
    ----------
    from_dt: datetime
        Datetime to start event gather from.
    to_dt: datetime
        Datetime to end event gather at.

    Returns
    -------
    events: List[EventIngestionModel]
        All events gathered that occured in the provided time range.

    Notes
    -----
    As the implimenter of the get_events function, you can choose to ignore the from_dt
    and to_dt parameters. However, they are useful for manually kicking off pipelines
    from GitHub Actions UI.
    """

    # Go to https://pub-missoula.escribemeetings.com/?Year=2022
    # within div class=past-meetings -> calendar-item

    # COMMITTEE NAME

    # meeting-title -> <a> child text ("City Council Meeting")

    # MEETING DATE

    # meeting-date child text ("Monday, 14 March 2022 @ 6:00 PM")

    # VIDEO FILE

    # Click on every single <a href=./Players/ISIStandAlonePlayer.aspx?*
    # On new page, grab the div id=isi_player's data-file_name
    # (Encoder1_AF_2022-03-02-02-03.mp4)
    # The video link is https://video.isilive.ca/missoula/ + value from previous step

    video_prefix = "https://video.isilive.ca/missoula/"

    hardcoded_mtg = ingestion_models.EventIngestionModel(
        body=ingestion_models.Body(
            name="Affordable Housing Resident Oversight Committee"
        ),
        sessions=[
            ingestion_models.Session(
                video_uri=video_prefix + "Encoder1_AHROC_2022-03-09-07-51.mp4",
                session_datetime=datetime(2022, 3, 9, 18),
                session_index=0,
            ),
        ],
    )

    return [hardcoded_mtg]
