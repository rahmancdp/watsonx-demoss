# __copyright__ = "Copyright (C) 2023 IBM Client Engineering US FSM Squad 12"
# __author__ = "Renate Hamrick, Boris Acha, and Ritu Patel"


import re
def split_py_code(file_contents, chunk_size=6000):
    code_chunks = []
    lines = file_contents.splitlines()
    current_chunk = ""

    for line in lines:
        # Check if adding the current line exceeds the chunk size
        if len(current_chunk) + len(line) > chunk_size:
            code_chunks.append(current_chunk)
            current_chunk = ""

        # Add the line to the current chunk
        current_chunk += line + "\n"

    # Add any remaining code to the last chunk
    if current_chunk:
        code_chunks.append(current_chunk)

    return code_chunks