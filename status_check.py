#!/usr/bin/env python

import paramiko, time, threading, sys, logging, os, multiprocessing
from progressbar import ProgressBar,Bar,Percentage

reload(sys)
sys.setdefaultencoding('utf-8')

date3 = time.strftime('%Y%m%d', time.localtime(time.time()))
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('%s.log' % date3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

local_update_file_dir = '/home/weblogic/pytest/%s/' % date3
config_file_source_dir = '/home/weblogic/config/source_list.txt'
config_file_node_dir = '/home/weblogic/config/node_list.txt'
config_file_report_nodes_dir = '/home/weblogic/config/report_nodes_list.txt'
config_file_report_source_dir = '/home/weblogic/config/report_source_list.txt'
config_list_source = []
config_list_node = []
config_list_report_source = []
config_list_report_nodes = []
thread_list_node = []
thread_list_source = []
thread_list_report_source = []
thread_list_report_nodes = []
job_config_list_source = []
job_config_list_node = []
job_config_list_report_source = []
job_config_list_report_nodes = []
job_list = []


def update_and_backup_nodes(list1):
    ip = list1[1]
    path = list1[2]
    global local_update_file_dir
    module = list1[0]
    server_name = list1[2][-17:-10]
    back_path = list1[2][0:-18]
    date2 = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    command_bak = 'LANG="zh_CN.UTF-8";cd %s;tar -cvf %s_%s.tar.gz EAR %s' % (back_path, server_name, date2, server_name)
    command_del = 'cd %s;rm -rf %s.zip' % (path, module)
    command_unzip = 'cd %s;unzip -o %s.zip' % (path, module)
    command_del_tar = 'cd %s;rm -rf %s_*.tar.gz' % (back_path, server_name)
    finish_job = module + ' '+server_name
    
    widgets=[' ',"%s:" %finish_job, Percentage(),' ',Bar(marker='>',left='[',right=']')]
    pgb1 = ProgressBar(widgets=widgets,maxval=60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='weblogic', password='weblogic')
    pgb1.update(10)

    sftp = ssh.open_sftp()
    try:
        sftp.put('%s%s.zip' % (local_update_file_dir, module), '%s/%s.zip' % (path, module))
    except IOError:
        raise
    except Exception, e:
        logger.error('%s', local_update_file_dir, exc_info=True)
    pgb1.update(20)
    
    stdin, stdout, stderr = ssh.exec_command(command_del_tar)
    for line in stdout:
        logger.info('%s', line.strip('\n'))
        
    pgb1.update(30)
    stdin, stdout, stderr = ssh.exec_command(command_bak)
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(40)
    stdin, stdout, stderr = ssh.exec_command(command_unzip)
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(50)
    stdin, stdout, stderr = ssh.exec_command(command_del)
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(60)
    pgb1.finish()
    logger.info('*******finish update %s  *******', finish_job)


def update_and_backup_source(list3):
    ip = list3[1]
    module = list3[0]
    path = list3[2]
    date2 = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    global local_update_file_dir
    widgets=[' ',"%s:" %module, Percentage(),' ',Bar(marker='>',left='[',right=']')]
    pgb1 = ProgressBar(widgets=widgets,maxval=60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='weblogic', password='weblogic')
    pgb1.update(10)
    sftp = ssh.open_sftp()
    try:
        sftp.put('%s%s.zip' % (local_update_file_dir, module), '%s/%s.zip' % (path, module))
    except IOError:
        raise
    except Exception, e:
        logger.error('%s', local_update_file_dir, exc_info=True)
    pgb1.update(20)
    stdin, stdout, stderr = ssh.exec_command('cd %s;rm -rf %s_*.tar.gz' % (path, module))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(30)
    stdin, stdout, stderr = ssh.exec_command('LANG="zh_CN.UTF-8";cd %s;\
                          tar -cvf %s_%s.tar.gz EAR' % (path, module, date2))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(40)
    stdin, stdout, stderr = ssh.exec_command('LANG="zh_CN.UTF-8";cd %s;unzip -o %s.zip' % (path, module))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(50)
    stdin, stdout, stderr = ssh.exec_command('cd %s;rm -rf %s.zip' % (path, module))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(60)
    pgb1.finish()
    logger.info('*******finish update source %s  *******', module)

def update_and_backup_report_node(list4):
    date_3 = time.strftime('%Y%m%d%H%S', time.localtime(time.time()))
    new_path_list = []
    ip = list4[1]
    path = list4[2]
    module = list4[0]
    tmp_list = list4[2].split('/')
    global local_update_file_dir

    for ll in tmp_list:
        if len(ll) <> 0:
            new_path_list.append(ll)

    tarbag_name = new_path_list[5]
    back_path = '/' + '/'.join(new_path_list[0:5])
    widgets=[' ',"%s:" %module, Percentage(),' ',Bar(marker='>',left='[',right=']')]
    pgb1 = ProgressBar(widgets=widgets,maxval=60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='weblogic', password='weblogic')
    pgb1.update(10)
    sftp = ssh.open_sftp()
    try:
        sftp.put('%s%s.zip' % (local_update_file_dir, module), '%s/%s.zip' % (path, module))
    except IOError:
        raise
    except Exception, e:
        logger.error('%s', local_update_file_dir, exc_info=True)
    pgb1.update(20)
    stdin, stdout, stderr = ssh.exec_command('cd %s;rm -rf %s_*.tar.gz' % (back_path, tarbag_name))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(30)
    stdin, stdout, stderr = ssh.exec_command(
        'LANG="zh_CN.UTF-8";cd %s;tar -cvf %s_%s.tar.gz %s' % (back_path, tarbag_name, date_3, tarbag_name))
    for line in stdout:
         logger.info('%s', line.strip('\n'))

    pgb1.update(40)
    stdin, stdout, stderr = ssh.exec_command('LANG="zh_CN.UTF-8";cd %s;unzip -o %s.zip' % (path, module))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(50)
    stdin, stdout, stderr = ssh.exec_command('cd %s;rm -rf %s.zip' % (path, module))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(60)
    pgb1.finish()
    logger.info('*******finish update report node %s  *******',module+' '+tarbag_name)


def update_and_backup_report_source(list5):
    ip = list5[1]
    date4 = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    module = list5[0]
    path = list5[2]
    tmp_list1 = list5[2].split('/')
    new_path_list_1 = []
    global local_update_file_dir

    for ll in tmp_list1:
        if len(ll) <> 0:
            new_path_list_1.append(ll)
    tarbag_report_name = new_path_list_1[4]
    new_path = '/'.join(new_path_list_1[0:4])
    
    widgets=[' ',"%s:" %module, Percentage(),' ',Bar(marker='>',left='[',right=']')]
    pgb1 = ProgressBar(widgets=widgets,maxval=60)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username='weblogic', password='weblogic')
    pgb1.update(10)
    sftp = ssh.open_sftp()
    
    try:
        sftp.put('%s%s.zip' % (local_update_file_dir, module), '/%s/%s.zip' % (new_path, module))
    except IOError:
        raise
    except Exception, e:
        logger.error('%s', local_update_file_dir, exc_info=True)
    pgb1.update(20)
    stdin, stdout, stderr = ssh.exec_command('cd /%s;rm -rf %s_*.tar.gz' % (new_path, tarbag_report_name))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(30)
    stdin, stdout, stderr = ssh.exec_command('LANG="zh_CN.UTF-8";cd /%s;tar -cvf %s_%s.tar.gz %s' % (
        new_path, tarbag_report_name, date4, tarbag_report_name))
    for line in stdout:
        logger.info('%s', line.strip('\n'))

    pgb1.update(40)
    stdin, stdout, stderr = ssh.exec_command('LANG="zh_CN.UTF-8";cd /%s;unzip -o %s.zip' % (new_path, module))
    for line in stdout:
        logger.info('%s', line.strip('\n'))

    pgb1.update(50)
    stdin, stdout, stderr = ssh.exec_command('cd /%s;rm -rf %s.zip' % (new_path, module))
    for line in stdout:
        logger.info('%s', line.strip('\n'))
    pgb1.update(60)
    pgb1.finish()
    logger.info('*******finish update report source %s  *******', module)


