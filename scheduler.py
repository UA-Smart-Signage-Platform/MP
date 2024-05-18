from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY
import sched
import time
import threading
import utils
import os

class SchedulerRule:
    def __init__(self, start_hour, start_minute, end_hour, end_minute, start_date, end_date, priority, weekdays, template):
        self.start_hour = start_hour
        self.start_minute = start_minute
        self.end_hour = end_hour
        self.end_minute = end_minute
        self.start_date = start_date
        self.end_date = end_date
        self.priority = priority
        self.weekdays = weekdays
        self.template = template

    @property
    def start(self):
        start_date = self.start_date if self.start_date != "" and self.start_date > datetime.now() else ""
        start_rule = rrule(freq=DAILY, count=1, byhour=self.start_hour, byminute=self.start_minute, bysecond=0, byweekday=self.weekdays, dtstart=start_date, until=self.end_date)
        if start_rule.count() <= 0:
            return None

        if self.end < start_rule[0]:
            return start_rule[0] - timedelta(days=1)

        return start_rule[0]

    @property
    def end(self):
        start_date = self.start_date if self.start_date != "" and self.start_date > datetime.now() else ""
        end_rule = rrule(freq=DAILY, count=1, byhour=self.end_hour, byminute=self.end_minute, bysecond=0, byweekday=self.weekdays, dtstart=start_date, until=self.end_date)
        if end_rule.count() <= 0:
            return None

        return end_rule[0]

    @staticmethod
    def parse_rule(rule):
        
        schedule = rule["schedule"]

        start_time_parts = schedule['startTime'].split(':')
        start_hour = int(start_time_parts[0])
        start_minute = int(start_time_parts[1])

        end_time_parts = schedule['endTime'].split(':')
        end_hour = int(end_time_parts[0])
        end_minute = int(end_time_parts[1])

        start_date = schedule['startDate']
        end_date = schedule['endDate']

        if start_date != "":
            start_date = datetime.strptime(schedule['startDate'], '%Y-%m-%d')

        if end_date != "":
            end_date = datetime.strptime(schedule['endDate'], '%Y-%m-%d')

        new_rule = SchedulerRule(start_hour, start_minute, end_hour, end_minute,
                        start_date, end_date, schedule["priority"], schedule["weekdays"], rule["html"])

        if new_rule.start == None or new_rule.end == None:
            return None

        return new_rule

class Scheduler:

    def __init__(self, logger, config, window):
        self.logger = logger
        self.config = config
        self.window = window        

        self.current_template = None
        self.rules = None
        self.stop = False

    def set_rules(self, rules):
        self.rules = [SchedulerRule.parse_rule(rule) for rule in rules if SchedulerRule.parse_rule(rule) is not None]
        self.stop = True

    def main_loop(self):

        while self.rules == None:
            time.sleep(1)

        self.stop = False

        # step 1 - display the current rule
        self.display(self.get_current_rule())

        # this sleep is to "fix" problems with rrule giving old values
        # time.sleep(1)

        # step 2 - sleep until next iteration
        next_iteration_timestamp = self.get_next_iteration_timestamp()
        if next_iteration_timestamp is not None:
            self.logger.info(f"Next Iteration at {datetime.fromtimestamp(next_iteration_timestamp)}")
            while self.stop == False and time.time() < next_iteration_timestamp:
                time.sleep(1)
            self.main_loop()
        else:
            self.logger.info("No More Rules")

    def get_current_rule(self):
        current_rule = None
        current_time = time.time()

        for rule in self.rules:
            if current_time > rule.end.timestamp() or current_time < rule.start.timestamp():
                continue

            if current_rule == None or rule.priority < current_rule.priority:
                current_rule = rule

        return current_rule

    def get_next_iteration_timestamp(self):
        next_iteration_timestamp = None
        current_time = time.time()

        for rule in self.rules:
            for timestamp in [rule.start.timestamp(), rule.end.timestamp()]:

                if timestamp < current_time:
                    continue

                if next_iteration_timestamp == None or current_time < timestamp < next_iteration_timestamp:
                    next_iteration_timestamp = timestamp
        
        return next_iteration_timestamp

    def display(self, rule):
        if rule == None:
            if self.config.getboolean('MediaPlayer', 'savings_mode'):
                self.logger.info("No Rule to be Displayed. Blanking Screen")
                os.system("xset dpms force off")
            else:
                self.logger.info("No Rule to be Displayed. Displaying Default Template")
                self.window.load_url(self.config["MediaPlayer"]["default_template"])
            
            self.current_template = None
        else:
            if self.config.getboolean('MediaPlayer', 'savings_mode'):
                os.system("xset dpms force on")
            self.logger.info(f"Displaying Template for Rule [{rule.start}]-[{rule.end}]")
            if self.current_template != rule.template: 
                self.current_template = rule.template
                utils.store_static("current.html", rule.template)
                self.window.load_url(utils.get_full_path("static/current.html"))