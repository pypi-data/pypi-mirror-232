# MIT License
#
# Copyright (c) 2021 Clivern
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import time

from hond.logger import Logger
from elasticsearch import Elasticsearch


class ElasticSearch:
    """
    ElasticSearch Driver Class
    """

    def __init__(self, nodes, index_name, ca_certs=None, username=None, password=None):
        """Inits elasticsearch"""
        self.logger = Logger().get_logger(__name__)
        self.index_name = index_name

        if ca_certs is not None and username is not None and password is not None:
            self.client = Elasticsearch(
                nodes, ca_certs=ca_certs, basic_auth=(username, password)
            )

        elif ca_certs is not None:
            self.client = Elasticsearch(
                nodes,
                ca_certs=ca_certs,
            )

        elif username is not None and password is not None:
            self.client = Elasticsearch(nodes, basic_auth=(username, password))

        else:
            self.client = Elasticsearch(nodes)

    def get_client(self):
        """
        Get elasticsearch client

        Returns:
            a dict of client info
        """
        return self.client.info()

    def migrate(self, shards=1, replicas=1):
        """
        Create metric index
        """
        doc = {
            "settings": {"number_of_shards": shards, "number_of_replicas": replicas},
            "mappings": {
                "properties": {
                    "id": {"type": "text"},
                    "name": {"type": "text"},
                    "value": {"type": "float"},
                    "timestamp": {"type": "long"},
                    "meta": {"type": "object"},
                }
            },
        }

        response = self.client.index(index=self.index_name, document=doc)

        return response

    def insert(self, metric):
        """
        Insert metrics into elastic search
        """
        doc = {
            "id": metric.id,
            "name": metric.name,
            "value": metric.value,
            "timestamp": metric.timestamp,
            "meta": metric.meta,
        }

        self.logger.debug("Insert metric into elasticsearch: {}", str(metric))

        response = self.client.index(index=self.index_name, document=doc)

        return response

    def is_absent(self, metric_name, for_in_sec=60):
        """
        Check if the metric is absent for x seconds
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response = self.search(query)

        return (
            response["hits"]["total"]["value"] == 0
            and len(response["hits"]["hits"]) == 0
        )

    def equal(self, metric_name, benchmark, for_in_sec=60):
        """
        Check if the metric is equal to the benchmark for x seconds
        """
        query1 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response1 = self.search(query1)

        # If no hits have been found
        if response1["hits"]["total"]["value"] == 0:
            return False

        query2 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {"match_phrase": {"value": {"query": benchmark}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response2 = self.search(query2)

        return (
            response1["hits"]["total"]["value"] == response2["hits"]["total"]["value"]
        )

    def above(self, metric_name, benchmark, for_in_sec=60):
        """
        Check if the metric is above the benchmark for x seconds
        """
        query1 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response1 = self.search(query1)

        # If no hits have been found
        if response1["hits"]["total"]["value"] == 0:
            return False

        query2 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {"range": {"value": {"gt": benchmark}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response2 = self.search(query2)

        return (
            response1["hits"]["total"]["value"] == response2["hits"]["total"]["value"]
        )

    def below(self, metric_name, benchmark, for_in_sec=60):
        """
        Check if the metric is below the benchmark for x seconds
        """
        query1 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response1 = self.search(query1)

        # If no hits have been found
        if response1["hits"]["total"]["value"] == 0:
            return False

        query2 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {"range": {"value": {"lt": benchmark}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response2 = self.search(query2)

        return (
            response1["hits"]["total"]["value"] == response2["hits"]["total"]["value"]
        )

    def above_equal(self, metric_name, benchmark, for_in_sec=60):
        """
        Check if the metric is above or equal the benchmark for x seconds
        """
        query1 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response1 = self.search(query1)

        # If no hits have been found
        if response1["hits"]["total"]["value"] == 0:
            return False

        query2 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {"range": {"value": {"gte": benchmark}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response2 = self.search(query2)

        return (
            response1["hits"]["total"]["value"] == response2["hits"]["total"]["value"]
        )

    def below_equal(self, metric_name, benchmark, for_in_sec=60):
        """
        Check if the metric is below or equal the benchmark for x seconds
        """
        query1 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response1 = self.search(query1)

        # If no hits have been found
        if response1["hits"]["total"]["value"] == 0:
            return False

        query2 = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"name": {"query": metric_name}}},
                        {"range": {"value": {"lte": benchmark}}},
                        {
                            "range": {
                                "timestamp": {"gte": int(time.time()) - for_in_sec}
                            }
                        },
                    ]
                }
            }
        }

        response2 = self.search(query2)

        return (
            response1["hits"]["total"]["value"] == response2["hits"]["total"]["value"]
        )

    def search(self, query):
        """
        Query elasticsearch index
        """
        return self.client.search(index=self.index_name, body=query)

    def evaluate(self, expression):
        """
        Evaluate a trigger value

        Examples:
            m{customers.123.456.789.cpu>=20}[30s]
            m{customers.123.456.789.cpu<20}[30s]
            m{customers.123.456.789.cpu==nul}[30s]
            m{customers.123.456.789.cpu==nul}[30s] and m{customers.123.456.789.mem==nul}[30s]

        TODO: switch to safer way other than eval but right now triggers is not a user input
        """
        result = []
        expressions = re.split(" and | or ", expression)

        for exp in expressions:
            pattern = r"^(m)\{(.*)\}(\[(.*)s\])?$"
            match = re.match(pattern, exp)
            if match:
                items = re.split(">=|<=|==|>|<", match.group(2))

                if items[1] == "nul":
                    metric_name = items[0]

                    try:
                        for_in_sec = int(match.group(4))
                    except Exception:
                        raise Exception("Invalid expression: {}".format(exp))

                    value = self.is_absent(metric_name, for_in_sec)
                else:
                    metric_name = items[0]

                    try:
                        benchmark = float(items[1])
                        for_in_sec = int(match.group(4))
                    except Exception:
                        raise Exception("Invalid expression: {}".format(exp))

                    if "==" in match.group(2):
                        value = self.equal(metric_name, benchmark, for_in_sec)
                    elif ">=" in match.group(2):
                        value = self.above_equal(metric_name, benchmark, for_in_sec)
                    elif "<=" in match.group(2):
                        value = self.below_equal(metric_name, benchmark, for_in_sec)
                    elif ">" in match.group(2):
                        value = self.above(metric_name, benchmark, for_in_sec)
                    elif "<" in match.group(2):
                        value = self.below(metric_name, benchmark, for_in_sec)

                if value:
                    result.append("True")
                else:
                    result.append("False")
            else:
                raise Exception("Invalid expression: {}".format(exp))

        out = expression

        for i in range(len(expressions)):
            out = out.replace(expressions[i], result[i])

        return eval(out)
