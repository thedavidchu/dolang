from prototype.analyzer.lol_analyzer_types import LolModule


class LolUserModule(LolModule):
    def __init__(self, name: str, raw_text: str):
        super().__init__(name, raw_text)

        # Add C and LOL builtins to C namespace and symbol table
        if name == "":
            self.add_lol_builtins()

    def add_lol_builtins(self):
        """
        NOTE: this adds these to only the top level module. We can only run
        this function once--otherwise, there will be duplicate int32 objects.
        """
        self._scope.add_to_scope(
            "int32", LolDataType("int32", alt_c_name="int")
        )
        self._scope.add_to_scope("str", LolDataType("str", alt_c_name="char *"))

    def add_builtin_func(self, name: str):
        if (
            name in self.c_namespace
            and self.c_namespace[name] != SymbolSource.C_STDLIB
        ):
            raise ValueError(
                f"user-defined symbol '{name}' already in "
                f"C namespace '{self.c_namespace}'"
            )
        self.c_namespace[name] = SymbolSource.C_STDLIB
        self.symbol_table[name] = LolFunction(name, is_builtin_c=True)

    def include_stdio(self, lol_alias: str):
        from prototype.analyzer.lol_analyzer_reserved_names import STDIO_H_NAMES

        lib_name = "<stdio.h>"
        if lib_name in self.c_includes:
            raise ValueError(
                f"module '{lib_name}' already in "
                f"C includes list '{self.c_includes}'"
            )
        self.c_includes.append(lib_name)
        # Ensure that all names within stdio.h are unique
        # NOTE: some C standard library names overlap without problem.
        # E.g. NULL, size_t, etc. We take care of that by checking the source
        # as well.
        for stdio_name in STDIO_H_NAMES:
            if stdio_name in self.c_namespace:
                if self.c_namespace[stdio_name] == SymbolSource.C_STDLIB:
                    continue
                else:
                    raise ValueError(
                        f"name '{stdio_name}' already in "
                        f"C namespace '{self.c_namespace}'"
                    )
            else:
                self.c_namespace[stdio_name] = SymbolSource.C_STDLIB
        # Check that the alias is unique in the symbol table too!
        if lol_alias in self.symbol_table:
            raise ValueError(
                f"name '{lol_alias}' already in "
                f"symbol table '{self.symbol_table}'"
            )
        stdio_namespace = LolModule(lol_alias, self._raw_text)
        stdio_namespace.add_builtin_func("printf")
        self.symbol_table[lol_alias] = stdio_namespace