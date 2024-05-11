from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY
import sched
import time
import threading
import utils

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
                        start_date, end_date, schedule["priority"], schedule["weekdays"], rule["template"])

        if new_rule.start == None or new_rule.end == None:
            return None

        return new_rule

class Scheduler:

    def __init__(self, window, rules):
        self.window = window
        self.rules = [SchedulerRule.parse_rule(rule) for rule in rules if SchedulerRule.parse_rule(rule) is not None]
        self.current_template = None

    def main_loop(self):

        # step 1 - get the current rule

        current_rule = None
        current_time = time.time()

        for rule in self.rules:
            #print(rule.start, rule.end)
            if current_time > rule.end.timestamp() or current_time < rule.start.timestamp():
                continue

            if current_rule == None or rule.priority < current_rule.priority:
                current_rule = rule

        if current_rule == None:
            print("nothing!")
            self.current_template = None
        else:
            print("displaying task", current_rule.start, current_rule.end)
            if self.current_template != current_rule.template: 
                self.current_template = current_rule.template
                utils.store_static("current.html", current_rule.template)
                self.window.load_url(utils.get_full_path("static/current.html"))

        # step 2 - schedule next iteration
        time.sleep(5)
        next_iteration_timestamp = None

        for rule in self.rules:
            for timestamp in [rule.start.timestamp(), rule.end.timestamp()]:

                if timestamp < current_time:
                    continue

                if next_iteration_timestamp == None or current_time < timestamp < next_iteration_timestamp:
                    next_iteration_timestamp = timestamp

        if next_iteration_timestamp is not None:
            delay = next_iteration_timestamp - current_time
            print("next task at", datetime.fromtimestamp(next_iteration_timestamp))
            time.sleep(delay)
            self.main_loop()
        else:
            print("No more scheduled tasks.")
