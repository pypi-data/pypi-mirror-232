# Copyright 2020 Adap GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Flower ClientManager."""


import random
import threading
from abc import ABC, abstractmethod
from logging import INFO
from typing import Dict, List, Optional, Callable

from daisyfl.common.logger import log
from daisyfl.common import CREDENTIAL, IS_ZONE

from .client_proxy import ClientProxy
from .criterion import Criterion
import time

class ClientManager(ABC):
    """Abstract base class for managing Flower clients."""

    @abstractmethod
    def num_available(self) -> int:
        """Return the number of available clients."""

    @abstractmethod
    def register(self, client: ClientProxy) -> bool:
        """Register Flower ClientProxy instance.

        Returns:
            bool: Indicating if registration was successful
        """

    @abstractmethod
    def unregister(self, client: ClientProxy) -> None:
        """Unregister Flower ClientProxy instance."""

    @abstractmethod
    def unregister_all(self,) -> None:
        """Unregister all Flower ClientProxy instances."""
    
    @abstractmethod
    def all(self) -> Dict[str, ClientProxy]:
        """Return all available clients."""

    @abstractmethod
    def wait_for(self, num_clients: int, timeout: int) -> bool:
        """Wait until at least `num_clients` are available."""

    @abstractmethod
    def sample(
        self,
        num_clients: int,
        min_num_clients: Optional[int] = None,
        credential: Optional[str] = None,
        criterion: Optional[Criterion] = None,
    ) -> List[ClientProxy]:
        """get all available Daisy ClientProxy instances."""

    @abstractmethod
    def get_clients_from_list(
        self,
        clients: List[ClientProxy],
        timeout: float,
    ) -> List[ClientProxy]:
        """get available clients from a list after a given number of seconds."""

    @abstractmethod
    def set_submit_subtask_fn(self, submit_subtask: Callable) -> None:
        """
        Server sets this callback function.
        ClientProxy calls this callback function to submit a result.
        """
    
    @abstractmethod
    def set_check_waiting_fn(self, check_waiting: Callable) -> None:
        """
        Server sets this callback function.
        ClientProxy calls this callback function to check if server is waiting for it.
        """

    @abstractmethod
    def set_client_fail_fn(self, client_fail: Callable) -> None:
        """
        Server sets this callback function.
        ClientProxy calls this callback function to notify server it failed.
        """
    
    @abstractmethod
    def set_client_roam_fn(self, client_roam: Callable) -> None:
        """
        Server sets this callback function.
        ClientProxy calls this callback function to notify client roamed into another edge.
        """