if not os.path.exists(local_update_file_dir):
    os.mkdir(local_update_file_dir)

f1 = open(config_file_source_dir, 'rt')
while True:
    g = f1.readline()
    if len(g) == 0:
        break
    config_list_source.append(g.strip('\n').split(':'))
f1.close()

f2 = open(config_file_node_dir, 'rt')
while True:
    m = f2.readline()
    if len(m) == 0:
        break
    config_list_node.append(m.strip('\n').split(':'))
f2.close()

f3 = open(config_file_report_source_dir, 'rt')
while True:
    rep = f3.readline()
    if len(rep) == 0:
        break
    config_list_report_source.append(rep.strip('\n').split(':'))
f3.close()

f4 = open(config_file_report_nodes_dir, 'rt')
while True:
    rep_nodes = f4.readline()
    if len(rep_nodes) == 0:
        break
    config_list_report_nodes.append(rep_nodes.strip('\n').split(':'))
f4.close()

for job in os.listdir(local_update_file_dir):
    job_list.append(job[:-4])

for node_list in config_list_node:
    if node_list[0] in job_list:
        job_config_list_node.append(node_list)

for source_list in config_list_source:
    if source_list[0] in job_list:
        job_config_list_source.append(source_list)

for report_source in config_list_report_source:
    if report_source[0] in job_list:
        job_config_list_report_source.append(report_source)

for report_nodes in config_list_report_nodes:
    if report_nodes[0] in job_list:
        job_config_list_report_nodes.append(report_nodes)

if len(job_config_list_source) <> 0:
    for list2 in job_config_list_source:
        t1 = multiprocessing.Process(target=update_and_backup_source, args=(list2,))
        thread_list_source.append(t1)

    for thread1 in thread_list_source:
        thread1.start()

    for thread2 in thread_list_source:
        thread2.join()

if len(job_config_list_node) <> 0:
    for list3 in job_config_list_node:
        t2 = multiprocessing.Process(target=update_and_backup_nodes, args=(list3,))
        thread_list_node.append(t2)

    for thread3 in thread_list_node:
        thread3.start()

    for thread4 in thread_list_node:
        thread4.join()

if len(job_config_list_report_source) <> 0:
    for list5 in job_config_list_report_source:
        t3 = multiprocessing.Process(target=update_and_backup_report_source, args=(list5,))
        thread_list_report_source.append(t3)

    for thread5 in thread_list_report_source:
        thread5.start()

    for thread6 in thread_list_report_source:
        thread6.join()

if len(job_config_list_report_nodes) <> 0:
    for list6 in job_config_list_report_nodes:
        t4 = multiprocessing.Process(target=update_and_backup_report_node, args=(list6,))
        thread_list_report_nodes.append(t4)

    for thread7 in thread_list_report_nodes:
        thread7.start()

    for thread8 in thread_list_report_nodes:
        thread8.join()

print("OK,finish job")

   
