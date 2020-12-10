# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: test
    plugin_type: inventory
    short_description: test inventory source
    extends_documentation_fragment:
        - inventory_cache
'''

from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable


class InventoryModule(BaseInventoryPlugin, Cacheable):

    NAME = 'test'

    def populate(self, hosts):
        for host in list(hosts.keys()):
            self.inventory.add_host(host, group='all')
            for hostvar, hostval in hosts[host].items():
                self.inventory.set_variable(host, hostvar, hostval)

    def get_hosts(self):
        return {'host1': {'one': 'two'}, 'host2': {'three': 'four'}}

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        self.load_cache_plugin()

        cache_key = self.get_cache_key(path)

        # cache may be True or False at this point to indicate if the inventory is being refreshed
        # get the user's cache option
        cache_setting = self.get_option('cache')

        attempt_to_read_cache = cache_setting and cache
        cache_needs_update = cache_setting and not cache

        # attempt to read the cache if inventory isn't being refreshed and the user has caching enabled
        if attempt_to_read_cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                # This occurs if the cache_key is not in the cache or if the cache_key expired, so the cache needs to be updated
                cache_needs_update = True

        if cache_needs_update:
            results = self.get_hosts()

            # set the cache
            self._cache[cache_key] = results

        self.populate(results)
