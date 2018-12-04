#!/usr/bin/env python3
import subprocess
import os
import argparse

def clean(build_dir):
    subprocess.call('rm -r %s'%build_dir , shell=True)
    subprocess.call('mkdir -p %s'%build_dir, shell=True)



if __name__ == '__main__':
    bazel_version = '0.20.0'
    with_sudo = ''
    build_dir = 'bazel_build'
    FNULL = open(os.devnull, 'w')
    
    parser = argparse.ArgumentParser(description='Bazel Build')
    parser.add_argument(
        'command', type=str, nargs=1, metavar='<COMMAND>', help='specify a command, like build, compile, install or clean')
    args = parser.parse_args()

    print('command: ',args.command)
    command = args.command[0]
    if subprocess.call('which sudo', shell=True, stdout=FNULL) == 0:
        with_sudo = 'sudo '

    if command == 'clean':
        clean(build_dir)
    elif command == 'build':
        clean(build_dir)
        os.chdir(build_dir)
        subprocess.call('wget https://github.com/bazelbuild/bazel/releases/download/%s/bazel-%s-dist.zip' % (bazel_version, bazel_version), shell=True)
        subprocess.call('unzip bazel-%s-dist.zip' % (bazel_version), shell=True)
        subprocess.call('./compile.sh', shell=True)
    elif command == 'compile':
        os.chdir(build_dir)
        subprocess.call('./compile.sh', shell=True)
    elif command == 'install':
        os.chdir(build_dir)
        subprocess.call(with_sudo+' cp ./output/bazel /usr/local/bin/', shell=True)
        subprocess.call('bazel version', shell=True)
    else:
        print('Cannot recognize the command.')


