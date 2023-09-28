import json
from .tokenizer import Tokenizer
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler


class Template:
    def __init__(self, source: str) -> None:
        self.__source = source

    def render(self) -> str:
        tokenizer = Tokenizer(self.__source)
        tokens = tokenizer.get_tokens()

        lexer = Lexer(tokens)
        lexemes = lexer.get_lexems()
        print(lexemes)

        parser = Parser(lexemes)
        ast = parser.get_ast()
        print(json.dumps(ast, ensure_ascii=False, indent=2))

        compiler = Compiler(ast)
        render = compiler.render_ast()
        return render
