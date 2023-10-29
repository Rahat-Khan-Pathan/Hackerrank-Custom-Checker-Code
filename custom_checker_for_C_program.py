# Start of BODY
# Python 3 Code
'''
TestStruct::
testcase_id                   [int] ID of the test-case
testcase_input_path           [str] File path to test-case input
testcase_output_path          [str] File path to test-case output generated by the problem solver
testcase_expected_output_path [str] File path to test-case expected output to be matched with
testcase_error_path           [str] File path to test-case STDERR
metadata_file_paths           [list<str>] File paths to Question metadata (Extra files usually used for defining traning sets)
submission_code_path          [str] File path to submission source code
submission_language           [str] Language token of submission
testcase_result               [bool] Set to True if test-case output matches test-case expected output. Matching is done line by line
testcase_signal               [int] Exit code of the test-case process
testcase_time                 [float] Time taken by the test-case process in seconds
testcase_memory               [int] Peak memory of the test-case process determined in bytes
data                          [str] <Future use>
ResultStruct::
result      [bool]  Assign test-case result. True determines success. False determines failure
score       [float] Assign test-case score. Normalized between 0 to 1
message     [str] Assign test-case message. This message is visible to the problem solver
'''

import re
def run_custom_checker(t_obj, r_obj):
    # Initialize the result to False by default
    r_obj.result = False
    r_obj.score = 0.0

    # If the result is already false, no need to check further. Just update the message
    if t_obj.testcase_result == False:
        r_obj.message = "Wrong Answer"
        return

    try:
        with open(t_obj.submission_code_path, "r") as code_file:
            code_contents = code_file.read()
            # remove all comments from the source code
            comment_pattern = r'//.*|/\*[\s\S]*?\*/'
            code_contents = re.sub(comment_pattern, '', code_contents) 

            # extract define statements and their definitions for data types
            define_pattern = r'#\s*define\s+(\w+)\s+([^#\n]+)'
            define_matches = re.findall(define_pattern, code_contents)
            define_dict = {name: value.strip() for name, value in define_matches}
            def replace_macros(match):
                macro_name = match.group(0)
                if macro_name in define_dict:
                    return define_dict[macro_name]
                return match.group(0)
            code_contents = re.sub(r'\b\w+\b', replace_macros, code_contents)

            # extract typedef statements and their definitions for data types
            typedef_dict = {}
            typedef_pattern = r'typedef\s+([\w\s]+)\s+(\w+);'
            matches = re.findall(typedef_pattern, code_contents, re.DOTALL)
            for match in matches:
                typedef_dict[match[1]] = match[0].strip()
            def replace_typedefs(match):
                typedef_alias = match.group(1)
                if typedef_alias in typedef_dict:
                    return typedef_dict[typedef_alias]
                return match.group(0)
            code_contents = re.sub(r'\b(\w+)\b', replace_typedefs, code_contents)

            function_name = "intcount_before_one("
            function_name2 = "longlongcount_before_one("
            function_name3 = "longlongintcount_before_one("
            # removed all spaces from line to check
            code_without_spaces = re.sub(r'\s', '', code_contents)
            if function_name in code_without_spaces or function_name2 in code_without_spaces or function_name3 in code_without_spaces: 
                # the function is found in the source code
                code_lines = code_contents.split('\n')
                inside_main = False
                br_found = False
                found=False
                stack = []
                function_call_name = "count_before_one("
                # now check if the function was called inside the main function 
                for line in code_lines:
                    if "main(" in line:
                        inside_main = True
                    if inside_main:
                        if len(stack)==0 and br_found==True:
                            break
                        if function_call_name in re.sub(r'\s', '', line): # removed all spaces from line to check 
                            # the caller function is found inside the scope of main function 
                            r_obj.message = "Success"
                            r_obj.result = True
                            r_obj.score = 1.0
                            found=True
                            break
                        if '{' in line:
                            stack.append('{')
                            br_found=True
                        if '}' in line:
                            stack.pop()
                if found == False:
                    r_obj.message = "The 'count_before_one()' function is not called inside the main function."
                    
            else:
                r_obj.message = "The 'count_before_one()' function is not defined correctly in the code."

    except Exception as e:
        r_obj.message = f"Error reading files or running the submitted code: {str(e)}"


# End of BODY