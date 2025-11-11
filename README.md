### Update November 11th, 2025:

Two new changes have been made to the script:

1. There is a new ENV variable (Docker) or standard variable (Native) to change the name of the output file. (See parameter list below)
2. Using both Radarr and Sonarr are not required anymore. Simply leave out ICAL_URL_RADARR or ICAL_URL_SONARR from the ENV variables and it will not process that app. Malformed or invalid URLs will now be skipped rather than erroring out.

### Update March 4th, 2025:

Note: This script has been updated to include Sonarr listings. It will show when a new series or season starts for a television show. You will need to update your environment variables to change the Radarr variable and add a Sonarr variable. See the "docker cli" and "docker compose" sections below for new variables.

# "Coming Soon" Pre-Roll Creation Script

This is a Python script for generating a "Coming Soon" pre-roll using data from Radarr (Radarr must be in use to use this script).

The way it works is it grabs the current iCal calendar from Radarr, then parses through the data to find upcoming digital releases and creates an intermediate text file listing the releases. It then overlays the text file onto an input video of your choice using ffmpeg and outputs the final file for your use.

## Radarr

To obtain the link for iCal, go to the Calendar tab from the left menu bar, then click on the "iCal Link" button on the top of the page. Keep "Show as All-Day Event" unchecked, but you can choose if you want "Include Unmonitored" checked or not. Leave the Tags blank and copy the text from the iCal Feed box into the string in the Python script.

# Docker

