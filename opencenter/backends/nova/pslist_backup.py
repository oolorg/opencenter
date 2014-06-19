import sys
import pexpect

EXPECT_PASSWD='.*password:.*'
EXPECT_YESNO='.*(yes/no)? '
SEND_YES='yes'

DEBUG_FLAG='ON'
PSLIST_FILE='pslist.txt'

class pslist_backup:

	def __init__(self, bk_ip, bk_uname, bk_upw):
		self.bk_ip   =bk_ip
		self.bk_uname=bk_uname
		self.bk_upw  =bk_upw

	def set_pslist(self, src_file, back_dir):
		# start get pysical switch list
		para='scp %s %s@%s:%s/%s' %(src_file, self.bk_uname, self.bk_ip, back_dir, PSLIST_FILE)
		c = pexpect.spawn(para)
		if 'ON' == DEBUG_FLAG:
			c.logfile=sys.stdout

		i=c.expect([EXPECT_PASSWD, EXPECT_YESNO, src_file[src_file.rindex('/')+1:]+ '.*'])
		if 0==i:
			c.sendline(self.bk_upw)
		if 1==i:
			c.sendline(SEND_YES)
			j=c.expect([EXPECT_PASSWD, src_file[src_file.rindex('/')+1:]+ '.*'])
			if 0 ==j:
				c.sendline(self.bk_upw)

		c.expect(pexpect.EOF)
		c.close()

		return 0

	def get_pslist(self, dst_file, back_dir):
		# start get pysical switch list
		para='scp %s@%s:%s/%s %s' %(self.bk_uname, self.bk_ip, back_dir, PSLIST_FILE, dst_file)
		c = pexpect.spawn(para)
		if 'ON' == DEBUG_FLAG:
			c.logfile=sys.stdout

		i=c.expect([EXPECT_PASSWD, EXPECT_YESNO, PSLIST_FILE + '.*'])
		if 0==i:
			c.sendline(self.bk_upw)
		if 1==i:
			c.sendline(SEND_YES)
			j=c.expect([EXPECT_PASSWD, PSLIST_FILE + '.*'])
			if 0 ==j:
				c.sendline(self.bk_upw)

		c.expect(pexpect.EOF)
		c.close()

		return 0
