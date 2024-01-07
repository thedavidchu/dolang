import os

from compiler.lol import LolModule


def lol_compile(input_file: str, output_dir: str = "results"):
    print(f"> Compiling '{input_file}'")
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


def main():
    for x in os.listdir('examples'):
        file_name = os.path.join("examples", x)
        if os.path.isfile(file_name):
            lol_compile(file_name)


if __name__ == "__main__":
    main()
