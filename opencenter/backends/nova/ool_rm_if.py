import urllib2
import json

import logging.handlers

# stub mode
#    ON : read test file
#    OFF: read data from device manager
STUB_FLAG = 'OFF'
Home_dir='./'
PY_PATH='/usr/share/pyshared/opencenter/backends/nova/'
CNF_FILE='db_info.cnf'

DB_URL_KEY ='DB_URL='
DB_PORT_KEY='DB_PORT='
ROOT_DIR='/ool_rm/'

PLANE_LIST=['C-Plane','M-Plane','D-Plane','S-Plane']

DBG_FLAG='ON'
####add##########
LOG_FILENAME = 'logging_rotatingfile_example.out'

# Set up a specific logger with our desired output level
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=20, backupCount=5)

my_logger.addHandler(handler)
####add##########

class ool_rm_if:

	def __init__(self):
		self.auth   =''
		# load configfile
		c_file= PY_PATH + CNF_FILE

		try:
			f=open(c_file, 'r')
		except:
			print 'file open(OOL_RM_IF_CNF) error'
			return

		for line in f:
			if line.find(DB_URL_KEY) != -1:
				self.url_head=line[line.find(DB_URL_KEY)+len(DB_URL_KEY):-1]
			if line.find(DB_PORT_KEY) != -1:
				self.port=line[line.find(DB_PORT_KEY)+len(DB_PORT_KEY):-1]

		if ('' == self.url_head) or ('' == self.port):
			print 'config file error'
			return
		
		self.rm_create = ool_rm_if_createImpl()
		self.rm_create.set_url_head(self.url_head)
		self.rm_create.set_port(self.port)
		self.rm_get = ool_rm_if_getImpl()
		self.rm_get.set_url_head(self.url_head)
		self.rm_get.set_port(self.port)
		self.rm_delete = ool_rm_if_deleteImpl()
		self.rm_delete .set_url_head(self.url_head)
		self.rm_delete.set_port(self.port)

#--auth
	def set_auth(self,auth):
		self.auth=auth
		self.rm_create.set_authImpl(auth)
		self.rm_get.set_authImpl(auth)
		self.rm_delete.set_authImpl(auth)

#--create interface
	def set_node_data(self, node_data):
		return self.rm_create.set_node_dataImpl(node_data)
	def set_switch_data(self, switch_data):
		return self.rm_create.set_switch_dataImpl(switch_data)
	def set_port_data(self, device_name, port_data):
		return self.rm_create.set_port_dataImpl(device_name, port_data)
	def set_nic_data(self, device_name, nic_data):
		return self.rm_create.set_nic_dataImpl(device_name, nic_data)
	def set_used_data(self, device_name, used_data):
		return self.rm_create.set_used_dataImpl(device_name, used_data)
	def set_backup_data(self, cluster_name, backup_name, device_list):
		return self.rm_create.set_backup_dataImpl(cluster_name, backup_name, device_list)

#--get interface
	def get_device(self, dev_name):
		return self.get_node(dev_name)
	def get_node(self, dev_name):
		return self.rm_get.get_nodeImpl(dev_name)
	def get_device_all(self):
		return self.get_node_all()
	def get_node_all(self):
		return self.rm_get.get_node_allImpl()
	def get_switch(self, sw_name):
		return self.rm_get.get_switchImpl(sw_name)
	def get_switch_all(self):
		return self.rm_get.get_switch_allImpl()
	def get_port(self, sw_name):
		return self.rm_get.get_portImpl(sw_name)
	def get_nic(self, dev_name):
		return self.rm_get.get_nicImpl(dev_name)
	def get_nic_traffic_info(self, dev_name, traffic_type):
		return self.rm_get.get_nicImpl(dev_name, traffic_type=traffic_type)
	def get_used(self, dev_name, user_name):
		return self.rm_get.get_usedImpl(dev_name, user_name)
	def get_tenant(self, dev_name, tenant_name):
		return self.rm_get.get_tenantImpl(dev_name, tenant_name)
	def get_backup_cluster(self, cluster_name):
		return self.rm_get.get_backup_clusterImpl(cluster_name)

#--update interface

