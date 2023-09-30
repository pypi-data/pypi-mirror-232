
import os
import shutil
from copy import deepcopy

from config import solidity_pool_path, result_path, temp_path, contract_pool_name_path_map, file_index, parameters
from funion.compile_contract import get_ast_root_node

from funion.combine_contracts import combine_involved_contracts

from funion.utils import get_file_items, extract_solc_version, extract_imported_content, \
    comment_out_import_statements_and_add_new_one


def collect_direct_import_file_paths_for_a_file(solidity_file_path_name:str):
    """
    return a list of import file paths and a bool indicating whether to consider this file or not (because some import files are not found)
    :param solidity_file_path_name:
    :return:
    """
    import_files_for_a_file = extract_imported_content(solidity_file_path_name)

    # get aboluste paths for import files
    new_import_content=""
    # get the absolute path for each import file
    clean_files = []
    divider = "\\"
    flag_consider =True # indicate whether to consider this file as some of its imported file is not available

    if len(import_files_for_a_file) > 0:
        file_path_items = get_file_items(solidity_file_path_name)

        for file in import_files_for_a_file:
            file=file[0:file.rindex('.sol')+4]
            complete_path = ""
            imported_contract_names = ""
            if "@" in file:
                for contract_pool_name in ["openzeppelin","chainlink",'uniswap']:
                    if "@{}".format(contract_pool_name) in file:
                        if 'from' in file:
                            first_idx = str(file).index('{')
                            last_idx = str(file).rindex('}')
                            imported_contract_names = file[first_idx + 1:last_idx]

                        complete_path = contract_pool_name_path_map[contract_pool_name] # begin with the path of pool
                        f_name = str(file).split("@{}".format(contract_pool_name))[-1]
                        f_name = f_name.strip('"')
                        file_items = get_file_items(f_name)
                        for item in file_items[0:-1]:
                            if len(item) == 0: continue
                            complete_path += item + divider
                        complete_path += file_items[-1]
                        if len(imported_contract_names) > 0:
                            new_import_content += "import {"+f"{imported_contract_names}"+"}"+" from \"./{}\";\n".format(file_items[-1])
                        else:
                            new_import_content += "import \"./{}\";\n".format(file_items[-1])

                        break
            else:
                imported_contract_names = ""
                if 'from' in file:
                    first_idx=str(file).index('{')
                    last_idx=str(file).rindex('}')
                    imported_contract_names=file[first_idx+1:last_idx]
                    file = file.split('from ')[-1]

                file = file.strip('"')
                file_items = get_file_items(file)

                go_back_index =0
                for item in file_items[0:-1]:  # the last is the file name, need to check
                    if len(item) == 0: continue
                    if item == '..':
                        if go_back_index==0:
                            go_back_index=-2
                        else:go_back_index-=1
                    elif item == '.':
                        go_back_index = -1
                        break
                    else:
                        # assume that ../ only appears as prefix (not in an interleaved way)
                        break

                if go_back_index == 0:
                    # case of "xxxx/xxx.sol", assuming that x
                    flag_consider = False
                    print(f'\t unknown: the import file: {file}.')
                    break
                else:
                    # add the shared path between the imported path and the target file
                    for e in file_path_items[0:go_back_index]:
                        complete_path += e + divider

                # add the sub-path leading to the imported file
                for item in file_items[0:-1]:
                    if len(item) == 0: continue
                    if str(item) not in ['.', '..']:
                        complete_path += item + divider

                # add the imported file name
                complete_path += file_items[-1]
                if len(imported_contract_names)>0:
                    new_import_content+="import {"+f"{imported_contract_names}"+"}"+" from \"./{}\";\n".format(file_items[-1])
                else: new_import_content+="import \"./{}\";\n".format(file_items[-1])

            if not os.path.exists(complete_path):
                print(f'\t does not exits: import file {complete_path}.')
                flag_consider=False
            else:
                clean_files.append("{}#{}".format(complete_path,file_items[-1]))

    if not flag_consider:
        return clean_files,new_import_content,False

    return clean_files,new_import_content,True


def put_related_solidity_files_together(solidity_file_path:str, solidity_file_name:str, my_temp_path:str):
    """
    put all the imported files required by the given solidity file together for compilation
    :param solidity_file_path:
    :param solidity_file_name:
    :param dest_path:
    :return:
    """

    file_path_name = os.path.join(solidity_file_path, solidity_file_name)
    flag_consider = True

    # get import files
    import_files_and_name, new_import_con, consider = collect_direct_import_file_paths_for_a_file(file_path_name)

    if not consider:
        # do not consider as some  import files are not found
        return [item.split('#')[-1] for item in import_files_and_name],[item.split('#')[0] for item in import_files_and_name],False


    if len(import_files_and_name) > 0:
        try:
            # Create the folder temp
            if os.path.exists(my_temp_path):
                shutil.rmtree(my_temp_path)
            os.makedirs(my_temp_path)

            # rewrite import statements and put it in a temp directory
            all_import_names = []
            all_import_file_paths = []
            for item in import_files_and_name:
                name = item.split('#')[-1]
                path = item.split('#')[0]
                all_import_file_paths.append(path)
                all_import_names.append(name)

            comment_out_import_statements_and_add_new_one(file_path_name, new_import_con,
                                                          my_temp_path + solidity_file_name)

            # go through the import files of the imported files
            work_list = deepcopy(import_files_and_name)
            while len(work_list) > 0:
                file_and_name = work_list.pop(0)
                file = file_and_name.split('#')[0]
                name = file_and_name.split('#')[-1]

                grand_import_files_and_names, grand_new_import_con, grand_consider = collect_direct_import_file_paths_for_a_file(
                    file)
                if not grand_consider:
                    flag_consider = False
                    break

                # rewrite import statements and put it in a temp directory
                # update the work list
                for item in grand_import_files_and_names:
                    f_name = item.split('#')[-1]
                    f_path = item.split('#')[0]
                    if f_name not in all_import_names:
                        if f_name == solidity_file_name:
                            print(
                                f'\t the imported file {name} imports back the file {solidity_file_name} that imports it, causing import cycle.')
                            flag_consider = False
                            break
                        all_import_names.append(f_name)
                        work_list.append(item)
                        all_import_file_paths.append(f_path)
                    else:
                        # handle a case: a solidity file may import another solidity file with the same but different paths

                        if f_path not in all_import_file_paths:
                            work_list.append(item)

                comment_out_import_statements_and_add_new_one(file, grand_new_import_con,
                                                              my_temp_path + name)

            if not flag_consider:
                return all_import_names,all_import_file_paths,False
            return all_import_names,all_import_file_paths,True

        except KeyError as e:
            print(f'KeyError')
        except shutil.SameFileError as e:
            print(f'shutil.SameFileError:{e.strerror}')
        except FileNotFoundError as e:
            print(f'File not found: {e.filename}')
            shutil.rmtree(my_temp_path)
        except:
            return [],[],False
    else:
        return [],[],True # no import file


