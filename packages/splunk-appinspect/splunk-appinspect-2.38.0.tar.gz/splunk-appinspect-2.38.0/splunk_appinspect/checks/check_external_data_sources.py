# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Calls to external data sources
"""
import logging

import splunk_appinspect
from splunk_appinspect.constants import Tags

logger = logging.getLogger(__name__)
report_display_order = 12


@splunk_appinspect.tags(Tags.SPLUNK_APPINSPECT, Tags.MANUAL, Tags.APPAPPROVAL)
@splunk_appinspect.cert_version(min="1.0.0")
def check_external_data_sources(reporter):
    """Check that all external data sources are explained in the app's
    documentation.
    """
    reporter.manual_check("Documentation will be read during code review.")