#-- delete interface
	def del_node(self, device_name):
		return self.rm_delete.del_nodeImpl(device_name)
	def del_switch(self, device_name):
		return self.rm_delete.del_switchImpl(device_name)
	def del_port(self, device_name, port_name):
		return self.rm_delete.del_portImpl(device_name, port_name=port_name)
	def del_port_all(self, device_name):
		return self.rm_delete.del_portImpl(device_name)
	def del_nic(self, device_name, nic_name):
		return self.rm_delete.del_nicImpl(device_name, nic_name=nic_name)
	def del_nic_all(self, device_name):
		return self.rm_delete.del_nicImpl(device_name)
	def del_used(self, device_name):
		return self.rm_delete.del_usedImpl(device_name)
	def del_tenant(self, dev_name, tenant_name):
		return self.rm_get.del_tenantImpl(dev_name, tenant_name)
	def del_backup(self, cluster_name, backup_name):
		return self.rm_delete.del_backupImpl(cluster_name, backup_name=backup_name)
	def del_backup_cluster(self, cluster_name):
		return self.rm_delete.del_backupImpl(cluster_name)

#--common
class ool_rm_if_common:
	def __init__(self):
		self.url_head = ''
		self.port     = ''
		self.errmsg   = ''

	def set_url_head(self, url_head):
		self.url_head = url_head

	def set_port(self, port):
		self.port = port

	def http_get(self, url_para):
		return self.__http_read__(url_para)

	def http_post(self, url_para, body):
		return self.__http_write__(url_para, '', body)

	def http_put(self, url_para, body):
		return self.__http_write__(url_para, 'UPDATE', body)

	def url_delete(self, url_para, body):
		return self.__http_write__(url_para, 'DELETE', body)

	def __http_read__(self, url_para):
		try:
			url='%s:%s%s' % (self.url_head, self.port, url_para)
			if 'ON' == STUB_FLAG:
				read_data=self.url_head_read_tst(url)
			else:
				read_data=json.load(urllib2.urlopen(url), encoding='utf8')
#				if 'ON' == DBG_FLAG:
#					my_logger.debug('read url:%s' %(url))
			return read_data
		except Exception, e:
			self.errmsg=e
			print str(e)
			return -1

	def __http_write__(self, url_para, sel, body):
		try:
			url='%s:%s%s' % (self.url_head, self.port, url_para)
			if 'ON' == STUB_FLAG:
				output=self.url_head_write_tst(url, body)
			else:
				body_data=str(body)
				req      =urllib2.Request(url, body_data)
				req.add_header('Content-Type', 'application/json')
				req.add_header('Accept-Charset', 'utf-8')
				if 'UPDATE' == sel:
					req.get_method = lambda: 'PUT'
				if 'DELETE' == sel:
					req.get_method = lambda: 'DELETE'
				response =urllib2.urlopen(req)
				output   =json.load(response, encoding='utf8')
			return output
		except Exception, e:
			self.errmsg=e
			print str(e)
			return -1

	def __list2dict__(self, para1):
		if True == isinstance(para1,list):
			dict_tmp=para1[0]
		else:
			dict_tmp=para1
		return dict_tmp

	def __err_chk__(self, err):
		if -1 == err:
			return [-1, self.errmsg]
		
		if ((200 != err['status']) and (201 != err['status'])):
			return [-1, str(err['status'])]

		return [0, 0]