Docker image location: [chadwpalm/coming-soon](https://hub.docker.com/repository/docker/chadwpalm/coming-soon)

The only current tag is "latest".

## Example

An example template: [Template](https://www.youtube.com/watch?v=kKc8jydRlzc)

Example of processed final video: [Final](https://www.youtube.com/watch?v=IJHpwps4DYM)

## Usage

Note: docker cli requires quotation marks for parameters and docker compose requires no quotation marks.

Everything needed for the script to run is in the Docker image.

### docker cli

```
docker run -d \
    --name=coming-soon \
    --network host \
    -e CRON_SCHEDULE="0 0 * * *" \
    -e TZ=America/Los_Angeles \
    -e INPUT_FILE="ComingSoonTemplate.mp4" \
    -e OUTPUT_FILE="MyFile.mp4" \
    -e FONT_FILE="times new roman.ttf" \
    -e ICAL_URL_RADARR="http://x.x.x.x:7878/feed/v3/calendar/Radarr.ics?apikey=******************" \
    -e ICAL_URL_SONARR="http://x.x.x.x:8989/feed/v3/calendar/Sonarr.ics?apikey=******************" \
    -e FONT_SIZE="70" \
    -e FONT_COLOR="white" \
    -e X_COORD="300" \
    -e Y_COORD="150" \
    -e CENTER_TEXT="false" \
    -e LINE_SPACING="10"
    -e START_TIME="5" \
    -e END_TIME="13" \
    -e UID="1000" \
    -e GID="1000" \
    -v /host/config/dir:/config \
    -v /host/output/dir:/output \
    --restart unless-stopped \
    chadwpalm/coming-soon:latest
```

### docker compose

```
  comingsoon:
    image: chadwpalm/coming-soon:latest
    container_name: coming-soon
    environment:
      - CRON_SCHEDULE=0 0 * * *
      - TZ=America/Los_Angeles
      - INPUT_FILE=ComingSoon.mp4
      - OUTPUT_FILE=MyFile.mp4
      - ICAL_URL_RADARR=http://x.x.x.x:7878/feed/v3/calendar/Radarr.ics?apikey=********************
      - ICAL_URL_SONARR=http://x.x.x.x:8989/feed/v3/calendar/Sonarr.ics?apikey=********************
      - FONT_SIZE=70
      - FONT_COLOR=white
      - X_COORD=300
      - Y_COORD=150
      - CENTER_TEXT=false
      - LINE_SPACING=10
      - START_TIME=5
      - END_TIME=13
      - UID=1000
      - GID=1000
    volumes:
      - /host/config/dir:/config
      - host/output/dir:/output
    restart: unless-stopped
    network_mode: "host"
```

| Param                       | Description                                                                                                                                                                                                                                                                                                                                                       |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| --name                      | The name you want to give to the container.                                                                                                                                                                                                                                                                                                                       |
| -e UID                      | (Optional) The user id for the settings file.                                                                                                                                                                                                                                                                                                                     |
| -e GID                      | (Optional) The group id for the settings file.                                                                                                                                                                                                                                                                                                                    |
| -e CRON_SCHEDULE            | (Required) The times you want the script to run.                                                                                                                                                                                                                                                                                                                  |
| -e TZ                       | (Recommended) Sets the time zone for the logs and is essential for schedule accuracy.                                                                                                                                                                                                                                                                             |
| -e INPUT_FILE               | (Required) The name of the template file the text will be overlaid on. This needs to be placed in the mounted config directory.                                                                                                                                                                                                                                   |
| -e OUTPUT_FILE              | (Optional) The name of the output file created. If omitted it will use the default "ComingSoon.mp4"                                                                                                                                                                                                                                                               |
| -e FONT_FILE                | (Optional) The name of the truetype font file. Must be a ttf file and placed in the mounted config directory. This parameter is optional and if ommited arial font will be used by default.                                                                                                                                                                       |
| -e ICAL_URL_RADARR          | (Optional) This is the iCal link generated from Radarr (See above for example). Ommiting this variable will prevent Radarr from being used in the final list.                                                                                                                                                                                                     |
| -e ICAL_URL_SONARR          | (Optional) This is the iCal link generated from Sonarr (See above for example). Ommiting this variable will prevent Sonarr from being used in the final list.                                                                                                                                                                                                     |
| -e FONT_SIZE                | (Required) The font size of the generated text in pixels.                                                                                                                                                                                                                                                                                                         |
| -e FONT_COLOR               | (Required) Color of the generated text. Usable strings can be found here: [color-syntax](https://ffmpeg.org/ffmpeg-utils.html#color-syntax)                                                                                                                                                                                                                       |
| -e X_COORD                  | (Required) The x coordinate for the top-left of the text area in pixels.                                                                                                                                                                                                                                                                                          |
| -e Y_COORD                  | (Required) The y coordinate for the top-left of the text area in pixels.                                                                                                                                                                                                                                                                                          |
| -e CENTER_TEXT              | (Optional) If set to "true" it centers the text on the screen. This will override the X and Y coordinates. Set to "false" to use X and Y coordinates. If ommited it will default to "false".                                                                                                                                                                      |
| -e LINE_SPACING             | (Optional) Sets the spacing between each movie title line in pixels. If ommited it will default to 10 pixels.                                                                                                                                                                                                                                                     |
| -e START_TIME               | (Required) The start time (in seconds) the text will appear in the video.                                                                                                                                                                                                                                                                                         |
| -e END_TIME                 | (Required) The end time (in seconds) the text will appear in the video.                                                                                                                                                                                                                                                                                           |
| -v /host/config/dir:/config | This is the mount points for the config directory. This is where the input file and font file need to be placed and where the log in intermediate text file will be generated. The left of the colon will be the path to the config on the host machine. The right of the colon will be the path of the config in the container and should always be **/config**. |
| -v /host/output/dir:/output | This is the mount points for the output directory. This is where the final output file will be saved. The left of the colon will be the path to the output on the host machine. The right of the colon will be the path of the out in the container and should always be **/output**.                                                                             |
| --restart                   | Docker [restart behavior](https://docs.docker.com/engine/reference/commandline/run/#restart).                                                                                                                                                                                                                                                                     |

This UID and GID should match the user and group setting used on the host so that the generated files are for the same user/group as the host account and prevents any permissions issues. These values both default to 1000 is not entered.

### Building Docker Image

If you want to make modifications and rebuild the Docker image for yourself you need to edit the app-docker.py script as this is the one that gets built into the image.....not app.py.

- Clone the repo
- Go into the directory (probably "coming-soon" unless you changed it during cloning)
- Run the command `docker build -t <image-name>:<tag> .` (Make sure to add the period at the end. It represents building from the Dockerfile in the current directory, not the end of a sentence)

## Native Install

**Ignore everything below if you are using Docker**

For native applications use **app.py** (app-docker.py is only used during the building of the Docker container and can be ignored in native applications). The script is commented to help guide you through the setup.

It is recommended to automate the running of the script at least once a day to keep the pre-roll up to date. This can be done through a cronjob or any other scheduling method of your choice.

The version of ffmpeg included in this repo is a verison that has been compiled with the necessary libraries to work with adding overlays to video files. Other versions may not work for you. You can substitute the font file with anything you want, you just need to make the filename change accordingly in the script.

### Important

This Python script uses the library "icalendar" to parse the iCal information received from Radarr. You will need to install the library onto your system using pip. This may also require you to install the pip package on your system. I won't go into any Python or Linux usage details here. Google or ChatGPT is a good resource for helping in these situations.

Typical install for the library would be:

    python3 -m pip install icalendar

Note: This package serves as a starting template and I will not be entertaining any pull requests or issues. This comes as-is and it is up to you to modify and use it however you please and have a somewhat working knowledge of Python and Linux.
