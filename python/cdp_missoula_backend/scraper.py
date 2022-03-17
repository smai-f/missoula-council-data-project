#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from bs4 import BeautifulSoup
from cdp_backend.pipeline import ingestion_models
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from typing import List

###############################################################################


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

    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.add_argument("--headless")
    driver = webdriver.Chrome("./chromedriver", options=options)

    msla_url = "https://pub-missoula.escribemeetings.com/?Year=2022"
    driver.get(msla_url)

    # expands the list view to include past meetings
    list_button = driver.find_element(
        by=By.CLASS_NAME, value="fc-mergedListViewButton-button"
    )
    driver.execute_script("arguments[0].click();", list_button)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # need to expand all the lil accordian thingies to get all meeting titles returned here
    meeting_divs = soup.find_all("div", attrs={"class": "meeting-title"})

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
