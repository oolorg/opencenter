#!/usr/bin/env python
#               OpenCenter(TM) is Copyright 2013 by Rackspace US, Inc.
##############################################################################
#
# OpenCenter is licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  This
# version of OpenCenter includes Rackspace trademarks and logos, and in
# accordance with Section 6 of the License, the provision of commercial
# support services in conjunction with a version of OpenCenter which includes
# Rackspace trademarks and logos is prohibited.  OpenCenter source code and
# details are available at: # https://github.com/rcbops/opencenter or upon
# written request.
#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0 and a copy, including this
# notice, is available in the LICENSE file accompanying this software.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the # specific language governing permissions and limitations
# under the License.
#
##############################################################################

import opencenter
import string
#for_neutron
import os
import json
#for_neutron
#add backup
import svbk_manager
#add backup
# sdn set
import psset_manager
# sdn set
import logging

# sdn
NOVA_CLUSTER_SW='SDN Boxes'

class NovaBackend(opencenter.backends.Backend):
    def __init__(self):
        super(NovaBackend, self).__init__(__file__)

    def additional_constraints(self, api, node_id, action, ns):
        return []

    #tenant start
    #def _make_subcontainer(self, api, name, parent_id, facts, backends,
    #                       attrs=None):
    def _make_subcontainer(self, api, name, parent_id, facts, backends,
                           attrs=None, tenant=None):
    #tenant end
        logging.debug('NovaBackend:_make_subcontainer')
        subcontainer = api._model_create('nodes', {'name': name})
        if subcontainer is None:
            return None
        if attrs is None:
            attrs = {}
        if facts is None:
            facts = {}

        facts.update({'parent_id': parent_id,
                      'backends': backends})
        data = {}
        data['facts'] = facts
        data['attrs'] = attrs

        #tenant(add attr) start
        if tenant is not None:
            #data['facts']['tenant'] = tenant
            data['attrs']['tenant'] = tenant
        #tenant(add attr) end

        for t in ['facts', 'attrs']:
            for k, v in data[t].items():
                d = {'key': k,
                     'value': v,
                     'node_id': subcontainer['id']}
                api._model_create(t, d)

        return subcontainer

    def create_az(self, state_data, api, node_id, **kwargs):
        # self.logger.debug('NovaBackend:create_az') 
        if not 'az_name' in kwargs:
            return self._fail(msg='AZ Name is required')

        valid = string.letters + string.digits + "_"
        test_valid = all([c in valid for c in kwargs['az_name']])
        if not test_valid:
            return self._fail(msg='Name cannot contain spaces or special'
                                  'characters')
        r = api.nodes_query('(facts.parent_id = %s) and '
                            '(facts.nova_az = "%s")' % (
                                node_id, kwargs['az_name']))
        if len(r) > 0:
            return self._fail(msg='AZ Name should be unique within a cluster.')
        self._make_subcontainer(api,
                                'AZ %s' % kwargs['az_name'],
                                node_id,
                                {'nova_az': kwargs['az_name'],
                                 'libvirt_type': kwargs['libvirt_type']},
                                ['node', 'container', 'nova'])

        return self._ok()

#########################
#add backup

    #####################
    #Backup Module
    #####################
    def backup_cluster(self, state_data, api, node_id, **kwargs):


        psbk=svbk_manager.svbk_manager(self.logger)
        retArray = psbk.backup_cluster(api, node_id, **kwargs)

        if 0 != retArray[0]:
            return self._fail(msg=retArray[1])

        return self._ok()


    #####################
    #Restore Module
    #####################
    def restore_cluster(self, state_data, api, node_id, **kwargs):


        psbk=svbk_manager.svbk_manager(self.logger)
        retArray = psbk.restore_cluster(api, node_id, **kwargs)

        if 0 != retArray[0]:
            return self._fail(msg=retArray[1])

        return self._ok()

