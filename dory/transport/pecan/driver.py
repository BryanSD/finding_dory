# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from wsgiref import simple_server

import pecan
from oslo.config import cfg

from dory.openstack.common import log
from dory import transport
from dory.transport.pecan import controllers
from dory.transport.pecan import hooks


_PECAN_OPTIONS = [
    cfg.StrOpt('bind', default='127.0.0.1',
               help='Address on which the self-hosting server will listen'),
    cfg.IntOpt('port', default=8888,
               help='Port on which the self-hosting server will listen'),
]

_PECAN_GROUP = 'drivers:transport:pecan'

LOG = log.getLogger(__name__)


class PecanTransportDriver(transport.Driver):

    def __init__(self, conf, manager):
        super(PecanTransportDriver, self).__init__(conf, manager)

        self._conf.register_opts(_PECAN_OPTIONS, group=_PECAN_GROUP)
        self._pecan_conf = self._conf[_PECAN_GROUP]

        self._setup_app()

    def _setup_app(self):
        root_controller = controllers.Root(self)

        pecan_hooks = [hooks.Context()]

        self._app = pecan.make_app(root_controller, hooks=pecan_hooks)

        v1_controller = controllers.V1(self)
        root_controller.add_controller('v1', v1_controller)

        todos_controller = controllers.Todos(self)
        v1_controller.add_controller('todos', todos_controller)

    def listen(self):
        LOG.info(
            'Serving on host %(bind)s:%(port)s',
            {
                'bind': self._pecan_conf.bind,
                'port': self._pecan_conf.port,
            },
        )

        httpd = simple_server.make_server(self._pecan_conf.bind,
                                          self._pecan_conf.port,
                                          self.app)
        httpd.serve_forever()
