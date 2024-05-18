#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import time

from datetime import date
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import List

from cdp_backend.pipeline.ingestion_models import Body
from cdp_backend.pipeline.ingestion_models import EventIngestionModel
from cdp_backend.pipeline.ingestion_models import Session

###############################################################################


def append_meeting_data(meeting, meetings_info, from_dt, to_dt):
    _meeting_data = {}

    meeting_date = meeting.find_element(
        by=By.XPATH, value=".//div[@class='meeting-date']"
    )
    # Thursday, 3 February 2022 @ 10:00 AM
    converted_dt = datetime.strptime(meeting_date.text, "%A, %d %B %Y @ %I:%M %p")
    if from_dt <= converted_dt <= to_dt:
        _meeting_data["date"] = converted_dt
    else:
        return

    try:
        video = meeting.find_element(
            by=By.XPATH,
            value=".//ul[@class='resource-list']//a[contains(@href,"
            "'/Players/ISIStandAlonePlayer.aspx?')]",
        )
    except Exception:
        return
    else:
        _meeting_data["video_player_uri"] = video.get_attribute("href")

    title = meeting.find_element(by=By.XPATH, value=".//div[@class='meeting-title']")
    _meeting_data["title"] = title.text

    meetings_info.append(_meeting_data)


def append_video_duration(driver, info):
    try:
        duration = driver.find_element(
            by=By.XPATH, value="//span[@class='fp-duration']"
        ).text
    except Exception:
        print("Duration not found")
        print(info)
        return

    if duration.count(":") == 1:
        duration = "00:" + duration
    (h, m, s) = duration.split(":")
    info["video_duration"] = timedelta(hours=int(h), minutes=int(m), seconds=int(s))


def append_video_uri(driver, info):
    if "video_player_uri" in info:
        driver.get(info["video_player_uri"])
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[@id='isi_player']",
                    )
                )
            )
        except Exception:
            print("Video player not found after 10 seconds")
            print(info)
            info["error"] = True
            return

        player = driver.find_element(by=By.XPATH, value="//div[@id='isi_player']")
        file_name = player.get_attribute("data-file_name")
        if file_name.count(".mp4") == 0:
            print(f"File name does not contain .mp4: {file_name}")
            print(info)
            info["error"] = True
            return
        info["video_uri"] = "https://video.isilive.ca/missoula/" + file_name
        info.pop("video_player_uri")


def expand_meeting_group(driver, meeting_group_ancestor):
    # expand this meeting type to render meetings
    anchor = meeting_group_ancestor.find_element(
        by=By.XPATH, value=".//a[contains(@class, 'PastMeetingTypesName')]"
    )
    anchor.click()

    # wait until the meeting-headers are visible
    ancestor_id = meeting_group_ancestor.get_attribute("id")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                f"//div[@id='{ancestor_id}']//div[@class='meeting-header']",
            )
        )
    )


def expand_past_meetings(driver):
    # expand the page's list view to render past meetings
    list_button = driver.find_element(
        by=By.CLASS_NAME, value="fc-mergedListViewButton-button"
    )
    list_button.click()
    # TODO: Update to wait for the relevant element to be displayed instead
    time.sleep(3)


def get_scraped_data(
    from_dt: datetime = datetime(2022, 1, 1),
    to_dt: datetime = datetime.today(),
    include_durations=False,
) -> List:
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )

    msla_url = "https://pub-missoula.escribemeetings.com/"
    driver.get(msla_url)
    expand_past_meetings(driver)

    # common ancestor of the anchor that expands the meeting type to display all the
    # meetings, and the meeting-headers themselves
    meeting_group_ancestors = driver.find_elements(
        by=By.XPATH, value="//div[@class='MeetingTypeList']"
    )

    # array of dictionaries, one per video, mutated directly along the way
    meetings_info: List = []
    for meeting_group_ancestor in meeting_group_ancestors:
        # WARNING: this is very necessary and important - ALL years of meetings are
        # rendered but the committee titles are hidden, this would be a very expensive
        # line of code to delete
        if meeting_group_ancestor.is_displayed():
            expand_meeting_group(driver, meeting_group_ancestor)

            meetings = meeting_group_ancestor.find_elements(
                by=By.XPATH, value=".//div[@class='meeting-header']"
            )
            for meeting in meetings:
                if meeting.is_displayed():
                    append_meeting_data(meeting, meetings_info, from_dt, to_dt)

    # navigate to each video player and construct the direct .mp4 uri
    for info in meetings_info:
        append_video_uri(driver, info)
        if include_durations:
            append_video_duration(driver, info)

    if include_durations:
        print_duration_info(meetings_info)

    meetings_info[:] = [meeting for meeting in meetings_info if "error" not in meeting]

    if len(meetings_info) > 2000:
        raise Exception(
            "Something has gone wrong. Way more many meetings than expected "
            "processed."
        )

    return meetings_info


def get_events(
    from_dt: datetime,
    to_dt: datetime,
    **kwargs,
) -> List[EventIngestionModel]:
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

    def create_ingestion_model(e):
        return EventIngestionModel(
            body=Body(name=e["title"]),
            sessions=[
                Session(
                    video_uri=e["video_uri"],
                    session_datetime=e["date"],
                    session_index=0,
                ),
            ],
        )

    get_scraped_results = get_scraped_data(from_dt, to_dt)
    events = list(map(create_ingestion_model, get_scraped_results))
    print(get_scraped_results)
    print(events)
    print(len(events))

    return events


def print_duration_info(meetings_info):
    durations = []
    for info in meetings_info:
        if "video_duration" in info:
            durations.append(info["video_duration"])
    total_meeting_time = functools.reduce(lambda a, b: a + b, durations)
    print("TOTAL MEETING TIME")
    print(total_meeting_time)
    avg_meeting_time_per_week = total_meeting_time / date.today().isocalendar()[1]
    print("AVERAGE MEETING TIME PER WEEK")
    print(avg_meeting_time_per_week)
