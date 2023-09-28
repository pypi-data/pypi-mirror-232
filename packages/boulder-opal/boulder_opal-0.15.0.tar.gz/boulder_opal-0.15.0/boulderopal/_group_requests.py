# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from typing import ContextManager

from qctrlcommons.exceptions import QctrlException
from qctrlworkflowclient import LocalRouter

from boulderopal._configuration import get_configuration


def group_requests() -> ContextManager:
    """
    Create a context manager for executing multiple function calls over available machines.

    Returns
    -------
    ContextManager
        A context manager to collect and run computation requests.

    Notes
    -----
    You can to group up to five requests together.
    All grouped calculations must be independent from each other.

    Within the context manager, the object returned from each request is a placeholder.
    When exiting, the context manager waits until all calculations have finished,
    hence this command blocks execution.
    When all results are received, the placeholders are replaced with them.

    Read the `Computational resources in Boulder Opal
    <https://docs.q-ctrl.com/boulder-opal/topics/computational-resources-in-boulder-opal>`_
    topic for more information about this feature.
    """
    router = get_configuration().get_router()
    if isinstance(router, LocalRouter):
        raise QctrlException("Grouping requests is not supported in local mode.")
    return router.enable_parallel()
