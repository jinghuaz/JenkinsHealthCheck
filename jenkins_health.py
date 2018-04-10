#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Jinghua Zhou
Usage: python jenkins_health.py &
Description: listen to jenkins health status
Version: 1.0
"""

import jenkins
import time
import psutil
import os

server = jenkins.Jenkins('http://jenkins.patsnap.com', timeout=5, username='jinghua.zhou', password='b347cc964b0f62591415c360b0c6bac9')


def check():
    try:
        print 'Execution Check...'
        server.build_job('health_check_jenkins')
        time.sleep(60)
        last_build_number = server.get_job_info('health_check_jenkins')['lastCompletedBuild']['number']
        print last_build_number
        build_info = server.get_build_info('health_check_jenkins', last_build_number)
        print build_info.get('result')
        if build_info.get('result') == 'SUCCESS':
            print 'Health Check Pass!'
        else:
            kill()
    except:
        kill()

def kill():
    a = 'kill jenkins pid ' + time.asctime( time.localtime(time.time()) )
    f = open('/tmp/jenkins_restart.log','a')
    print >> f, a
    f.close()
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if pinfo.get('name') == 'java':
                jenkins_pid = pinfo.get('pid')
                cmd = 'kill -9 ' + jenkins_pid
                os.system(cmd)
                time.sleep(10)
                # start jenkins
                cmd = 'cd /data && nohup java -Duser.timezone=Asia/Shanghai -Xmx12G -Xms8G -Xmn8G -XX:MaxPermSize=2G -XX:+UseConcMarkSweepGC -jar jenkins.war --httpPort=80 1>/dev/null 2>/data/jenkins/log &'
                os.system(cmd)
        except psutil.NoSuchProcess:
            print 'Jenkins not started'

if __name__ == '__main__':
    while True:
        check()
        time.sleep(300)
