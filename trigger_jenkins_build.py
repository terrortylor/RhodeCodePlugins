# -*- coding: utf-8 -*-
"""
install requests using::

    pip install json
    pip install requests

config example::

    CONFIG = DotDict(
        jenkins=DotDict(

        ),
    )

    CONFIG.jenkins.default_config = {
        'JENKINS_URL' : 'http://dummy.jenkins.com:8080',
        'JENKINS_USERNAME' : '<username>',
        'JENKINS_PASSWORD' : '<token>',
        'JENKINS_JOB' : 'TestBuild'
    }

example use in hooks::

    call = load_extension('trigger_jenkins_build.py')
    if call:
        kwargs.update(CONFIG.jenkins.default_config)
        kwargs['JENKINS_REVISION'] = kwargs.get('source').get('reference').get('commit_id')
        kwargs['JENKINS_TARGET'] = kwargs['target']['repository']
        kwargs['JENKINS_SOURCE'] = kwargs['source']['repository']
        kwargs['JENKINS_PULL_REQUEST_ID'] = kwargs['pull_request_id']
        call(**kwargs)

"""
import json
import requests
import logging
import requests.packages.urllib3 as urllib3

def run(*args, **kwargs):
    from rhodecode.lib import helpers as h

    # URL of Jenkins instance
    URL_PATH = kwargs.pop('JENKINS_URL', None)

    # Jenkins username
    USERNAME = kwargs.pop('JENKINS_USERNAME', None)

    # Jenkins user password
    TOKEN = kwargs.pop("JENKINS_TOKEN", None)

    # Job to build
    JOB_NAME = kwargs.pop("JENKINS_JOB", None)

    # Revision to build from
    REVISION = kwargs.pop("JENKINS_REVISION", None)

    # Target repo
    TARGET_REPO = kwargs.pop("JENKINS_TARGET", None)

    # Source repo
    SOURCE_REPO = kwargs.pop("JENKINS_SOURCE", None)

    # Source repo
    PULL_REQUEST_ID = kwargs.pop("JENKINS_PULL_REQUEST_ID", None)

    params={"parameter": [
                {"name":"REVISION", "value":REVISION},
                {"name":"TARGET_REPO", "value":TARGET_REPO},
                {"name":"SOURCE_REPO", "value":SOURCE_REPO},
                {"name":"PULL_REQUEST_ID", "value":PULL_REQUEST_ID}
            ]
        }
    target = '%s/job/%s/build' % (URL_PATH, JOB_NAME)
    logging.info('Target URL: %s \nData: %s' % (target,params))

    data, content_type = urllib3.encode_multipart_formdata([
        ("json", json.dumps(params)),
        ("Submit", "Build"),
        ])

    r = requests.post(target, auth=(USERNAME, TOKEN), headers={"content-type": content_type}, data=data, verify=False)
    if(r.ok):
        logging.info('Jenkins job: %s has been kicked off with revision: %s' % (JOB_NAME, REVISION))
    else:
        logging.error('Unable to build Jenkins job: %s with revision: %s' % (JOB_NAME, REVISION))
        r.raise_for_status()
    return 0