#--create Impl
class ool_rm_if_createImpl(ool_rm_if_common):
	def __init__(self):
		self.auth=''

	def set_authImpl(self, auth):
		self.auth=auth

	def set_data(self, url_para, body):
		http_write=self.http_post(url_para, body)
		err_status = self.__err_chk__(http_write)
		if -1 == err_status[0]:
			return err_status

		ret=http_write['status']
		return [0, ret]

	def set_dataImpl(self, url_para, body):
		http_write=self.http_post(url_para, body)
		err_status = self.__err_chk__(http_write)
		if -1 == err_status[0]:
			return err_status

		ret=http_write['status']
		return [0, ret]

	def set_node_dataImpl(self, node_data):
		body={}
		body.update({'auth':self.auth})
		body.update({'params':node_data})

		url_para='%sNode' % (ROOT_DIR)
		return self.set_data(url_para, body)

	def set_switch_dataImpl(self, switch_data):
		body={}
		body.update({'auth':self.auth})
		body.update({'params':switch_data})

		url_para='%sSwitch' % (ROOT_DIR)
		return self.set_data(url_para, body)

	def set_port_dataImpl(self, device_name, port_data):
		body={}
		body.update({'auth':self.auth})
		body.update({'device_name':str(device_name)})
		body.update({'params':port_data})

		url_para='%sPort' % (ROOT_DIR)
		return self.set_data(url_para, body)

	def set_nic_dataImpl(self, device_name, nic_data):
		body={}
		body.update({'auth':self.auth})
		body.update({'device_name':str(device_name)})
		body.update({'params':nic_data})

		url_para='%sNic' % (ROOT_DIR)
		return self.set_data(url_para, body)

	def set_used_dataImpl(self, device_name, used_data):
		body={}
		body.update({'auth':self.auth})
		body.update({'device_name':str(device_name)})
		body.update({'params':used_data})

		url_para='%sUsed' % (ROOT_DIR)
		return self.set_data(url_para, body)

	def set_backup_dataImpl(self, cluster_name, backup_name, device_list):
		body={"auth":"","params":{"cluster_name":"","backup_name":"","device":""}}	
		body['auth']                  = self.auth
		body['params']['cluster_name']=str(cluster_name)
		body['params']['backup_name'] =str(backup_name)
		
		for i in range(0, len(device_list)):
			device_list[i] = str(device_list[i])
		body['params']['device'] = device_list

		url_para='%sBackup' % (ROOT_DIR)
		return self.set_data(url_para, body)

