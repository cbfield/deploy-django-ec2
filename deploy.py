import sys,paramiko,argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Get Django Project Name')
    parser.add_argument('--project-name',required=True,action='store',dest='name')
    args = parser.parse_args()

    return args.name


def main():
    django_project_name = parse_arguments()

    #creation of ec2 node
    
    #connection to node
    key = paramiko.RSAKey.from_private_key_file("/home/chris/.ssh/EC2-2019-09-09.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname='34.216.29.209',username='ubuntu',pkey=key)

    stdin , stdout, stderr = client.exec_command('pwd')
    print(stdout.read())

if __name__ == '__main__':
    sys.exit(main())
