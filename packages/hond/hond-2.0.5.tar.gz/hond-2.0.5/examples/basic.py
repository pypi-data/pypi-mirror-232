# Copyright 2020 Clivern
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import sys
from hond.driver.elasticsearch import ElasticSearch
from hond.metric import Metric
from hond.hond import Hond
from hond.trigger import Trigger


def main():
    driver = ElasticSearch(["http://localhost:9200"], "metrics")
    hond = Hond(driver)

    if sys.argv[1] == "migrate":
        driver.migrate()

    if sys.argv[1] == "insert":
        m = input("Enter Metric:")

        while not m == "":
            items = m.split("=")

            metric = Metric(
                items[0],
                float(items[1]),
                {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"},
            )

            hond.insert(metric)

            m = input("Enter Metric:")

    if sys.argv[1] == "watch":
        t = input("Enter Trigger:")

        while True:
            trigger = Trigger(
                "trigger", t, {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"}
            )
            print("{} is {}".format(t, hond.evaluate(trigger)))
            time.sleep(10)

    # Imagine a check that reports CRITICAL, WARNING, OK, UNKNOWN
    # OK if m{hond.1625352.check_a==0}[60s]
    # CRITICAL if m{hond.1625352.check_a==2}[60s]
    # WARNING if m{hond.1625352.check_a==1}[60s]
    # UNKNOWN if m{hond.1625352.check_a==3}[60s]
    # MISSING if m{hond.1625352.check_a==nul}[60s]

    if sys.argv[1] == "demo_insert":
        m = input("Enter Metric:") # hond.1625352.check_a

        c = 1
        x = 0
        while not m == "":
            if c > 20:
                c = 1
            if x > 3:
                x = 0

            if c == 20:
                x += 1

            metric = Metric(
                m,
                float(x),
                {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"},
            )

            print(str(metric))
            hond.insert(metric)

            time.sleep(15)
            c += 1

    if sys.argv[1] == "demo_watch":
        t = input("Enter Metric:") # hond.1625352.check_a

        while True:
            ok_trigger = Trigger(
                "trigger",
                "m{" + t + "}==0}[60s]",
                {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"},
            )
            critical_trigger = Trigger(
                "trigger",
                "m{" + t + "}==2}[60s]",
                {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"},
            )
            warning_trigger = Trigger(
                "trigger",
                "m{" + t + "}==1}[60s]",
                {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"},
            )
            unknown_trigger = Trigger(
                "trigger",
                "m{" + t + "}==3}[60s]",
                {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"},
            )

            missing_trigger = Trigger(
                "trigger",
                "m{" + t + "}==nul}[60s]",
                {"agentId": "1bee4e3c-0976-44d9-bf4a-6432857e4f3c"},
            )

            ok_status = hond.evaluate(ok_trigger)
            critical_status = hond.evaluate(critical_trigger)
            warning_status = hond.evaluate(warning_trigger)
            unknown_status = hond.evaluate(unknown_trigger)
            missing_status = hond.evaluate(missing_trigger)

            if ok_status:
                print("State is OK")

            if critical_status:
                print("State is CRITICAL")

            if warning_status:
                print("State is WARNING")

            if unknown_status:
                print("State is UNKNOWN")

            if missing_status:
                print("State is MISSING")

            time.sleep(10)


if __name__ == "__main__":
    main()