#--get Impl
class ool_rm_if_getImpl(ool_rm_if_common):
	def __init__(self):
		self.auth = ''

	def set_authImpl(self, auth):
		self.auth = auth

	def get_data(self, url_para):
		http_read=self.http_get(url_para)
		err_status = self.__err_chk__(http_read)
		if -1 == err_status[0]:
			return err_status

		ret =  http_read['result']
		return [0, ret]

	def get_node_filter(self, data):
		url_para='%sNode?' %(ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		if "status" in data:
			url_para=url_para + 'status=%s&' % (data['staus'])
		if "owner" in data:
			url_para=url_para + 'owner=%s&' % (data['owner'])
		if "site" in data:
			url_para=url_para + 'site=%s&' % (data['site'])
		if "traffic_type" in data:
			url_para=url_para + 'traffic_type=%s&' % (data['traffic_type'])

		url_para=url_para + 'auth=%s' % (self.auth)

		dev_info=self.get_data(url_para)
		return dev_info

	def get_switch_filter(self, data):
		url_para='%sSwitch?' %(ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		if "status" in data:
			url_para=url_para + 'status=%s&' % (data['staus'])
		if "owner" in data:
			url_para=url_para + 'owner=%s&' % (data['owner'])
		if "site" in data:
			url_para=url_para + 'site=%s&' % (data['site'])

		url_para=url_para + 'auth=%s' % (self.auth)

		sw_info=self.get_data(url_para)
		return sw_info

	def get_port_filter(self, data):
		url_para='%sPort?' %(ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		else:
			return [-1,""]
		if "port_name" in data:
			url_para=url_para + 'port_name=%s&' % (data['port_name'])
		if "band" in data:
			url_para=url_para + 'band=%s&' % (data['band'])
		if "openflow_flg" in data:
			url_para=url_para + 'openflow_flg=%s&' % (data['openflow_flg'])

		url_para=url_para + 'auth=%s' % (self.auth)

		port_info=self.get_data(url_para)
		return port_info

	def get_nic_filter(self, data):
		url_para='%sNic?' %(ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		else:
			return [-1,""]
		if "nic_name" in data:
			url_para=url_para + 'nic_name=%s&' % (data['nic_name'])
		if "band" in data:
			url_para=url_para + 'band=%s&' % (data['band'])
		if "mac_address" in data:
			url_para=url_para + 'mac_address=%s&' % (data['mac_address'])
		if "ip_address" in data:
			url_para=url_para + 'ip_address=%s&' % (data['ip_address'])
		if "traffic_type" in data:
			url_para=url_para + 'traffic_type=%s&' % (data['traffic_type'])

		url_para=url_para + 'auth=%s' % (self.auth)

		nic_info=self.get_data(url_para)
		return nic_info

	def get_used_filter(self, data):
		url_para='%sUsed?' %(ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		if "user_name" in data:
			url_para=url_para + 'user_name=%s&' % (data['user_name'])

		url_para=url_para + 'auth=%s' % (self.auth)
		used_info=self.get_data(url_para)
		return used_info

	def get_tenant_filter(self, data):
		url_para='%sTenant?' %(ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		if "tenant_name" in data:
			url_para=url_para + 'tenant_name=%s&' % (data['tenant_name'])

		url_para=url_para + 'auth=%s' % (self.auth)
		tenant_info=self.get_data(url_para)
		return tenant_info

	def get_backup_filter(self, data):
		url_para='%sBackup?' %(ROOT_DIR)
		if "cluster_name" in data:
			url_para=url_para + 'cluster_name=%s&' % (data['cluster_name'])
		if "backup_name" in data:
			url_para=url_para + 'backup_name=%s&' % (data['backup_name'])

		url_para=url_para + 'auth=%s' % (self.auth)
		bk_info=self.get_data(url_para)
		return bk_info

#--get Impl
	def get_nodeImpl(self, dev_name, **key):
		para = {'device_name':''}
		para['device_name'] = dev_name
		if 'status' in key:
			para.update({'status':key['status']})
		if 'owner' in key:
			para.update({'owner':key['owner']})
		if 'site' in key:
			para.update({'site':key['site']})
		if 'traffic_type' in key:
			para.update({'traffic_type':key['traffic_type']})

		dev_info=self.get_node_filter(para)
		if -1==dev_info[0]:
			return dev_info
		else:
			dev_data=self.__list2dict__(dev_info[1])
			return [0, dev_data]

	def get_node_allImpl(self):
		para={}
		dev_info=self.get_node_filter(para)
		if -1==dev_info[0]:
			return dev_info
		else:
			dev_data=[]
			dev_info_wk=dev_info[1]
			for i in range(0,len(dev_info_wk)):
				dev_wk=self.__list2dict__(dev_info_wk[i])
				dev_data.append(dev_wk['device_name'])
			return [0, dev_data]

	def get_switchImpl(self, sw_name, **key):
		para = {'device_name':''}
		para['device_name'] = sw_name
		if 'status' in key:
			para.update({'status':key['status']})
		if 'owner' in key:
			para.update({'owner':key['owner']})
		if 'site' in key:
			para.update({'site':key['site']})

		dev_info=self.get_switch_filter(para)

		if -1==dev_info[0]:
			return dev_info
		else:
			dev_data=self.__list2dict__(dev_info[1])
#			my_logger.debug('?????get switch:%s' %(dev_data))
			return [0, dev_data]

	def get_switch_allImpl(self):
		para={}
		sw_info=self.get_switch_filter(para)
		if -1==sw_info[0]:
			return sw_info
		else:
			sw_data=[]
			sw_info_wk=sw_info[1]
			for i in range(0, len(sw_info_wk)):
				sw_wk=self.__list2dict__(sw_info_wk[i])
				sw_data.append(sw_wk['device_name'])
				sw_data.append(sw_wk['vender_name'])
			return [0, sw_data]

	def get_portImpl(self, sw_name, **key):
		para = {'device_name':''}
		para['device_name'] = sw_name
		if 'port_name' in key:
			para.update({'port_name':key['port_name']})
		if 'band' in key:
			para.update({'band':key['band']})
		if 'openflow_flg' in key:
			para.update({'openflow_flg':key['openflow_flg']})
		port_info=self.get_port_filter(para)
		return port_info

	def get_nicImpl(self, dev_name, **key):
		para = {}
		para.update({'device_name':dev_name})
		if 'nic_name' in key:
			para.update({'nic_name':key['nic_name']})
		if 'band' in key:
			para.update({'band':key['band']})
		if 'mac_address' in key:
			para.update({'mac_address':key['mac_address']})
		if 'ip_address' in key:
			para.update({'ip_address':key['ip_address']})
		if 'traffic_type' in key:
			t_type=''
			for i in range(0, len(PLANE_LIST)):
				if PLANE_LIST[i]==key['traffic_type']:
					t_type='{0:03d}'.format(i+1)
					break
			para.update({'traffic_type':t_type})

		nic_info=self.get_nic_filter(para)
		return nic_info

	def get_usedImpl(self, dev_name, user_name):
		para = {}
		if '' != dev_name:
			para.update({'device_name':dev_name})
		if '' != user_name:
			para.update({'user_name':dev_name})
		used_info=self.get_used_filter(para)
		return used_info

	def get_tenantImpl(self, dev_name, tenant_name):
		para = {}
		if '' != dev_name:
			para.update({'device_name':dev_name})
		if '' != tenant_name:
			para.update({'tenant_name':tenant_name})
		tenant_info=self.get_tenant_filter(para)
		return tenant_info

	def get_backup_clusterImpl(self, cluster_name, **key):
		para = {}
		para.update({'cluster_name':cluster_name})
		if 'backup_name' in key:
			para.update({'backup_name':key['backup_name']})
		backup_info=self.get_backup_filter(para)
		return backup_info

#--update Impl
class ool_rm_if_updateImpl(ool_rm_if_common):
	def __init_(self):
		self.auth = ''
		
	def set_authImpl(self, auth):
		self.auth = auth

	def update_data(self, url_para, data):
		url_update = self.http_put(url_para, data)
		err_status = self.__err_chk__(url_update)
		if -1 == err_status[0]:
			return err_status

		ret=url_update['status']
		return [0, ret]

#--delete Impl
class ool_rm_if_deleteImpl(ool_rm_if_common):
	def __iniit__(self):
		self.auth = ''

	def set_authImpl(self, auth):
		self.auth = auth

	def del_data(self, url_para, data):
		url_del=self.url_delete(url_para, data)
		err_status = self.__err_chk__(url_del)
		if -1 == err_status[0]:
			return err_status

		ret=url_del['status']
		return [0, ret]

	def del_cmn_filter(self, url_para, data):
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		else:
			return [-1,""]
		url_para=url_para + 'auth=%s' % (self.auth)
		ret=self.del_data(url_para, '')
		return ret
	
	def del_node_filter(self, data):
		url_para='%sNode?' %(ROOT_DIR)
		return self.del_cmn_filter(url_para, data)

	def del_switch_filter(self, data):
		url_para='%sSwitch?' % (ROOT_DIR)
		return self.del_cmn_filter(url_para, data)

	def del_port_filter(self, data):
		url_para='%sPort?' % (ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		else:
			return [-1,""]
		if "port_name" in data:
			url_para=url_para + 'port_name=%s&' % (data['port_name'])

		url_para=url_para + 'auth=%s' % (self.auth)
		ret=self.del_data(url_para, '')
		return ret

	def del_nic_filter(self, data):
		url_para='%sNic?' % (ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		else:
			return [-1,""]
		if "nic_name" in data:
			url_para=url_para + 'nic_name=%s&' % (data['nic_name'])

		url_para=url_para + 'auth=%s' % (self.auth)
		ret=self.del_data(url_para, '')
		return ret

	def del_used_filter(self, data):
		url_para='%sUsed?' % (ROOT_DIR)
		return self.del_cmn_filter(url_para, data)

	def del_tenant_filter(self, data):
		url_para='%sTenant?' % (ROOT_DIR)
		if "device_name" in data:
			url_para=url_para + 'device_name=%s&' % (data['device_name'])
		else:
			if "tenant_name" in data:
				url_para=url_para + 'tenant_name=%s&' % (data['tenant_name'])
			else:
				return [-1,""]

		url_para=url_para + 'auth=%s' % (self.auth)
		ret=self.del_data(url_para, '')
		return ret

	def del_backup_filter(self, data):
		url_para='%sBackup?' % (ROOT_DIR)
		if "cluster_name" in data:
			url_para=url_para + 'cluster_name=%s&' % (data['cluster_name'])
		else:
			return [-1,""]
		if "back_name" in data:
			url_para=url_para + 'back_name=%s&' % (data['back_name'])
		else:
			return [-1,""]
		url_para=url_para + 'auth=%s' % (self.auth)
		ret=self.del_data(url_para, '')
		return ret

#------
	def del_nodeImpl(self, dev_name):
		para = {}
		para.update({'device_name':dev_name})
		return self.del_node_filter(para)

	def del_switchImpl(self, dev_name):
		para = {}
		para.update({'device_name':dev_name})
		return self.del_switch_filter(para)

	def del_portImpl(self, dev_name, **key):
		para = {}
		para.update({'device_name':dev_name})
		if 'port_name' in key:
			para.update({'port_name':key['port_name']})
		return self.del_port_filter(para)

	def del_nicImpl(self, dev_name, **key):
		para = {}
		para.update({'device_name':dev_name})
		if 'nic_name' in key:
			para.update({'nic_name':key['nic_name']})
		return self.del_nic_filter(para)

	def del_usedImpl(self, dev_name):
		para = {}
		para.update({'device_name':dev_name})
		return self.del_used_filter(para)

	def del_tenantImpl(self, dev_name, tenant_name):
		para = {}
		if '' != dev_name:
			para.update({'device_name':dev_name})
		if '' != tenant_name:
			para.update({'tenant_name':tenant_name})
		return self.del_tenant_filter(para)

	def del_backupImpl(self, cluster_name, **key):
		para = {}
		para.update({'cluster_name':cluster_name})
		if 'backup_name' in key:
			para.update({'backup_name':key['backup_name']})
		return self.del_backup_filter(para)

#--test code
class ool_rm_if_tst:
	def __init__(self):
		return

	def http_read_tst(self, url):
		wk = str(url)

		data={}
		if -1 != wk.find(ROOT_DIR + 'Node?auth='):
			f = open(Home_dir + "test_data/dev_cnf_all.txt", 'r')
			data = json.load(f)
			f.close()
			return data
		else:
			if -1 !=  wk.find(ROOT_DIR + 'Node?device_name='):
				r_fname='%stest_data/dev_cnf_%s.txt' % (Home_dir, wk[wk.rfind('_name=')+6:wk.find('&')])
				f = open(r_fname, 'r')
				data = json.load(f)
				f.close()
				return data

		if -1 != wk.find(ROOT_DIR + 'Switch?auth='):
			f = open(Home_dir + "test_data/sw_cnf_all.txt", 'r')
			data = json.load(f)
			f.close()
			return data
		else:
			if -1 !=  wk.find(ROOT_DIR + 'Switch?device_name='):
				r_fname='%stest_data/sw_cnf_%s.txt' % (Home_dir, wk[wk.rfind('_name=')+6:wk.find('&')])
				f = open(r_fname, 'r')
				data = json.load(f)
				f.close()
				return data

		if -1 != wk.find(ROOT_DIR + 'Port?'):
			f = open(Home_dir + "test_data/port_cnf.txt", 'r')
			data = json.load(f)
			f.close()
			return data

		if -1 != wk.find(ROOT_DIR + 'Nic?traffic_type='):
			r_fname='%stest_data/nic_cnf_%s.txt' % (Home_dir, wk[wk.rfind('_type=')+6:wk.find('&')])
			f = open(r_fname, 'r')
			data = json.load(f)
			f.close()
			return data
		else:
			if -1 != wk.find(ROOT_DIR + 'Nic?'):
				f = open(Home_dir + "test_data/nic_cnf.txt", 'r')
				data = json.load(f)
				f.close()
				return data

		if -1 != wk.find(ROOT_DIR + 'Backup?'):
			f = open(Home_dir + "test_data/backup_cnf.txt", 'r')
			data = json.load(f)
			f.close()
			return data

	def http_write_tst(self, url, body):
		wk = str(url)

		if -1 != wk.find(ROOT_DIR + 'Backup?auth='):
			f = open(Home_dir + "test_data/backup_wdata.txt", 'w')
			f.write(body)
			f.close()
			return {"result":[''],"status":200}
