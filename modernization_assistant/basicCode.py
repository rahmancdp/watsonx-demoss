import re
 

def split_basic_code(file_content):
    # Define regular expressions for subroutine name and code
    subroutine_pattern = re.compile(r'(\b\w+\b):([\s\S]*?)(?=\b\w+\b:|$)')
    # Find all subroutine matches in the BASIC code
    subroutine_matches = subroutine_pattern.findall(file_content)
    # Extract subroutine names and codes into arrays
    subroutine_names = [match[0] for match in subroutine_matches]
    subroutine_codes = [match[1].strip() for match in subroutine_matches]
    chunks = []
    basciStr = ""
    for name, code in zip(subroutine_names, subroutine_codes):
        if code.find(name+':') and code.find("RETURN") != -1:
         basciStr = ""
         cleaned_code = re.sub(r'REM.*$', '', code, flags=re.MULTILINE)
         basciStr += "Subroutine Name: " + name + '\n' + name + ":\n" + cleaned_code
         chunks.append(basciStr)

    chunks.append(file_content)
    return chunks 