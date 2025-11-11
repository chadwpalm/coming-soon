import requests
import subprocess
import os
import logging
from icalendar import Calendar
from datetime import datetime, date, time, timedelta
import re

# Logging setup. You must input a log file location.

log_file = "/config/coming-soon.log"

# Here are where the file locations will be input. It is recommended to use absolute paths instead of relative ones.

ffmpegLoc = "/coming-soon" # Location of ffmpeg binary
textFile = "/config/upcoming.txt" # Location to save the intermediate text file
inputFile = f"/config/{os.getenv("INPUT_FILE")}" # Input file. This is the video you want to use as the background.
outputDir = "/output" # This is the location where the final video is saved.
outputFileName = f"{os.getenv("OUTPUT_FILE")}" # Output file. This is the name of the final output file.
fontFileEnv = f"/config/{os.getenv('FONT_FILE', 'arial.ttf')}"
fontFile = fontFileEnv if os.path.exists(fontFileEnv) else "/coming-soon/arial.ttf"
iCalURL_radarr = os.getenv("ICAL_URL_RADARR", "") # This is the URL to retrieve Radarr ical file.
iCalURL_sonarr = os.getenv("ICAL_URL_SONARR", "") # This is the URL to retrieve Sonarr ical file.

# Here are the parameters for the text overlayed onto the video. The defaults are what works in my setup.
# fontsize: fontsize in pixels
# fontcolor: Usable strings can be found here: https://ffmpeg.org/ffmpeg-utils.html#color-syntax
# x: The x coordinate for the top-left of the text area
# y: The y coordinate for the top-left of the text area
# startTime: The time of the video (in seconds) the text appears
# endTime: The time of the video (in seconds) the text disappears

fontSize = int(os.getenv("FONT_SIZE", 70))
fontColor = os.getenv("FONT_COLOR", "white")
x = int(os.getenv("X_COORD", 300))
y = int(os.getenv("Y_COORD", 150))
startTime = int(os.getenv("START_TIME",5))
endTime = int(os.getenv("END_TIME", 13))
centerText = os.getenv("CENTER_TEXT", "false").lower() == "true"
lineSpacing = int(os.getenv("LINE_SPACING", 10))

if centerText:
    x = "(w-text_w)/2"
    y = "(h-text_h)/2"

outputFile = f"{outputDir}/{outputFileName}"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Fetching of ical file

def fetch_ical_data(url_radarr, url_sonarr):
    def get_ical(url):
        if not url or not str(url).strip():
            return ""
        url = str(url).strip()
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except:
            return ""

    radarr_text = get_ical(url_radarr)
    sonarr_text = get_ical(url_sonarr)

    if radarr_text or sonarr_text:
        logging.info("Fetched iCal data successfully")

    return radarr_text, sonarr_text

# Checking if just a date and makes the object a datetime object for downsteam operations

def normalize_dt(dt):
    
    if isinstance(dt, str):
        try:
            # Try parsing datetime with timezone (e.g., "2025-02-26 01:00:00+00:00")
            dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S%z")
            dt = dt.replace(tzinfo=None)  # Strip timezone info
        except ValueError:
            # If that fails, assume it's a date only format (e.g., "2024-11-06")
            dt = datetime.strptime(dt, "%Y-%m-%d")

    # If the input is a datetime object with timezone info
    elif isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)  # Remove timezone info

    if isinstance(dt, date) and not isinstance(dt, datetime):
        # If the input is a date object, combine with time
        dt = datetime.combine(dt, time.min)

    dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)  # Reset to midnight
    return dt

def extract_episode(input_str):
    # Regular expression to match the episode in the format '1x05'
    match = re.match(r"^(.*?) - (\d+)x(\d+)", input_str)
    if match:
        # Return the three parts: episode name, season number, episode number
        return match.group(1), match.group(2), match.group(3)
    return None, None, None  # Return None if no match is found

# Parsing of the ical file to create a filtered list of upcoming digital releases