def handle_solidity_pool(solidity_pool_dir:str,result_dir:str):
    file_index=0
    for root, _, files in os.walk(solidity_pool_dir):
        for solidity_file_name in files:
            if solidity_file_name.endswith(".sol"):
                file_index+=1
                file_path_name=os.path.join(root,solidity_file_name)

                solc_version = extract_solc_version(file_path_name)
                if solc_version is None:
                    solc_version = "0.5.0"
                print(f'\n**** {solidity_file_name}:{solc_version} ****')
                print(f'\t {file_path_name}.')

                my_temp_path=temp_path+solidity_file_name+"\\"
                # put related files in a temp directory
                import_names,import_files,consider=put_related_solidity_files_together(root,solidity_file_name,my_temp_path)

                if not consider:
                    print("\t not considered.")
                    continue

                if len(import_files)==0:
                    print(f'\t no need to combine as there is no import file.')
                    shutil.copy(file_path_name,
                                os.path.join(result_dir, "{}".format(solidity_file_name)))
                else:
                    print(f'\t need to combine {import_names}.')
                    for path in import_files:
                        print(f'\t{path}')

                    # # the use the latest version
                    # solc_version_new = return_the_latest_solc_version(import_files,solc_version)
                    # if not solc_version.__eq__(solc_version_new):
                    #     print(f'\t use the latest solc version {solc_version_new} among imported files.')
                    # solc_version = solc_version_new

                    # compile contracts in temp folder
                    com_status=combine_involved_contracts(my_temp_path, solidity_file_name, solc_version,
                                               [my_temp_path], result_dir)
                    if com_status:
                        # test the combined file
                        nodes, file_content=get_ast_root_node(result_dir, solidity_file_name, solc_version, [])
                        if nodes is not None:
                            print(f'\t test: success: the combined file {result_dir}{solidity_file_name} can be compiled')
                        else:
                            print(f'\t test: failure: the combined file {result_dir}{solidity_file_name} can not be compiled')

                    # Delete the folder and its contents
                    shutil.rmtree(my_temp_path)


def handle_one_solidity_file(solidity_file_path:str,solidity_file_name:str, temp_path:str, result_dir: str):


        file_path_name = os.path.join(solidity_file_path, solidity_file_name)

        solc_version = extract_solc_version(file_path_name)
        if solc_version is None:
            solc_version = "0.5.0"
        print(f'**** {solidity_file_name}:{solc_version} ****')
        print(f'\t {file_path_name}')

        my_temp_path = temp_path + solidity_file_name + "\\"
        # put related files in a temp directory
        import_names, import_files, consider = put_related_solidity_files_together(solidity_file_path,solidity_file_name,
                                                                                   my_temp_path)

        if not consider:
            print("\t not considered.")
            return

        if len(import_files) == 0:
            print(f'\t no need to combine as there is no import file.')
            shutil.copy(file_path_name,
                        os.path.join(result_dir, "{}".format(solidity_file_name)))
        else:
            print(f'\t need to combine solidity file(s): {import_names}.')
            print(f'\t the paths of solidity file(s): ')
            for path in import_files:
                print(f'\t   {path}')

            # # the use the latest version
            # solc_version_new=return_the_latest_solc_version(import_files)
            # if not solc_version.__eq__(solc_version_new):
            #     print(f'\t use the latest solc version {solc_version_new} among imported files.')
            # solc_version=solc_version_new

            # compile contracts in temp folder
            combine_involved_contracts(my_temp_path, solidity_file_name, solc_version,
                                       [my_temp_path], result_dir)

            get_ast_root_node(result_dir, solidity_file_name, solc_version, [])

        # # Delete the folder and its contents
        # shutil.rmtree(my_temp_path)


if __name__=="__main__":
    # # deal with individual Solidity files
    # solidity_file_path=parameters[file_index][0]
    # solidity_file_name=parameters[file_index][1]
    # handle_one_solidity_file(solidity_file_path,solidity_file_name,temp_path,result_path)

    # handle a group Solidity files
    handle_solidity_pool(solidity_pool_path,result_path)