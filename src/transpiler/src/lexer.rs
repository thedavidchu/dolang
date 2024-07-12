enum TokenType {
    /* Key Words */
    Function,
    Return,
    Import,
    Let,
    Const,

    /* Literals */
    String,
    Integer,

    /* Identifier */
    Identifier,

    /* Brackets and such */
    LeftParenthesis,
    RightParenthesis,
    LeftSquareBracket,
    RightSquareBracket,
    LeftBrace,
    RightBrace,

    /* Separators */
    Period,
    Comma,
    Set,    // := or = (still can't decide)
    Colon,
    Semicolon,
    Arrow,

    /* Operators */
    // NOTE Just the simple ones for now!
    Plus,
    Minus,
}

struct Token {
    type: TokenType,
    text: String,
    position: u32,
}

struct Lexer {
    tokens: Vec<Token>,
}

impl Lexer {
    fn run(input_text: String) {
        for (i, c) in input_text.chars().enumerate() {
            println!("{}: {}", i, c);
        }
    }
}
