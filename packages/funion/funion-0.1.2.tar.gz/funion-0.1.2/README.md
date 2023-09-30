## Funion ##
Funion combines multiple involved Solidity files in one compilable and independent Solidity file.

This version reduces the burn of giving proper import paths to compile a Solidity file that imports dependent contracts or libraries. All the user need to do is to give the root paths of contract pools that the to-be-compiled Solidty file uses. In addition, it can support to handle a group of Solidity files together instead of one by one manually.

One use case is to obtain compilable Solidity files from a large number of Solidity files. 

## Use it as a  Pycharm project ##

#### 1, Create a new project in Pycharm by cloning this repository ####

#### 2, Create virtual environment and install dependent packages ####

#### 3, Path Configuration ####
In the config.py, provide the paths of the Solidity pools you want to obtain compilable Solidity files, the contract pools (collections) that the Solidity files to be compiled import, and other paths.

Here is an example. 
```
solidity_pool_path = "C:\\Users\\18178\\collected_contracts\\SmartContractDataset-main\\"
temp_path="C:\\Users\\18178\\PycharmProjects\\funion\\temp\\"
result_path="C:\\Users\\18178\\collected_contracts\\SmartContractDataset_processed\\"

# add contract pools that are used in the contracts in the solidity pool
openzeppelin_path='C:\\Users\\18178\\collected_contracts\\openzeppelin\\'
chainlink_path='C:\\Users\\18178\\collected_contracts\\chainlink\\'
uniswap_path='C:\\Users\\18178\\collected_contracts\\uniswap\\'

contract_pool_name_path_map={
    "uniswap":uniswap_path,
    "chainlink":chainlink_path,
    "openzeppelin":openzeppelin_path,
}
```
**solidity_pool_path**: specifies the path that contains the Solidity files you want to get compilable independent Solidity files.

**temp_path**: used to temporarily store file data during the the combining process. 

**result_path**: holds the compilable Solidity files.

**openzeppelin_path**: specifies the path to the Openzeppelin contracts pool. 

**chainlink_path** and **uniswap_path** specify the paths to Chainlink and Uniswap pools respectively.

**contract_pool_name_path_map**: this map is critical to attach a keyword to a contract pool.

#### 4, run combine_contracts_advanced.py ####

Here is an example of terminal output:
```
**** EminenceCurrency.sol:0.5.17 ****
	 C:\Users\18178\collected_contracts\SmartContractDataset-main\SmartContractDataset-main\soliditySourceCodes\bonding-curve\EminenceCurrency.sol.
	 need to combine ['EminenceCurrencyHelpers.sol'].
	C:\Users\18178\collected_contracts\SmartContractDataset-main\SmartContractDataset-main\soliditySourceCodes\bonding-curve\EminenceCurrencyHelpers.sol
	 combined successfully to C:\Users\18178\collected_contracts\SmartContractDataset_processed\EminenceCurrency.sol.
	 test: success: the combined file C:\Users\18178\collected_contracts\SmartContractDataset_processed\EminenceCurrency.sol can be compiled

**** EminenceCurrencyBase.sol:0.5.17 ****
	 C:\Users\18178\collected_contracts\SmartContractDataset-main\SmartContractDataset-main\soliditySourceCodes\bonding-curve\EminenceCurrencyBase.sol.
	 need to combine ['EminenceCurrencyHelpers.sol'].
	C:\Users\18178\collected_contracts\SmartContractDataset-main\SmartContractDataset-main\soliditySourceCodes\bonding-curve\EminenceCurrencyHelpers.sol
	 combined successfully to C:\Users\18178\collected_contracts\SmartContractDataset_processed\EminenceCurrencyBase.sol.
	 test: success: the combined file C:\Users\18178\collected_contracts\SmartContractDataset_processed\EminenceCurrencyBase.sol can be compiled

**** EminenceCurrencyHelpers.sol:0.5.17 ****
	 C:\Users\18178\collected_contracts\SmartContractDataset-main\SmartContractDataset-main\soliditySourceCodes\bonding-curve\EminenceCurrencyHelpers.sol.
	 no need to combine as there is no import file.
```
 
## Use it in command line ##
In this case, right now, Funion only supports to deal with one Solidity file at a time and you still need to set up the paths of contract pools that the Solidity file requires.

Install it using pip
```
pip install funion
```
command:
```
merge --advanced -p path-to-solidity-file -n file-name -tp path-of-temp-folder -rp path-to-save-results

```
Note that you do not need to specify the compiler version. Funion will extract from Solidity files.