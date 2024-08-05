"""This module repeatedly grabs web page and webcam data and uploads 
it to Dropbox."""

import time
import argparse
import yaml
from prometheus_client import start_http_server, Counter
from webcam import Webcam
import dropbox_upload
import web_screenshot

CONFIG_YAML = 'config.yaml'

class weather_updater:
    def __init__(self):
        with open(CONFIG_YAML, 'r') as file: # pylint: disable=unspecified-encoding
            self.config = yaml.safe_load(file)

        self.webcam = Webcam(self.config['webcam_index'])
        self.db = dropbox_upload.DropboxUploader(self.config['dropbox_app_key'],
                                                 self.config['dropbox_app_secret'],
                                                 self.config['dropbox_refresh_token'])

        start_http_server(self.config['prom_port'])
        self.weather_capture_successful = Counter('weather_capture_successful',
                                                  'Weather captures successful')
        self.weather_capture_failed = Counter('weather_capture_failed',
                                              'Weather captures failed')
        self.webcam_frame_successful = Counter('webcam_frame_successful',
                                               'Webcam frame captures successful')
        self.webcam_frame_failed = Counter('webcam_frame_failed',
                                             'Webcam frame captures failed')
        self.upload_failed = Counter('dropbox_upload_failed',
                                     'Webcam frame captures failed')
        self.upload_successful = Counter('dropbox_upload_successful',
                                         'Webcam uploads successful')

    def do_webcam(self):
        local_fn = self.config['webcam_path'] + self.config['webcam_prefix']
        local_fn += time.strftime("%Y%m%d_%H%M%S") + ".jpg"

        frame = self.webcam.capture_frame()
        if frame is None:
            print("Failed to capture frame")
            self.webcam_frame_failed.inc()
            return False

        self.webcam_frame_successful.inc()
        self.webcam.save_frame(frame, local_fn,
                                    self.config['webcam_time_prefix_string'])
        return self.upload_file(local_fn, self.config['webcam_dropbox_fn'])

    def do_weather(self):
        local_fn = self.config['weather_path'] + 'weather.png'
        try:
            web_screenshot.screenshot_to_file(self.config['weather_url'],
                                              local_fn)
        except Exception as e:  # pylint: disable=broad-except
            print(f"Failed to capture weather: {e}")
            self.weather_capture_failed.inc()
            return False

        self.weather_capture_successful.inc()
        return self.upload_file(local_fn, self.config['weather_dropbox_fn'])

    def upload_file(self, local_file, dropbox_file):
        """Uploads a file to Dropbox."""
        upload_ret = self.db.upload_file(local_file, dropbox_file)
        if upload_ret:
            print(f"Uploaded {local_file} to {dropbox_file}")
            self.upload_successful.inc()
            return True

        print(f"Failed to upload {local_file} to {dropbox_file}")
        self.upload_failed.inc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--time_delay", type=int,
                        help="Time delay between loops in seconds", default=60)
    args = parser.parse_args()
    wg = weather_updater()

    while True:
        print("doing webcam capture")
        wg.do_webcam()
        print("doing weather capture")
        wg.do_weather()
        time.sleep(args.time_delay)
