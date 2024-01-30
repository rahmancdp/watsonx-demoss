# __copyright__ = "Copyright (C) 2023 IBM Client Engineering US FSM Squad 12"
# __author__ = "Renate Hamrick, Boris Acha, and Ritu Patel"


def clean_assem_code(file_content):
  lines = file_content.splitlines()
  output = []

  for row in lines:
        row = row[0:72].rstrip()
        output.append(row)

  return output

def split_assem_code(file_content):
    chunks = []
    chunk = []
    current_size = 0

    for line in file_content:
            # Check if adding the current line exceeds the limit
            if current_size + len(line) > 6000:
                # Check if the line is a header
                if line[:8].strip():  # Assuming headers are non-blank in the first 8 chars
                    chunks.append(''.join(chunk))  # Add the current chunk to the list
                    chunk = [line +'\n']                 # Start a new chunk with the header
                    current_size = len(line)
                else:
                    chunk.append(line)
                    chunks.append(''.join(chunk))  # Add the chunk including the current line to the list
                    chunk = []
                    current_size = 0
            else:
                chunk.append(line+ '\n')
                current_size += len(line)

        # Add the last chunk if it's not empty
    if chunk:
        chunks.append(''.join(chunk))

    return chunks