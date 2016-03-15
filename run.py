#!/usr/bin/env python

import datetime
import time
import yaml
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s lineno=%(lineno)s %(message)s')
project_root = Path(__file__).absolute().parent
log_dir = Path(project_root, 'log')

if __name__ == "__main__":
    with Path(project_root, 'config.yml').open() as f:
        config = yaml.load(f)
    interval = datetime.timedelta(seconds=config['interval'])
    next_run_utctime = datetime.datetime.utcnow()
    
    while True:
        while datetime.datetime.utcnow() < next_run_utctime:
            time.sleep(10)

        if not log_dir.is_dir():
            log_dir.mkdir()
        next_run_utctime = datetime.datetime.utcnow() + interval
        logging.info('Start crawling')
        for spider_name, source_list in config['sources'].items():
            command = 'scrapy crawl {0} --logfile log/{0}-{1}'.format(spider_name, time.time())
            logging.info('Invoke command `{}`'.format(command))
            return_code = subprocess.call(command.split())
            if return_code != 0:
                logging.error("Received abnormal return code {}".format(return_code))
        logging.info('End crawling. Next crawl time (utc): {}'.format(next_run_utctime))
