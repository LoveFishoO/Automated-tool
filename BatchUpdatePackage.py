import os
import sys
import re
import subprocess as sp

import argparse

PYTHON = sys.executable


parser = argparse.ArgumentParser()
parser.add_argument('--exclude', type=str, default='',
                    help='Packages that do not require updates. e.g "package1 package2 ..."')
parser.add_argument('--extype', type=str, default='',
                    help='The type of package that does not need to be updated')

ARGS = parser.parse_args()


def update_pip():
    
    cmd = [PYTHON, '-m', 'pip install', '-U', 'pip']
    
    p = sp.Popen(' '.join(cmd), stdin=sp.PIPE,
                 stdout=sp.PIPE, shell=True)
    
    return None
    

def get_all_package():

    cmd = [PYTHON, '-m', 'pip list']
    p = sp.Popen(' '.join(cmd), stdin=sp.PIPE,
                stdout=sp.PIPE, shell=True)
    
    p_info = p.stdout.readlines()
    
    packages = []
    
    for info in p_info[2:]:
        
        packages.append(info.decode().split())

    return packages

def get_outdated_package():
    
    cmd = [PYTHON, '-m', 'pip list', '--outdated']
    p = sp.Popen(' '.join(cmd), stdin=sp.PIPE,
                 stdout=sp.PIPE, shell=True)

    p_info = p.stdout.readlines()

    packages = []

    for info in p_info[2:]:

        packages.append(info.decode().split())

    return packages

def update_package():
    
    outdated_packages = get_outdated_package()

    exclude_packages = ARGS.exclude.split()
    print(f'The packages that need to be excluded: {ARGS.exclude}')
    
    updated_packages = []
    roll_back_infos = []
    if ARGS.exclude:
        # Delete packages that do not need to be updated
        for outdated_package in outdated_packages:
            
            package = outdated_package[0]
            Type = outdated_package[-1]
            
            if package not in exclude_packages and Type != ARGS.extype:
                
                updated_packages.append(outdated_package)
    else:
        
        updated_packages = outdated_packages
    
    print(f'The packages that need to be updated:')
    for updated_info in updated_packages:
        
        print(f'{" ".join(updated_info)}')
    
    print('---------------------------------------') 
    for updated_package in updated_packages:

        Package, Version, Latest, Type = updated_package
        
        upcmd = [PYTHON, '-m', 'pip install', '-U', f'{Package}', '--user']
        
        up = sp.Popen(' '.join(upcmd), stderr=sp.PIPE, shell=True)
        
        # read error info
        err_infos = up.stderr.readlines()
        
        # need_install_package_dict = {}
        
        for err in err_infos:

            err_info = err.decode()

            # automatically detects whether there is a conflict
            if 'incompatible' in err_info:

                # roll back version
                rbcmd = [PYTHON, '-m', 'pip install', '-U',
                        f'{Package}=={Version}', '--user']

                rbp = sp.Popen(' '.join(rbcmd), stderr=sp.PIPE, shell=True)
                roll_back_infos.append([Package, Latest, Version])
                break
    
    for roll_back_info in roll_back_infos:
        
        package, latest, version = roll_back_info
        print(f'Roll back {package} version: {latest}->{version}')
        
    
        #     if 'not installed' in err_info:
        #         # TODO automatically install other dependency packages
                
        #         no_install_info_list = re.split('[, ]', err_info)

        #         try:
        #             idx = no_install_info_list.index('requires') + 1
        #         except ValueError:
        #             continue

        #         target_package = no_install_info_list[idx]

        #         if is_str_include_num(target_package):

        #             separator = ''

        #             for i in target_package:

        #                 if i == '<':
        #                     separator += '<'

        #                 if i == '=':
        #                     separator += '='

        #                 if i == '>':
        #                     separator += '>'

        #             target_package_name, target_package_version = target_package.split(
        #                 separator)

        #             if '=' in separator:

        #                 if target_package_name not in need_install_package_dict:

        #                     need_install_package_dict[target_package_name] = target_package_version

        #                     pass

        #                 else:

        #                     if '<' in separator:

        #                         if target_package_version <= need_install_package_dict[target_package_name]:
        #                             need_install_package_dict[target_package_name] = target_package_version

        #                     if '>' in separator:

        #                         if target_package_version >= need_install_package_dict[target_package_name]:
        #                             need_install_package_dict[target_package_name] = target_package_version

        #             else:
        #                 print(f'{target_package_name}:{target_package_version}')

        #         else:
        #             # TODO find target package info with other method
        #             continue

        #         pass

        # # install dependency package
        # for pack, pack_version in need_install_package_dict.items():

        #     install_cmd = [PYTHON, '-m', 'pip install',
        #                 f'{pack}=={pack_version}', '--user']

        #     install_p = sp.Popen(' '.join(install_cmd), stderr=sp.PIPE, shell=True)
                    
            
    return None

def is_str_include_num(s: str):
    
    for i in s:
        
        if i.isdigit():
            
            return True
    
    return False
    

if __name__ == '__main__':
    
    update_package()
