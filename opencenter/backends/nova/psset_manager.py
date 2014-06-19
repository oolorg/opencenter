import ool_rm_if
import pfs_if
import pica8_if
import centec_if
import logging

# Device Manager URL and port 
DBG_FLAG='ON'

TRACE_TITLE='PSST_MANAGER:%s'
EXCEPT_TITLE='PSST_MANAGER:%s'

AUTH_KEY='xxx'

class psset_manager():

	def __init__(self):
		self.a_model={}
		self.a_ip={}
		self.a_user={}
		self.a_pw={}
		self.a_switch=[]
		self.a_port_info=[]
		self.a_ofc_ip=[]

		self.auth=''
		self.logger=logging

		self.ori=ool_rm_if.ool_rm_if()
		self.ori.set_auth(AUTH_KEY)

	def __trace_log__(self, log):
		if 'ON' == DBG_FLAG:
			self.logger.debug(TRACE_TITLE %(log))
		return 0

	def __except_log__(self, log):
		self.logger.debug(EXCEPT_TITLE %(log))
		return 0

	def __get_PS_info__(self):
	# Get Physical switch infomation from resource manager

		for i in range(0, len(self.a_switch)):

			data_sw=self.ori.get_switch(self.a_switch[i])

			if -1 != data_sw[0]:
				pfs_info={}
				pfs_info=data_sw[1]
				self.a_model[i]=pfs_info["product_name"]
				self.a_ip[i]=pfs_info["ip_address"]
				self.a_user[i]=pfs_info["user_name"]
				self.a_pw[i]=pfs_info["password"]
			else:
				print data_sw
				print "<switch info get error>"
				return -1

			get_port_data=self.ori.get_port(self.a_switch[i])

			if -1 != get_port_data[0]:
				port_info=[]
				port_info=get_port_data[1]
				self.a_port_info.append(port_info)
			else:
				print "<port info get error>"
				return -1

		return 0

	def set_auth(self, auth):
		self.__trace_log__('set_auth IN')
		self.auth=auth
		self.ori.set_auth(auth)
		self.__trace_log__('set_auth OUT')

	def set_logger(self, logger):
		self.logger=logger

	def set_sw_list(self, switch_list):
		self.__trace_log__('set_sw_list IN')
		if isinstance(switch_list,list):
			self.a_switch=switch_list
		else:
			self.__except_log__('set_sw_list ParaError OUT')
			return -1
		self.__trace_log__('set_sw_list OUT')
		return 0

	def set_ofc_ip_list(self, ofc_ip_list):
		self.__trace_log__('set_ofc_ip_list IN')
		if isinstance(ofc_ip_list,list):
			self.a_ofc_ip=ofc_ip_list
		else:
			self.__except_log__('set_ofc_ip_list ParaError OUT')
			return -1
		self.__trace_log__('set_ofc_ip_list OUT')
		return 0

	def setup_switch(self):
		self.__trace_log__('Start Setup of Physical Switch')
		print "Start Setup of Physical Switch"
		
		if -1 ==self.__get_PS_info__():
			return -1

		for i in range(0, len(self.a_switch)):
			sw_setup=''

			if ((True == self.a_model[i].startswith("P-3295")) or (True == self.a_model[i].startswith("P-3290"))):
				priority=255 - i
				sw_setup=pica8_if.pica8_if()

		#	if (True == a_sw_model[i].startswith("BCM56846" )):
		#		priority=255 - i
		#		sw_setup=riava_if.riava_if()

			if (True == self.a_model[i].startswith("PF5240" )):
				priority=255 - i
				sw_setup=pfs_if.pfs_if()

			if (True == self.a_model[i].startswith("48T4X" )):
				priority=255 - i
				sw_setup=centec_if.centec_if()

			if ''==sw_setup:
				continue

			sw_setup.set_auth(self.auth)
			sw_setup.set_logger(self.logger)
			sw_setup.set_host_name(self.a_switch[i])
			sw_setup.set_ofc_info(priority, self.a_ofc_ip)
			ret=sw_setup.setup_ofc()

			if 0 != ret:
				self.__except_log__('setup process error.')
				print "setup process error."
				return -1

		self.__trace_log__('End Setup of Physical Switch')
		print "End Setup of Physical Switch"
		return 0
