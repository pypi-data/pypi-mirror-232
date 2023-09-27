# Copyright 2012 Hewlett-Packard Development Company, L.P.
# Copyright 2023 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import voluptuous as v
from zuul.trigger import BaseTrigger
from zuul.driver.gerrit.gerritmodel import GerritEventFilter
from zuul.driver.gerrit import gerritsource
from zuul.driver.util import scalar_or_list, to_list, make_regex, ZUUL_REGEX
from zuul.configloader import DeprecationWarning


class GerritRequireApprovalDeprecation(DeprecationWarning):
    zuul_error_name = 'Gerrit require-approval Deprecation'
    zuul_error_message = """The 'require-approval' trigger attribute
is deprecated.  Use 'require' instead."""


class GerritRejectApprovalDeprecation(DeprecationWarning):
    zuul_error_name = 'Gerrit reject-approval Deprecation'
    zuul_error_message = """The 'reject-approval' trigger attribute
is deprecated.  Use 'reject' instead."""


class GerritTrigger(BaseTrigger):
    name = 'gerrit'
    log = logging.getLogger("zuul.GerritTrigger")

    def getEventFilters(self, connection_name, trigger_conf,
                        error_accumulator):
        efilters = []
        for trigger in to_list(trigger_conf):
            approvals = {}
            for approval_dict in to_list(trigger.get('approval')):
                for key, val in approval_dict.items():
                    approvals[key] = val
            # Backwards compat for *_filter versions of these args
            comments = to_list(trigger.get('comment'))
            if not comments:
                comments = to_list(trigger.get('comment_filter'))
            emails = to_list(trigger.get('email'))
            if not emails:
                emails = to_list(trigger.get('email_filter'))
            usernames = to_list(trigger.get('username'))
            if not usernames:
                usernames = to_list(trigger.get('username_filter'))
            ignore_deletes = trigger.get('ignore-deletes', True)
            if 'require-approval' in trigger:
                error_accumulator.addError(
                    GerritRequireApprovalDeprecation())
            if 'reject-approval' in trigger:
                error_accumulator.addError(
                    GerritRejectApprovalDeprecation())

            types = [make_regex(x, error_accumulator)
                     for x in to_list(trigger['event'])]
            branches = [make_regex(x, error_accumulator)
                        for x in to_list(trigger.get('branch'))]
            refs = [make_regex(x, error_accumulator)
                    for x in to_list(trigger.get('ref'))]
            comments = [make_regex(x, error_accumulator) for x in comments]
            emails = [make_regex(x, error_accumulator) for x in emails]
            usernames = [make_regex(x, error_accumulator) for x in usernames]

            f = GerritEventFilter(
                connection_name=connection_name,
                trigger=self,
                types=types,
                branches=branches,
                refs=refs,
                event_approvals=approvals,
                comments=comments,
                emails=emails,
                usernames=usernames,
                required_approvals=(
                    to_list(trigger.get('require-approval'))
                ),
                reject_approvals=to_list(
                    trigger.get('reject-approval')
                ),
                uuid=trigger.get('uuid'),
                scheme=trigger.get('scheme'),
                ignore_deletes=ignore_deletes,
                require=trigger.get('require'),
                reject=trigger.get('reject'),
                error_accumulator=error_accumulator,
            )
            efilters.append(f)

        return efilters


def getSchema():
    variable_dict = v.Schema(dict)

    approval = v.Schema({'username': str,
                         'email': str,
                         'older-than': str,
                         'newer-than': str,
                         }, extra=v.ALLOW_EXTRA)

    gerrit_trigger = {
        v.Required('event'):
            scalar_or_list(v.Any('patchset-created',
                                 'draft-published',
                                 'change-abandoned',
                                 'change-restored',
                                 'change-merged',
                                 'comment-added',
                                 'ref-updated',
                                 'pending-check',
                                 'vote-deleted',
                                 'wip-state-changed')),
        'uuid': str,
        'scheme': str,
        'comment_filter': scalar_or_list(str),
        'comment': scalar_or_list(v.Any(ZUUL_REGEX, str)),
        'email_filter': scalar_or_list(str),
        'email': scalar_or_list(v.Any(ZUUL_REGEX, str)),
        'username_filter': scalar_or_list(str),
        'username': scalar_or_list(v.Any(ZUUL_REGEX, str)),
        'branch': scalar_or_list(v.Any(ZUUL_REGEX, str)),
        'ref': scalar_or_list(v.Any(ZUUL_REGEX, str)),
        'ignore-deletes': bool,
        'approval': scalar_or_list(variable_dict),
        'require-approval': scalar_or_list(approval),
        'reject-approval': scalar_or_list(approval),
        'require': gerritsource.getRequireSchema(),
        'reject': gerritsource.getRejectSchema(),
    }

    return gerrit_trigger