def ical_to_filtered_list(ical_data):
    events = []
    today = datetime.now()

    def parse_calendar(ical_text, source_name):
        if not ical_text or not ical_text.strip():
            logging.info(f"No {source_name} iCal data – skipping.")
            return []
        try:
            cal = Calendar.from_ical(ical_text)
            return list(cal.walk())
        except Exception as e:
            logging.error(f"Failed to parse {source_name} iCal: {e}")
            return []

    radarr_components = parse_calendar(ical_data[0], "Radarr")
    sonarr_components = parse_calendar(ical_data[1], "Sonarr")


    for component in radarr_components:
        if component.name == "VEVENT":
            dtstart = normalize_dt(component.get('dtstart').dt)
            print (dtstart)
            if dtstart > today:
                summary = str(component.get('summary'))
                logging.info(f"Analyzing: {summary} {dtstart}")
                if "Digital Release" in summary:
                    cleaned_summary = summary.replace(" (Digital Release)", "")
                    dtstart_str = dtstart.strftime("%m/%d/%Y")
                    events.append((cleaned_summary, dtstart_str))
                    logging.info(f"Processing {cleaned_summary}")
                else:
                    logging.info("Not a digital release")

    for component in sonarr_components:
        if component.name == "VEVENT":
            dtstart = normalize_dt(component.get('dtstart').dt)
            if dtstart > today:
                summary = str(component.get('summary'))

                seas_epi = extract_episode(summary)

                show, season, episode = seas_epi

                logging.info(f"Analyzing: {summary} {dtstart}")

                print ("Show name: ", seas_epi[0], "\nSeason: ", seas_epi[1], "\nEpisode: ", seas_epi[2])
                
                if season == "1" and episode == "01":
                    cleaned_summary = f"{show} (Series Premiere)"
                    dtstart_str = dtstart.strftime("%m/%d/%Y")
                    events.append((cleaned_summary, dtstart_str))
                    logging.info(f"Processing {cleaned_summary}")
                elif season != "1" and episode == "01":
                    cleaned_summary = f"{show} (Season Premiere)"
                    dtstart_str = dtstart.strftime("%m/%d/%Y")
                    events.append((cleaned_summary, dtstart_str))
                    logging.info(f"Processing {cleaned_summary}")
                else:
                    logging.info("Not a new show or new season")

    events.sort(key=lambda x: datetime.strptime(x[1], "%m/%d/%Y"))
    print(events)
    return events

# Writes the list to the intermediate file.

def write_to_file(events, filename):
    with open(filename, "w") as file:
        for summary, dtstart in events:
            file.write(f"{dtstart} - {summary}\n") # You can edit this line to format how you desire. {dtstart} is the release date and {summary} is the movie title.
    logging.info(f"Wrote {len(events)} events to {filename}")

# This is the running of the ffmpeg command. It takes in the intermediate file and overlays the text onto the video.

def run_ffmpeg_command():
    command = (
        f"{ffmpegLoc}/ffmpeg -y -i {inputFile} -vf "
        f"\"drawtext=textfile={textFile}:fontfile={fontFile}:fontsize={fontSize}:fontcolor={fontColor}:x={x}:y={y}:line_spacing={lineSpacing}:enable='between(t,{startTime},{endTime})'\" "
        f"-c:a copy {outputFile}"
    )
    logging.info(f"FFmpeg command: {command}")
    subprocess.run(command, shell=True, check=True)
    logging.info("FFmpeg command executed successfully")

# If there are no upcoming movies the Coming Soon video will not be made and the existing one will be deleted. This is because software (ex: Plex) will not show anything
# if the file doesn't exist. Delete lines 121 thru 123 if you do not want this function to run.

def delete_file_if_no_events(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        logging.info(f"Deleted file {filepath} because there were no events")

# The main function

def main():
    try:
        ical_data = fetch_ical_data(iCalURL_radarr, iCalURL_sonarr)
        
        events = ical_to_filtered_list(ical_data)
        
        write_to_file(events, textFile)
        
        if events:
            run_ffmpeg_command()
        else:
            delete_file_if_no_events(outputFile)
            logging.info("There are no upcoming movies to process")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

