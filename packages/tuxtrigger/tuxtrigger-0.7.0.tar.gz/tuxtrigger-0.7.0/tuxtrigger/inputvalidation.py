#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Dict, List, Optional

from urllib.parse import urlparse


class Base:
    def url_validation(self, url):
        urlScheme = urlparse(url)
        if urlScheme.scheme not in ["http", "https"]:
            raise TypeError("Invalid url input.")

    def url_path(self):
        return urlparse(self.url.rstrip("/"))


@dataclass
class YamlValidator(Base):
    url: str
    squad_group: str
    branches: List[Dict]
    regex: Optional[str] = None
    default_plan: Optional[str] = None
    squad_project_prefix: Optional[str] = None
    default_squad_project: Optional[str] = None
    lava_test_plans_project: Optional[str] = None
    lab: Optional[str] = None

    def __post_init__(self):
        self.url_validation(self.url)