class SimpleClientManager(ClientManager):
    """Provides a pool of available clients."""

    def __init__(self) -> None:
        self.zones: Dict[str, ClientProxy] = {}
        self.clients: Dict[str, Dict[str, ClientProxy]] = {}
        self._cv = threading.Condition()
        self.submit_subtask: Callable = None

    def __len__(self,) -> int:
        count = 0
        for key in self.clients.keys():
            count = count + len(self.clients[key])
        count = count + len(self.zones)
        return count

    def wait_for(self, num_clients: int, credential: Optional[str], timeout: int = 86400) -> bool:
        """Block until at least `num_clients` are available or until a timeout
        is reached.

        Current timeout default: 1 day.
        """
        with self._cv:
            return self._cv.wait_for(
                lambda: self.num_available(credential) >= num_clients, timeout=timeout
            )

    def num_available(self, credential: Optional[str]) -> int:
        """Return the number of available clients."""
        if credential is None:
            return len(self.zones.values())
        
        if not self.clients.__contains__(credential):
            self.clients[credential] = {}

        nums = 0
        for client in self.clients[credential].values():
            if client.bridge.client_available():
                nums = nums + 1
        for client in self.zones.values():
            if client.bridge.client_available():
                nums = nums + 1
        return nums

    def register(self, client: ClientProxy, is_zone: bool) -> bool:
        """Register Flower ClientProxy instance.

        Returns:
            bool: Indicating if registration was successful. False if ClientProxy is
                already registered or can not be registered for any reason
        """
        # check cid
        for credential_key in self.clients:
            if client.cid in self.clients[credential_key].keys():
                return False
        if client.cid in self.zones.keys():
            return False
        client.set_submit_subtask_fn(self.submit_subtask)
        client.set_check_waiting_fn(self.check_waiting)
        client.set_client_fail_fn(self.client_fail)
        client.set_client_roam_fn(self.client_roam)
        # register a zone
        if is_zone:
            self.zones[client.cid] = client
        else:
            credential = client.metadata_dict[CREDENTIAL]
            if not self.clients.__contains__(credential):
                self.clients[credential] = {}
            self.clients[credential][client.cid] = client
        
        with self._cv:
            self._cv.notify_all()

        return True

    def unregister(self, client: ClientProxy) -> None:
        """Unregister Flower ClientProxy instance.

        This method is idempotent.
        """
        if self.zones.__contains__(client.cid):
            del self.zones[client.cid]
        for credential_key in self.clients.keys():
            if self.clients[credential_key].__contains__(client.cid):
                del self.clients[credential_key][client.cid]

        with self._cv:
            self._cv.notify_all()

    def unregister_all(self,) -> None:
        clients = self.all()
        for client in clients:
            client.bridge.close()
            self.unregister(client)

    def all(self) -> List[ClientProxy]:
        """Return all available clients."""
        def get_values(d):
            values = []
            for v in d.values():
                if isinstance(v, dict):
                    values.extend(get_values(v))
                else:
                    values.append(v)
            return values
        
        client_list = get_values(self.clients)
        client_list = client_list + list(self.zones.values())
        return client_list

    def sample(
        self,
        num_clients: int,
        min_num_clients: Optional[int] = None,
        credential: Optional[str] = None,
        criterion: Optional[Criterion] = None,
    ) -> List[ClientProxy]:
        """Sample a number of Flower ClientProxy instances."""
        # Block until at least num_clients are connected.
        if min_num_clients is None:
            min_num_clients = num_clients
        self.wait_for(min_num_clients, credential)

        if credential is None:
            return list(self.zones.values())
        
        # Sample clients which meet the criterion
        
        client_list = []
        available_clients = list(self.clients[credential].values())
        for client in available_clients:
            if client.bridge.client_available():
                if criterion is not None:
                    if criterion.select(client):
                        client_list.append(client)
                else:
                    client_list.append(client)
        available_zones = list(self.zones.values())
        for zone_client in available_zones:
            if zone_client.bridge.client_available():
                client_list.append(zone_client)
        
        if num_clients > len(client_list):
            log(
                INFO,
                "Sampling failed: number of available clients"
                " (%s) is less than number of requested clients (%s).",
                len(client_list),
                num_clients,
            )
            return []

        sampled_clients = random.sample(client_list, num_clients)
        return sampled_clients
    
    def get_clients_from_list(
        self,
        clients: List[ClientProxy],
        timeout: float,
        credential: str,
    ) -> List[ClientProxy]:
        time.sleep(timeout)
        ids = []
        for client in clients:
            ids.append(client.cid)
        client_list = []
        for client in self.clients[credential].values():
            if (client.cid in ids) and (client.bridge.client_available()):
                client_list.append(client)
        for client in self.zones.values():
            if (client.cid in ids) and (client.bridge.client_available()):
                client_list.append(client)
        return client_list
    
    def set_submit_subtask_fn(self, submit_subtask: Callable) -> None:
        self.submit_subtask = submit_subtask

    def set_check_waiting_fn(self, check_waiting: Callable) -> None:
        self.check_waiting = check_waiting

    def set_client_fail_fn(self, client_fail: Callable) -> None:
        self.client_fail = client_fail

    def set_client_roam_fn(self, client_roam: Callable) -> None:
        self.client_roam = client_roam
