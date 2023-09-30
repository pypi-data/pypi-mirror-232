import argparse
import logging
import os

import funion
from funion.combine_contracts_advanced import handle_one_solidity_file
from funion.compile_contract import get_ast_root_node
from funion.combine_contracts import combine_involved_contracts

logger = logging.getLogger(__name__)



def register_basic_arguments(parser: argparse.ArgumentParser):
    # Define command-line arguments
    parser.add_argument('-p','--solidity_file_path', type=str, default="",
                        help="specify the path where Solidity files are held.")
    parser.add_argument('-n','--solidity_file_name', type=str, default="",
                        help="specify the name of the solidity file of the target contract.")

    parser.add_argument('-cn','--contract_name', type=str, help="specify the name of the target contract")
    parser.add_argument('-lv','--log_level', type=int, default=3)
    parser.add_argument('-sv','--solc_version', type=str, default="0.5.0", help="the compiler version of the target contract")
    parser.add_argument('-ip','--import_paths', nargs="+", type=str, default=[],
                        help="specify the paths that the dependent solidity files reside")

    parser.add_argument('-rp','--result_path', type=str, default="", help="the directory to save the merged solidity file.")

    parser.add_argument('-rc','--remove_comments', default=False, action='store_true')
    parser.add_argument('--advanced', default=False, action='store_true')
    parser.add_argument('-tp','--temp_path', type=str, default="")

    return parser


def set_logging_level(args):
    if args.log_level == 4:
        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )
    elif args.log_level == 5:
        logging.basicConfig(
            level=logging.ERROR,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )
    elif args.log_level==3:
        logging.basicConfig(
            level=logging.WARNING,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )
    else:
        logging.basicConfig(
            level=logging.info,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format='%(asctime)s [%(levelname)s]: %(message)s',  # Define the log message format
            datefmt='%Y-%m-%d %H:%M:%S'  # Define the date-time format
        )


def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="A simple script with command-line arguments.")

    parser = register_basic_arguments(parser)

    # Parse the command-line arguments
    args = parser.parse_args()
    if args.remove_comments:
        funion.combine_contracts.flag_remove_comments=True

    set_logging_level(args)

    solidity_file_path_name = args.solidity_file_path + args.solidity_file_name
    if os.path.exists(solidity_file_path_name):
        if args.advanced:
            handle_one_solidity_file(args.solidity_file_path, args.solidity_file_name, args.temp_path,args.result_path)
        else:
            try:
                logger.info("Prepare to combine")
                status=combine_involved_contracts(args.solidity_file_path,args.solidity_file_name,args.solc_version,args.import_paths,args.result_path)
                if status:
                    logger.info("combine files successfully.")
                else:
                    logger.info("fail to combine.")
            except Exception as e:
                logger.error("Fail to merge files")
                logger.error("Error message: {}".format(e))
                return
            # test the merged file
            try:
                logger.info("Prepare to test the merged file")
                get_ast_root_node(args.solidity_file_path,args.solidity_file_name,args.solc_version,args.import_paths)
                logger.info("The merged file can be compiled successfully.")
            except:
                logger.error("The merged file can not be compiled")

    else:
        logger.error("file does not exit: {}".format(solidity_file_path_name))



