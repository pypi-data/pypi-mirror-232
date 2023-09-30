import logging

from funion.compile_contract import get_all_AST_nodes
from funion.utils import read_a_file, remove_import_statements, remove_comments

flag_remove_comments=False
logger = logging.getLogger(__name__)

def get_contract_dependencies(all_AST_nodes: list):
    """
    collect the dependency among contracts from ast nodes
    :param all_AST_nodes:
    :return:
    """
    contract_dependency = {}
    contract_paths = {}
    paths_to_contracts={}
    for node in all_AST_nodes:
        paths_dict = {}
        if hasattr(node, 'absolutePath'):
            solidity_absolute_path = node.absolutePath
            paths_to_contracts[solidity_absolute_path]=[]
            paths_dict['contract_path'] = solidity_absolute_path
        contract_name = ''

        if hasattr(node, 'nodes'):
            for node_child in node.nodes:
                if hasattr(node_child, 'nodeType'):
                    if node_child.nodeType == 'ContractDefinition':
                        contract_name = node_child.name
                        paths_to_contracts[solidity_absolute_path].append(contract_name)
                        # get its dependent contracts
                        if hasattr(node_child, 'dependencies'):
                            contract_dependency[node_child.name] = []
                            for dp_con in node_child.dependencies:
                                if hasattr(dp_con, 'name'):
                                    contract_dependency[contract_name].append(dp_con.name)
                    elif node_child.nodeType == 'ImportDirective':
                        if hasattr(node_child, 'absolutePath'):
                            path = node_child.absolutePath
                            if 'import_path' not in paths_dict.keys():
                                paths_dict['import_path'] = [path]
                            else:
                                paths_dict['import_path'].append(path)
        if len(contract_name) > 0:
            contract_paths[contract_name] = paths_dict
    return contract_dependency, contract_paths,paths_to_contracts


def order_contracts(inter_contract_dependency: dict) -> list:
    """
    example:
        {'Ownable': ['Context'],
         'IERC20': [],
         'IERC20Permit': [],
         'SafeERC20': ['Address', 'IERC20'],
         'Address': [],
         'Context': [],
         'VestingWallet': ['Address', 'Context', 'IERC20', 'Ownable', 'SafeERC20']
         }
    :param inter_contract_dependency:
    :return:
    """

    left_contracts = list(inter_contract_dependency.keys())
    # get contracts that have no base contracts
    ordered_contracts = [con for con in left_contracts if len(inter_contract_dependency[con]) == 0]
    # get the left behind contracts
    left_contracts = [con for con in left_contracts if con not in ordered_contracts]

    # to-do: this while loop can be infinite
    records={}
    while len(left_contracts) > 0:
        target = left_contracts.pop(0)
        dependents = inter_contract_dependency[target]
        items=[item for item in dependents if item not in ordered_contracts]
        if len(items) == 0:
            # mean all the base contracts are already found and included in the ordered list
            ordered_contracts.append(target)
        else:
            # need to reconsider this contract and put it at the end of the work list.

            if target not in records.keys():
                records[target]=1
            else:
                records[target]+=1
            if records[target]>1:
                print(f'{target} depends on {items}, which can not be ordered')
                break
            left_contracts.append(target)
    return ordered_contracts


def merge_solidity_files(ordered_contracts: list, contract_paths: dict, paths_to_contracts:dict, merged_file_path: str):
    """
    merge the solidity files that have the contracts that should be combined
    :param ordered_contracts:
    :param contract_paths:
    :param paths_to_contracts:
    :param merged_file_path:
    :return:
    """
    try:
        # collect the paths of solidity files
        solidity_paths=[]
        for con_name in ordered_contracts:

            s_path=""
            if con_name not in contract_paths.keys():
                for path,contracts in paths_to_contracts.items():
                    if con_name in contracts:
                        s_path=path
                        break
            else:
                s_path = contract_paths[con_name]['contract_path']
            if len(s_path)>0:
                if s_path not in solidity_paths:
                   solidity_paths.append(s_path)

        # collect the contents of solidity files
        # all content of a solidity file is considered. even though may be one contract in them is used.
        # this should be considered later
        file_contents = []
        for s_path in solidity_paths:
            file_content = read_a_file(s_path)

            if flag_remove_comments:
                file_content=remove_comments(file_content)

            # Remove import statements from the Solidity code
            cleaned_code = remove_import_statements(file_content)

            file_contents.append(cleaned_code)

        with open(merged_file_path, "w",encoding="utf-8") as file_write:
            for content in file_contents:
                file_write.write(content + "\n")
        file_write.close()
        return True
    except:
        return False


def combine_involved_contracts(solidity_file_path:str, solidity_file_name:str, solc_version:str, import_paths:list,result_path:str,file_name_index:int=0):


    # get all related AST nodes

    nodes = get_all_AST_nodes(solidity_file_path, solidity_file_name, solc_version, import_paths)

    if nodes is None:
        return False

    # get the contract dependency
    contract_dependency, contract_paths,paths_to_contracts = get_contract_dependencies(nodes)
    logger.info(f'The dependency:{contract_dependency}')

    # order contracts based on the dependency
    ordered_contracts = order_contracts(contract_dependency)
    logger.info(f'The order of libraries or contracts:{ordered_contracts}')

    # merge contract file content based on the order of the contracts
    if file_name_index==0:
        final_file_path_and_name = result_path + "{}".format(solidity_file_name)
    else:
        final_file_path_and_name = result_path + "{}_{}".format(file_name_index,solidity_file_name)
    status=merge_solidity_files(ordered_contracts, contract_paths, paths_to_contracts, final_file_path_and_name)
    if status:
        print(f'\t combined successfully to {final_file_path_and_name}.')
        return True
    else:
        print(f'\t fail to combine files to {final_file_path_and_name}.')
        return False