#add backup
#########################

    # README(shep): part of happy path, not excluding from code coverage
    def create_cluster(self, state_data, api, node_id, **kwargs):
        self.logger.debug('NovaBackend:create_cluster')
        kwargs['nova_az'] = 'nova'

        # make sure we have good inputs
        if not 'cluster_name' in kwargs:
            return self._fail(msg='Cluster Name (cluster_name) required')
        valid = string.letters + string.digits + "_-"
        test_valid = all([c in valid for c in kwargs['cluster_name']])
        if not test_valid:
            return self._fail(msg='Cluster name must be entirely composed of'
                              ' alphanumeric characters, -s, or _s')
        r = api.nodes_query('facts.chef_environment = "%s"' % (
            kwargs['cluster_name'],))
        if len(r) > 0:
            return self._fail(msg='Cluster Name should be unique')

        cluster_facts = ["nova_public_if",
                         "keystone_admin_pw",
                         "nova_dmz_cidr",
                         "nova_vm_fixed_range",
                         "nova_vm_fixed_if",
                         "nova_vm_bridge",
                         "osops_mgmt",
                         "osops_nova",
                         "osops_public",
                         "libvirt_type"]

        environment_hash = {}
        for k, v in kwargs.items():
            if k in cluster_facts:
                environment_hash[k] = v

        environment_hash['chef_server_consumed'] = kwargs['chef_server']
        environment_hash['chef_environment'] = kwargs['cluster_name']
        environment_hash['ram_allocation_ratio'] = 1
        environment_hash['cpu_allocation_ratio'] = 16
        environment_hash['nova_use_single_default_gateway'] = 'false'
        environment_hash['nova_network_dhcp_name'] = 'novalocal'

        #for_neutron
        my_path = os.path.abspath(os.path.dirname(__file__))
        fact_list_path = os.path.join(my_path, 'neutron.json')

        if os.path.exists(fact_list_path):
            with open(fact_list_path, 'r') as f:
                neutron_fact = json.loads(f.read())
                for k in neutron_fact.keys():
                    if kwargs.has_key(k):
                        environment_hash[k] = kwargs[k]
                    else :
                        environment_hash[k] = neutron_fact[k]
        #for_neutron

        #tenant start
        if kwargs['tenant_name'] is None or kwargs['tenant_name'] == '':
            return self._fail(msg='Tenant Name is Invalid')

        target_tenant = kwargs['tenant_name']

        # have the attribute map, let's make it an apply the
        # facts.
        #cluster = self._make_subcontainer(
        #    api, kwargs['cluster_name'], node_id, environment_hash,
        #    ['node', 'container', 'nova', 'chef-environment'],
        #    attrs={"locked": True})
        cluster = self._make_subcontainer(
            api, kwargs['cluster_name'], node_id, environment_hash,
            ['node', 'container', 'nova', 'chef-environment'],
            attrs={"locked": True}, tenant=target_tenant)
        #tenant end

        if cluster is None:
            return self._fail(msg='cannot create nova cluster container')

        infra = self._make_subcontainer(
            api, 'Infrastructure', cluster['id'],
            {'nova_role': 'nova-controller-master', 'ha_infra': False},
            ['node', 'container', 'nova', 'nova-controller'])

        if infra is None:
            return self._fail(msg='cannot create "Infra" container')

        comp = self._make_subcontainer(
            api, 'Compute', cluster['id'],
            {'nova_role': 'nova-compute'},
            ['node', 'container', 'nova', 'nova-compute'],
            {"locked": True})

        if comp is None:
            return self._fail(msg='cannot create "Compute" container')

        az = kwargs['nova_az']

        self._make_subcontainer(
            api, 'AZ %s' % az, comp['id'], {'nova_az': az},
            ['node', 'container', 'nova'])

        # self.logger.debug('NovaBackend:create_cluster-SND')
        #
        self._make_subcontainer(
            api, 'SDN Boxes', cluster['id'],
            {'nova_role': 'nova-sdn'},
            ['node', 'container', 'nova', 'sdn'])
        #

        return self._ok()

    def set_sdnbox(self, state_data, api, node_id, **kwargs):
        logging.error('NovaBackend:set_sdnbox')
        #nodeinfo = api.node_get_by_id(node['id'])
        #if 'chef_environment' in nodeinfo['facts']:
        #    old_backend = nodeinfo['facts'].get('backends', [])
        novacluster = self._get_novacluster_name(api, node_id)
        #novacluster = None 
        logging.error('novacluster:%s' % novacluster)
        if novacluster is None:
            # movo to Available
            logging.error('set_sdnbos ret')
            return self._ok()

        node_list = api.nodes_query('name = "%s"' % novacluster)
        #tmp = None
        logging.error('novacluster info = %s' % node_list)
        nova_id = node_list[0]['id']
        logging.error('novacluster id = %s' % nova_id)

