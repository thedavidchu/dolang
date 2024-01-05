import argparse
import json
import os
import time
from typing import Any, Dict, List, Optional

from compiler.lexer.lol_lexer_types import Token
from compiler.parser.lol_parser_token_stream import TokenStream

from compiler.lexer.lol_lexer import tokenize
from compiler.parser.lol_parser import parse, LolParserModuleLevelStatement
from compiler.analyzer.lol_analyzer import analyze, LolAnalysisModule
from compiler.emitter.lol_emitter import emit_c


class LolSymbol:
    def __init__(self):
        self.type: Any = None
        self.definition: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, }


class LolModule:
    def __init__(self):
        # Metadata
        self.init_timestamp = time.time()

        self.text: str = ""
        self.tokens: List[Token] = []
        self.ast: List[LolParserModuleLevelStatement] = []
        self.module: Optional[LolAnalysisModule] = None
        self.code: Optional[str] = None
        self.output_language: Optional[str] = None

    def read_file(self, file_name: str):
        assert isinstance(file_name, str)
        with open(file_name) as f:
            self.text = f.read()

    ############################################################################
    ### LEXER
    ############################################################################

    def run_lexer(self):
        assert self.text != "", "LolModule"
        assert self.tokens == []

        self.tokens = tokenize(self.text)

    def save_lexer_output_only(self, output_dir: str):
        file_name: str = f"{output_dir}/{self.init_timestamp}-lexer-output-only.json"
        with open(file_name, "w") as f:
            json.dump({"lexer-output": [x.to_dict() for x in self.tokens]}, f, indent=4)

    ############################################################################
    ### PARSER
    ############################################################################

    def run_parser(self):
        assert self.tokens != []

        stream = TokenStream(self.tokens, self.text)
        self.ast = parse(stream)

    def save_parser_output_only(self, output_dir: str):
        file_name: str = f"{output_dir}/{self.init_timestamp}-parser-output-only.json"
        with open(file_name, "w") as f:
            json.dump({"parser-output": [x.to_dict() for x in self.ast]}, f, indent=4)

    ############################################################################
    ### ANALYZER
    ############################################################################

    def run_analyzer(self):
        self.module = analyze(self.ast, self.text)

    def save_analyzer_output_only(self, output_dir: str):
        assert isinstance(self.module, LolAnalysisModule)
        file_name: str = f"{output_dir}/{self.init_timestamp}-analyzer-output-only.json"
        with open(file_name, "w") as f:
            json.dump({"analyzer-output": {x: y.to_dict() for x, y in self.module.module_symbol_table.items()}}, f, indent=4)

    ############################################################################
    ### EMITTER
    ############################################################################

    def run_emitter(self):
        # TODO: Make this in the __init__function
        assert self.code is None and self.output_language is None
        self.code = emit_c(self.module)
        self.output_language = "c"

    def save_emitter_output_only(self, output_dir: str):
        assert isinstance(self.code, str) and self.output_language == "c"
        file_name: str = f"{output_dir}/{self.init_timestamp}-emitter-output-only.c"
        with open(file_name, "w") as f:
            f.write(self.code)



def main() -> None:
    parser = argparse.ArgumentParser()
    # TODO(dchu): make this accept multiple file names or folders. Also accept
    # a full configuration file.
    parser.add_argument(
        "-i", "--input", type=str, required=True, help="Input file name"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Output directory name"
    )
    args = parser.parse_args()

    # I explicitly extract the names because otherwise one may be tempted to
    # pass the 'args' namespace, which is always confusing.
    input_file = args.input
    output_dir = args.output

    module = LolModule()
    # Assume input_file is not None because it is required
    module.read_file(input_file)
    # Make empty output dir if it doesn't exist
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    module.run_lexer()
    module.save_lexer_output_only(output_dir)
    module.run_parser()
    module.save_parser_output_only(output_dir)
    module.run_analyzer()
    module.save_analyzer_output_only(output_dir)
    module.run_emitter()
    module.save_emitter_output_only(output_dir)


if __name__ == "__main__":
    main()
