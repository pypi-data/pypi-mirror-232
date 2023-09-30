# Copyright 2018 Databricks, Inc.
import re

# VERSION = "2.7.2.dev0"
VERSION = "2.8.3"


def is_release_version():
    return bool(re.match(r"^\d+\.\d+\.\d+$", VERSION))