#        self.get_node_info(api, nova_id)

        # sdn s
        switch = api._model_get_by_id('nodes', node_id)
        switch_list = switch['name'].split(',')
        logging.error('switch name = %s' % switch['name'])

        nodes = api._model_get_all('nodes')
        for node in nodes:
            #node info get
            nodeinfo = api.node_get_by_id(node['id'])
            logging.error('nodeinfo = %s' % nodeinfo['name'])

            if NOVA_CLUSTER_SW == nodeinfo['name']:
                ofc_ip_list= nodeinfo['facts']['neutron_ofc_host'].split(',')
                logging.error('OFC IP = %s' % nodeinfo['facts']['neutron_ofc_host'])
                break

        logging.error('token_id = %s' % kwargs['tokenid'])

        auth=kwargs['tokenid']

        psm=psset_manager.psset_manager()
        psm.set_logger(logging)
        psm.set_auth(auth)
        if -1==psm.set_sw_list(switch_list):
            return self._fail(msg='Switch List')
        if -1==psm.set_ofc_ip_list(ofc_ip_list):
            return self._fail(msg='OFC ip list')
        psm.setup_switch()
        # sdn e

        return self._ok()

    def _get_novacluster_name(self, api, node_id):
        logging.error('NovaBackend:_get_novacluster_name')
        nodeinfo = api.node_get_by_id(node_id)

        if 'chef_environment' in nodeinfo['facts']:
            logging.error('chef_environment:%s' % nodeinfo['facts']['chef_environment'])
            name = nodeinfo['facts']['chef_environment']
        else:
            logging.error('name None')
            name = None

        return name

    def _parent_list(self, api, starting_node):  # pragma: no cover
        ret = list()
        node = starting_node
        while 'parent_id' in node['facts']:
            ret.append(node['facts']['parent_id'])
            node = api.node_get_by_id(node['facts']['parent_id'])
        return ret

    def get_node_info(self, api, node_id):
        #get all node id
        logging.error('NovaBackend:get_node_info')
        server_node_list = []
        server_node_name = []
        switch_node_list = []
        switch_node_name = []

        nodes = api._model_get_all('nodes')
        logging.error('nodes = %s' % nodes)

        for node in nodes:
            #node info get
            nodeinfo = api.node_get_by_id(node['id'])
            logging.error('nodeinfo = %s' % nodeinfo)
            parent_list = []

            #node parent list get
            parent_list = self._parent_list(api, nodeinfo)
            logging.error('parent_list = %s' % parent_list)

            #is novacluster_id in parent_list
            if node_id in parent_list:
                #is novacluster_id in parent_list
                if 'backends' in nodeinfo['facts']:
                    #is agent in facts.backend
                    if 'agent' in nodeinfo['facts']['backends']:
                        if 'sdn' in nodeinfo['facts']['backends']:
                            switch_node_list.append(node['id'])
                            switch_node_name.append(node['name'])
                        else:
                            server_node_list.append(node['id'])
                            server_node_name.append(node['name'])

        #self.br_log(node_id, name, br_mode, '*** SERVER_NODE_LIST: %s' % server_node_list)
        #self.br_log(node_id, name, br_mode, '*** SERVER_NODE_NAME: %s' % server_node_name)

        #self.br_log(node_id, name, br_mode, '*** SWITCH_NODE_LIST: %s' % switch_node_list)
        #self.br_log(node_id, name, br_mode, '*** SWITCH_NODE_NAME: %s' % switch_node_name)

        logging.error('*** SERVER_NODE_LIST: %s' % server_node_list)
        logging.error('*** SERVER_NODE_NAME: %s' % server_node_name)
        logging.error('*** SWITCH_NODE_LIST: %s' % switch_node_list)
        logging.error('*** SWITCH_NODE_NAME: %s' % switch_node_name)

        return [server_node_name, switch_node_name]

