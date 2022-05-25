
#!/bin/bash

# In the root of the repo
source ./.venv/bin/activate;
cd src/tokenizer/prototype;   # so program.txt is in the cwd
python3 tokenizer.py --input-file ../examples/program.txt;