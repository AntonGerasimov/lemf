import boto3
import os
import sys
import time
ami = 'ami-d93622b8'
#Amazon Linux AMI 2015.09.1 (PV) - ami-d93622b8
#The Amazon Linux AMI is an EBS-backed, AWS-supported image. The default image includes AWS command line tools, Python, Ruby, Perl, and Java. The repositories include Docker, PHP, MySQL, PostgreSQL, and other packages.

region = 'us-west-2'
key_name = 'Alexander-key-pair-Oregon'
sg = ['Alexander_SG_Oregon']
def init_session(r=None):
    return boto3.resource('ec2')

def create_inst(ami_):
    ec2 = init_session()
    ec2.create_instances(ImageId=ami_, MinCount=1, MaxCount=1, KeyName = key_name, SecurityGroupIds = sg, InstanceType = 't1.micro')

def list_of_inst():
    ret = []
    ec2 = init_session()
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        ret.append(instance.id)
    return ret

def list_of_dns():
    ret = []
    ec2 = init_session()
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        ret.append(instance.public_dns_name)
    return ret

def ls(): #show id and type of all lanched isntances
    ec2 = init_session()
    instances = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        print("Instance id = {0} Instance type = {1} DNS = {2}".format(instance.id, instance.instance_type, instance.public_dns_name)) 
    l = list_of_inst()
    if len(l)==0:
        print("No instances found")
     
def terminate_inst(inst_id):
    ec2 = init_session()
    ec2.instances.filter(InstanceIds=inst_id).terminate()

def terminate_all(): #terminate all launched instances. Need before to finish the program
    l = list_of_inst()
    for i in range(len(l)):
        ids = [l[i]]
        terminate_inst(ids)

def stop_inst(inst_id):
    ec2 = init_session()
    ec2.instances.filter(InstanceIds=inst_id).stop()

def stop_all(): #stop all launched instances. Need before to finish the program
    l = list_of_inst()
    for i in range(len(l)):
        ids = [l[i]]
        stop_inst(ids)

import paramiko

user = 'ec2-user' #'ec2-user'
key_file = '''Alexander-key-pair-Oregon.pem'''

exe_ = "rm *"
def add_exe(exe, text):
    return exe + "; " + text
file_ = "main.cc"

def text_(text, file_):
    return "echo '" + text + "' >>" + file_


#Есть файлик my_text.cc. В нем n строк. Мы n раз вызываем exe_ = add_exe(), поочередно добавляя строчки. В итоге получаем запись нужного нам файлика
f = open('base_my_text.cc')
n = len(f.readlines())
f.close()
f = open('base_my_text.cc')
for i in range(n):
    line = f.readline()
    n_ = len(line)
    line_ = ""
    for j in range(n_-1):
        line_ = line_ + line[j]    
    exe_ = add_exe(exe_, text_(line_, file_))
f.close()

def add_cat_file(exe, file_):
    return exe + "; g++ " + file_ + " -o task"


exe_ = add_cat_file(exe_,file_)
exe_ = add_exe(exe_, "./task")

print('###############################################')
print(exe_)
print('###############################################')

def connect_(dns_, n):
    print("Hi. It's just test. I am inst #", n, ". I am going to work now.")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(dns_, username=user, key_filename=key_file)
    return ssh

def install_(ssh):
    stdin, stdout, stderr = ssh.exec_command("sudo yum install gcc-c++ -y", get_pty = True)
    stdin.flush()
    data = stdout.read().splitlines()
    err = stderr.read().splitlines()
    for line in data:
        print (line)
    for line in err:
        print(line)
        
def execute_(ssh, exe_):
    stdin, stdout, stderr = ssh.exec_command(exe_, get_pty = True)
    stdin.flush()
    data = stdout.read().splitlines()
    err = stderr.read().splitlines()
    for line in data:
        print (line)
    for line in err:
        print(line)

def close_(ssh):
    ssh.close()
    
inst = create_inst(ami)
time.sleep(120)

dns = list_of_dns()
if(len(dns) != 0):
  ssh=connect_(dns[len(dns) - 1], 1)
  install_(ssh)
  execute_(ssh, exe_)
  close_(ssh)

#terminate_all()
