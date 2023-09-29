from .preprocessor import Preprocessor
from .tokenizer import Tokenizer
from .lexer import Lexer
from .parser import Parser
from .compiler import Compiler


class Template:
    def __init__(self, source: str) -> None:
        self.__source = source

    def render(self) -> str:
        preprocessor = Preprocessor(self.__source)
        preprocessed_template = preprocessor.preprocess()

        tokenizer = Tokenizer(preprocessed_template)
        tokens = tokenizer.get_tokens()

        lexer = Lexer(tokens)
        lexemes = lexer.get_lexems()

        parser = Parser(lexemes)
        ast = parser.get_ast()

        compiler = Compiler(ast)
        render = compiler.render_ast()
        return render
