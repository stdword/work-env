#!/usr/bin/env python

import re
from copy import deepcopy
from collections import OrderedDict

import requests


COOKIES = """INSERT COOKIES HERE"""
SPRINT_VALUE = 67
NEXT_SPRINT_VALUE = 68
IGNORE_ISSUES = []


BASE_URL = 'https://<company>.atlassian.net'


class JiraSprint(object):
    """
    Example: "com.atlassian.greenhopper.service.sprint.Sprint@52f26b53[id=67,rapidViewId=8,state=CLOSED,name=KEY 22,goal=Feature redesign,startDate=2018-07-10T11:07:30.501Z,endDate=2018-08-07T11:07:00.000Z,completeDate=2018-08-22T08:12:40.708Z,sequence=71]"
    """

    def __init__(self, item):
        self._item = item

    def __repr__(self):
        return 'JiraSprint(id={}, name="{}")'.format(self.id, self.name)

    @property
    def id(self):
        match = re.search(r'id="?(.*?)[,\]"]', self._item)
        return match.group(1)

    @property
    def name(self):
        match = re.search(r'name="?(.*?)[,\]"]', self._item)
        return match.group(1)


class JiraIssue(object):
    def __init__(self, item):
        self._item = item

    def __repr__(self):
        return 'JiraIssue(key="{}", type="{}")'.format(self.key, self.type)

    @property
    def url(self):
        return '{}/browse/{}'.format(BASE_URL, self.key)

    @property
    def key(self):
        return self._item['key']

    @property
    def type(self):
        return self._item['fields']['issuetype']['name']

    @property
    def story_points(self):
        return self._item['fields']['customfield_10008']

    @property
    def sprints(self):
        return sorted(JiraSprint(item) for item in self._item['fields']['customfield_10003'])

    @property
    def components(self):
        return sorted(item['name'] for item in self._item['fields']['components'])

    @property
    def status(self):
        return self._item['fields']['status']['name']

    @property
    def seconds_spent(self):
        return self._item['fields']['timespent']


class JiraClient(object):
    API_URL = '{}/rest/api/2/search'.format(BASE_URL)

    def __init__(self, cookies):
        self.cookies = cookies

    def _request(self, jql, start_at, max_results):
        params = {
            'jql': jql,
            'maxResults': max_results,
            'startAt': start_at,
        }
        headers = {'Cookie': self.cookies}

        try:
            response = requests.get(self.API_URL, params=params, headers=headers)
        except Exception as e:
            print 'ERROR: Network problem:', e
            return None

        return response

    def jql(self, jql, start_at=0, max_results=100):
        response = self._request(jql, start_at, max_results)
        if not response.ok:
            print 'ERROR: Bad request:', response.content
            return None

        return response.json()

    def get_issues(self, jql):
        data = []
        start_at = 0
        max_results = 100
        while True:
            print 'Jira request...'
            response = self.jql(jql, start_at, max_results)
            if response is None:
                break

            data.extend(response['issues'])

            total = response['total']
            if total <= (start_at + max_results):
                break

            start_at += max_results

        return [JiraIssue(item) for item in data]


class JiraStatService(object):
    backend_component = 'Backend'
    frontend_component = 'Frontend'

    time_adjustment_k = 1.10

    def __init__(self, jira_client, sprint, next_sprint, ignore_issues):
        self.client = jira_client
        self.sprint = sprint
        self.next_sprint = next_sprint
        self.ignore_issues = ignore_issues

    def bugs_stat(self):
        stat_front = {
            'bugs+support': {
                'count': 0,
                'work_time': 0,
            },
            'burned': 0,
        }
        stat_back = deepcopy(stat_front)

        result_stat = {
            self.backend_component: stat_back,
            self.frontend_component: stat_front,
        }

        jql = (
            'Sprint = {} and Sprint != {} and issueType in (Bug, Improvement, "Support Request", Task)'
            .format(self.sprint, self.next_sprint)
        )
        issues = self.client.get_issues(jql)
        for issue in issues:
            if issue.key in self.ignore_issues:
                continue

            components = [c for c in issue.components if c in (self.backend_component, self.frontend_component)]
            if self.backend_component in components and self.frontend_component in components:
                print 'WARNING: both components:', issue.url
                continue

            if self.backend_component not in components and self.frontend_component not in components:
                print 'WARNING: no one of components:', issue.url
                continue

            if issue.story_points is None and (issue.seconds_spent is None or issue.seconds_spent == 0):
                print 'WARNING: no stat for', issue.url
                continue

            if issue.status not in ('QA: todo', 'Done'):
                print 'WARNING: bad status "{}" for'.format(issue.status), issue.url
                continue

            stat = result_stat[components[0]]

            if issue.type in ('Bug', 'Support Request'):
                support_stat = stat['bugs+support']

                support_stat['count'] += 1

                if issue.story_points is None:
                    support_stat['work_time'] += issue.seconds_spent * self.time_adjustment_k

            if issue.story_points is not None:
                stat['burned'] += issue.story_points

        return result_stat


def print_stat(stat, key):
    stat = stat[key]

    print '{}:'.format(key)
    print '\tBugs and support count: {}'.format(stat['bugs+support']['count'])
    print '\tBugs and support time: {}h'.format(round(stat['bugs+support']['work_time'] / 60.0 / 60), 2)
    print '\tBurned: {} points'.format(stat['burned'])
    print


def main():
    jira_client = JiraClient(COOKIES)
    service = JiraStatService(jira_client, SPRINT_VALUE, NEXT_SPRINT_VALUE, IGNORE_ISSUES)
    stat = service.bugs_stat()

    print_stat(stat, JiraStatService.frontend_component)
    print_stat(stat, JiraStatService.backend_component)


#####################


main()
