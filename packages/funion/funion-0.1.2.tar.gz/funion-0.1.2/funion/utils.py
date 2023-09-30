import os
import re


def read_a_file(file_path):
    return open(file_path, 'r', encoding="utf-8").read()



def remove_comments(input_str):
    # Remove single-line comments (// ...)
    input_str = re.sub(r'\/\/.*', '', input_str)

    # Remove multi-line comments (/* ... */)
    input_str = re.sub(r'\/\*.*?\*\/', '', input_str, flags=re.DOTALL)

    # Remove unnecessary space lines
    input_str = re.sub(r'\n\s*\n', '\n', input_str, flags=re.MULTILINE)

    return input_str


def remove_import_statements(file_content:str)->str:
    # Define the regular expression pattern to match import statements
    import_pattern = r'^\s*import\s+[^\n\r;]+[;\n\r]'
    # Remove import statements from the Solidity code
    cleaned_code = re.sub(import_pattern, '', file_content, flags=re.MULTILINE)

    return cleaned_code


def replace_import_statements(solidity_file_path:str, replacement_content:str,dest_path:str):

    # Read the content of the Solidity file
    with open(solidity_file_path, 'r', encoding='utf-8') as file:
        solidity_code = file.read()
    file.close()

    # Define a regular expression pattern to match import statements
    import_pattern = r'^\s*import\s[^;]+;\s*$'

    # Use re.sub to replace import statements with the provided content
    modified_solidity_code = re.sub(import_pattern, replacement_content, solidity_code, flags=re.MULTILINE)

    # Write the modified code back to the file
    with open(dest_path, 'w',encoding='utf-8') as file:
        file.write(modified_solidity_code)
    file.close()

    print("Import statements replaced successfully.")


def comment_out_import_statements_and_add_new_one(solidity_file_path:str, replacement_content:str, dest_path:str):
    # Read the content of the Solidity file
    with open(solidity_file_path, 'r', encoding='utf-8') as file:
        solidity_code = file.read()
    file.close()

    # # Define the regular expression pattern to match import statements
    # import_pattern = r'^\s*import\s+[^\n\r;]+[;\n\r]'
    # # Remove import statements from the Solidity code
    # # cleaned_code = re.sub(import_pattern, '', solidity_code, flags=re.MULTILINE)
    #
    # import_pattern = r'\s*import\s[^;]+;\s*'
    # commented_solidity_code = re.sub(import_pattern, lambda x: "// " + x.group(), solidity_code, flags=re.MULTILINE)
    # commented_solidity_code = re.sub(import_pattern, lambda x: "// " + x.group(), solidity_code, flags=re.MULTILINE)

    # Split the Solidity code into lines
    lines = solidity_code.split('\n')

    # Create a flag to determine if we are inside an import statement
    inside_import = False

    # Iterate through the lines and comment out import statements
    for i, line in enumerate(lines):
        if line.strip().startswith("import "):
            inside_import = True
            lines[i] = "// " + line  # Comment out the import statement
        elif inside_import and line.strip() == "":
            inside_import = False  # Stop commenting out when a blank line is encountered

    # Join the modified lines back into a single string
    commented_solidity_code = '\n'.join(lines)


    modified_code=replacement_content+commented_solidity_code
    # Write the modified code back to the file
    with open(dest_path, 'w', encoding='utf-8') as file:
        file.write(modified_code)
    file.close()





def extract_imported_content(file_path:str):
    # print(f'extract import files for file: {file_path}')
    with open(file_path, 'r',encoding='utf-8') as file:
        solidity_code = file.read()
    file.close()
    # Define a regular expression pattern to match import statements
    import_pattern = r'^\s*import\s[^;]+;\s*$'

    # Return the extracted imported content as a list
    imported_files = re.findall(r'^\s*import\s([^;]+);\s*$', solidity_code, flags=re.MULTILINE)
    return imported_files


def list_solidity_files(directory):
    solidity_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".sol"):
                solidity_files.append(os.path.join(root, file))
    return solidity_files

def get_file_items(file_path:str):
    if '\\' in file_path:
        file_path_items = str(file_path).split('\\')
    elif '/' in file_path:
        file_path_items = str(file_path).split('/')
    else:
        file_path_items = file_path
    return file_path_items

def extract_solc_version(file_path):
    try:
        with open(file_path, 'r',encoding="utf-8") as solidity_file:
            file_contents = solidity_file.read()

            # Use a regular expression to extract the Solc version from the pragma statement
            pragma_match = re.search(r'pragma solidity (\^?0\.\d+\.\d+);', file_contents)
            if pragma_match:
                result=pragma_match.group(1)
                if '^' in result:
                    return result.strip('^')
                else:return result

            else:
                pragma_match = re.search(r'pragma solidity (>=?0\.\d+\.\d+);', file_contents)
                if pragma_match:
                    result = pragma_match.group(1)
                    if '>=' in result:
                        return result.strip('>=')
                    else:
                        return result
                else:
                    match = re.search(r'pragma\s+solidity\s+>=([\d.]+)\s?.*',file_contents)

                    if match:
                        return match.group(1)
                    else:return None


    except FileNotFoundError:
        # Handle the case where the file does not exist
        print(f'Solc extraction faces FileNotFoundError: {file_path}')
        return None
    except UnicodeDecodeError:
        print(f'Solc extraction facesUnicodeDecodeError: {file_path}')
        return None
    except OSError as e:
        print(f'Solc extraction OSError:{e.strerror}:{file_path}')
        return None



def return_the_latest_solc_version(file_paths:list,given_solc_version:str)->str:
    versions=[given_solc_version]
    if len(file_paths)==0:return None
    for path in file_paths:
        versions.append(extract_solc_version(path))
    latest="0.0.0"
    latest_int=[0,0,0]
    # versions=['0.4.5','0.5.0','0.4.2']
    # versions = ['0.8.0', '0.5.2', '0.4.2']
    # versions = ['0.5.2', '0.8.4', '0.4.2']
    # versions = ['0.5.2', '0.4.2', '0.8.4']
    for version in versions:
        items=version.split('.')
        items=[int(e) for e in items]
        assert len(items)==3
        for (i,j) in zip(latest_int,items):
            if i<j:
                latest=version
                latest_int=items
                break
            elif i>j:
                break
            else:
                continue
    return latest

# results=extract_imported_content('C:\\Users\\18178\\collected_contracts\\openzeppelin\\contracts\\interfaces\\IERC165.sol')
# print(f'xxx')
#
