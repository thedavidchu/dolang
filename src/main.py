import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from compiler.analyzer.lol_analyzer import analyze, LolAnalysisModule
from compiler.emitter.lol_emitter import emit_c
from compiler.lexer.lol_lexer import tokenize
from compiler.lexer.lol_lexer_types import LolToken
from compiler.parser.lol_parser import parse, LolParserModuleLevelStatement
from compiler.parser.lol_parser_token_stream import TokenStream


class LolSymbol:
    def __init__(self):
        self.type: Any = None
        self.definition: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
        }


class LolModule:
    def __init__(
        self,
        *,
        input_file: str,
        output_dir: str,
    ):
        # Metadata
        self.input_file = input_file
        self.output_dir = output_dir
        prefix, ext = os.path.splitext(os.path.basename(input_file))
        self.output_prefix = prefix

        self.text: str = ""
        self.tokens: List[LolToken] = []
        self.ast: List[LolParserModuleLevelStatement] = []
        self.module: Optional[LolAnalysisModule] = None
        self.code: Optional[str] = None
        self.output_language: Optional[str] = None

    def read_input_file(self):
        with open(self.input_file) as f:
            self.text = f.read()

    def setup_output_dir(self):
        # Make empty output dir if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    ############################################################################
    ### LEXER
    ############################################################################

    def run_lexer(self):
        assert self.text != "", "LolModule"
        assert self.tokens == []

        self.tokens = tokenize(Path(self.input_file))

    def save_lexer_output_only(self):
        file_name: str = (
            f"{self.output_dir}/{self.output_prefix}-{time.time()}-lexer-output-only.json"
        )
        with open(file_name, "w") as f:
            json.dump(
                {"lexer-output": [x.to_dict() for x in self.tokens]},
                f,
                indent=4,
            )

    ############################################################################
    ### PARSER
    ############################################################################

    def run_parser(self):
        assert self.tokens != []

        stream = TokenStream(self.tokens, self.text)
        self.ast = parse(stream)

    def save_parser_output_only(self):
        file_name: str = (
            f"{self.output_dir}/{self.output_prefix}-{time.time()}-parser-output-only.json"
        )
        with open(file_name, "w") as f:
            json.dump(
                {"parser-output": [x.to_dict() for x in self.ast]}, f, indent=4
            )

    ############################################################################
    ### ANALYZER
    ############################################################################

    def run_analyzer(self):
        self.module = analyze(self.ast, self.text)

    def save_analyzer_output_only(self):
        assert isinstance(self.module, LolAnalysisModule)
        file_name: str = (
            f"{self.output_dir}/{self.output_prefix}-{time.time()}-analyzer-output-only.json"
        )
        with open(file_name, "w") as f:
            json.dump(
                {
                    "analyzer-output": {
                        x: y.to_dict()
                        for x, y in self.module.module_symbol_table.items()
                    }
                },
                f,
                indent=4,
            )

    ############################################################################
    ### EMITTER
    ############################################################################

    def run_emitter(self):
        # TODO: Make this in the __init__function
        assert self.code is None and self.output_language is None
        self.code = emit_c(self.module)
        self.output_language = "c"

    def save_emitter_output_only(self):
        assert isinstance(self.code, str) and self.output_language == "c"
        file_name: str = (
            f"{self.output_dir}/{self.output_prefix}-{time.time()}-emitter-output-only.c"
        )
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
        "-o", "--output", type=str, default=".", help="Output directory name"
    )
    args = parser.parse_args()

    # I explicitly extract the names because otherwise one may be tempted to
    # pass the 'args' namespace, which is always confusing.
    input_file = args.input
    output_dir = args.output

    module = LolModule(input_file=input_file, output_dir=output_dir)
    module.read_input_file()
    module.setup_output_dir()

    module.run_lexer()
    module.save_lexer_output_only()
    module.run_parser()
    module.save_parser_output_only()
    module.run_analyzer()
    module.save_analyzer_output_only()
    module.run_emitter()
    module.save_emitter_output_only()


if __name__ == "__main__":
    main()
