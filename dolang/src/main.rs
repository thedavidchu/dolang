use std::env;
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Copy)]
struct Position {
    position: usize,
    line: usize,
    column: usize,
}

impl Position {
    fn new() -> Position {
        Position {
            position: 0,
            line: 1,
            column: 1,
        }
    }

    fn next_line(&mut self) {
        self.position += 1;
        self.line += 1;
        self.column = 1;
    }

    fn next_column(&mut self) {
        self.position += 1;
        self.column += 1;
    }

    fn next_column_step(&mut self, step: usize) {
        self.position += step;
        self.column += step;
    }

    fn to_csv_string(&self) -> String {
        let mut s: String = "".to_string();
        s.push_str(self.position.to_string().as_str());
        s.push_str(",");
        s.push_str(self.line.to_string().as_str());
        s.push_str(",");
        s.push_str(self.column.to_string().as_str());
        return s;
    }
}

struct StringLiteral {
    position: Position,
    raw_text: String,
    value: String,
}

struct IntegerLiteral {
    position: Position,
    raw_text: String,
    // TODO Use BigInt.
    value: i64,
}

struct FloatLiteral {
    position: Position,
    raw_text: String,
    // TODO Use arbitrary precision.
    value: f64,
}

struct CommentLiteral {
    position: Position,
    raw_text: String,
}

struct Identifier {
    position: Position,
    raw_text: String,
}

struct UnknownOpLiteral {
    position: Position,
    raw_text: String,
}

enum Token {
    /* IDK if this should be a literal or not. */
    LiteralComment(CommentLiteral),
    LiteralUnknownOp(UnknownOpLiteral),

    KeywordFunction(Position),
    KeywordStruct(Position),
    KeywordIf(Position),
    KeywordElse(Position),
    KeywordLet(Position),

    Identifier(Identifier),

    LiteralString(StringLiteral),
    LiteralInteger(IntegerLiteral),
    LiteralFloat(FloatLiteral),

    BracketLeftRound(Position),
    BracketRightRound(Position),
    BracketLeftSquare(Position),
    BracketRightSquare(Position),
    BracketLeftCurly(Position),
    BracketRightCurly(Position),

    Semicolon(Position),
    Comma(Position),

    OpNot(Position),
}

impl Token {
    fn get_position(&self) -> Position {
        match self {
            Token::KeywordFunction(pos) => pos,
            Token::KeywordStruct(pos) => pos,
            Token::KeywordIf(pos) => pos,
            Token::KeywordElse(pos) => pos,
            Token::KeywordLet(pos) => pos,
            Token::Identifier(id) => &id.position,
            /* Literals */
            Token::LiteralString(lit) => &lit.position,
            Token::LiteralInteger(lit) => &lit.position,
            Token::LiteralFloat(lit) => &lit.position,
            /* Comment */
            Token::LiteralComment(lit) => &lit.position,
            Token::LiteralUnknownOp(lit) => &lit.position,
            /* Brackets */
            Token::BracketLeftRound(pos) => pos,
            Token::BracketRightRound(pos) => pos,
            Token::BracketLeftSquare(pos) => pos,
            Token::BracketRightSquare(pos) => pos,
            Token::BracketLeftCurly(pos) => pos,
            Token::BracketRightCurly(pos) => pos,
            /* Non-repeating punctuation */
            Token::Semicolon(pos) => pos,
            Token::Comma(pos) => pos,
            /* Possbily repeating punctuation */
            Token::OpNot(pos) => pos,
        }
        .clone()
    }

    fn to_raw_text(&self) -> String {
        match self {
            Token::KeywordFunction(_) => "function",
            Token::KeywordStruct(_) => "struct",
            Token::KeywordIf(_) => "if",
            Token::KeywordElse(_) => "else",
            Token::KeywordLet(_) => "let",
            Token::Identifier(identifier) => identifier.raw_text.as_str(),
            /* Literals */
            Token::LiteralString(lit) => lit.raw_text.as_str(),
            Token::LiteralInteger(lit) => lit.raw_text.as_str(),
            Token::LiteralFloat(lit) => lit.raw_text.as_str(),
            /* Comment */
            Token::LiteralComment(lit) => lit.raw_text.as_str(),
            Token::LiteralUnknownOp(lit) => lit.raw_text.as_str(),
            /* Brackets */
            Token::BracketLeftRound(_) => "(",
            Token::BracketRightRound(_) => ")",
            Token::BracketLeftSquare(_) => "[",
            Token::BracketRightSquare(_) => "]",
            Token::BracketLeftCurly(_) => "{{",
            Token::BracketRightCurly(_) => "}}",
            /* Non-repeating punctuation */
            Token::Semicolon(_) => ";",
            Token::Comma(_) => ",",
            /* Possbily repeating punctuation */
            Token::OpNot(_) => "!",
        }
        .to_string()
    }
}

/** @brief  A greedy lexer. Every token is acquired greedily.
 *
 *  @note   Punctuation (that doesn't include brackets or underscores or
 *          commas or semicolons) will be greedily combined.
 */
struct Lexer<'a> {
    input_path: &'a Path,
    output_path: &'a Path,
    text: String,
    position: Position,
    tokens: Vec<Token>,
}

impl Lexer<'_> {
    pub fn new<'a>(input_path: &'a Path, output_path: &'a Path) -> Result<Lexer<'a>, &'static str> {
        if output_path.exists() {
            let x = output_path.display();
            eprintln!("{x} exists");
        }
        return Ok(Lexer {
            input_path,
            output_path,
            text: fs::read_to_string(input_path).expect("{input_path.display()} DNE}"),
            position: Position::new(),
            tokens: Vec::new(),
        });
    }

    fn parse_identifier(&mut self, position: Position) -> usize {
        let mut length: usize = 0;
        for c in self.text[position.position..].chars() {
            match c {
                c if c.is_alphanumeric() || c == '_' => {
                    length += 1;
                    continue;
                }
                _ => {
                    break;
                }
            }
        }

        let raw_text: String = self.text[position.position..position.position + length].to_string();
        match raw_text.as_str() {
            "function" => self.tokens.push(Token::KeywordFunction(position)),
            "struct" => self.tokens.push(Token::KeywordStruct(position)),
            "if" => self.tokens.push(Token::KeywordIf(position)),
            "else" => self.tokens.push(Token::KeywordElse(position)),
            "let" => self.tokens.push(Token::KeywordLet(position)),
            _ => self.tokens.push(Token::Identifier(Identifier {
                position,
                raw_text: raw_text.to_string(),
            })),
        }
        println!("{raw_text}");
        length
    }

    fn parse_number(&mut self, position: Position) -> usize {
        let mut length: usize = 0;
        for c in self.text[position.position..].chars() {
            match c {
                // TODO Support hexadecimal, octal, binary, decimal, and
                //      scientific notation.
                c if c.is_ascii_digit() => {
                    length += 1;
                    continue;
                }
                _ => {
                    break;
                }
            }
        }
        let raw_text = &self.text[position.position..position.position + length];
        let value = raw_text
            .parse()
            .expect("cannot parse int from string '{raw_text}'");
        self.tokens.push(Token::LiteralInteger(IntegerLiteral {
            position: position,
            raw_text: raw_text.to_string(),
            value: value,
        }));
        length
    }

    fn parse_string(&mut self, start: Position) -> usize {
        let mut length: usize = 1;
        let mut escaped = false;
        if &self.text[start.position..start.position + 1] != "\"" {
            return 0;
        }
        for c in self.text[start.position + 1..].chars() {
            match c {
                c if c == '"' && !escaped => {
                    length += 1;
                    break;
                }
                // TODO Support other escaped characters.
                '\\' => {
                    length += 1;
                    escaped = true;
                }
                '\n' => {
                    panic!("unmatched quote");
                }
                _ => {
                    length += 1;
                    escaped = false;
                    continue;
                }
            }
        }
        // TODO Panic if reach EOF.
        let raw_text = &self.text[start.position..start.position + length];
        let value = raw_text.parse().expect("cannot parse string from string");
        self.tokens.push(Token::LiteralString(StringLiteral {
            position: start,
            raw_text: raw_text.to_string(),
            value: value,
        }));
        println!("String: '{raw_text}'");
        length
    }

    /// @note   We already know this is punctuation.
    fn parse_comment(&mut self, start: Position) -> usize {
        let mut length: usize = 2;
        let mut almost_end: bool = false;
        if &self.text[start.position..start.position + 2] != "/*" {
            return 0;
        }
        for c in self.text[start.position + 2..].chars() {
            match c {
                '*' => {
                    length += 1;
                    almost_end = true;
                }
                c if almost_end && c == '/' => {
                    length += 1;
                    let raw_text = &self.text[start.position..start.position + length];
                    self.tokens.push(Token::LiteralComment(CommentLiteral {
                        position: start,
                        raw_text: raw_text.to_string(),
                    }));
                    println!("Comment: '{raw_text}'");
                    return length;
                }
                _ => {
                    length += 1;
                    almost_end = false;
                }
            }
        }
        panic!("reached EOF without finishing string!");
    }

    fn parse_punctuation(&mut self, position: Position) -> usize {
        let mut length: usize = 0;

        if &self.text[position.position..position.position + 2] == "/*" {
            return self.parse_comment(self.position);
        }

        for c in self.text[position.position..].chars() {
            match c {
                // These must occur above the ASCII punctuation arm
                // otherwise they'll be sucked in as well.
                '(' | ')' | '[' | ']' | '{' | '}' => break,
                c if c.is_ascii_punctuation() => length += 1,
                _ => break,
            }
        }
        let raw_text = &self.text[position.position..position.position + length];
        match raw_text {
            "!" => self.tokens.push(Token::OpNot(position)),
            _ => {
                println!("unrecognized op '{raw_text}'");
                self.tokens.push(Token::LiteralUnknownOp(UnknownOpLiteral {
                    position: position,
                    raw_text: raw_text.to_string(),
                }))
            }
        }
        println!("Op: '{raw_text}'");
        length
    }

    pub fn run(&mut self) {
        // HACK This is just to prevent a reference to the Lexer from
        //      being created.
        let text = self.text.clone();
        let mut skip: usize = 0;
        for (i, c) in text.chars().enumerate() {
            if skip > 0 {
                skip -= 1;
                continue;
            }
            println!("{i}: {c}");
            if i != self.position.position {
                let p = self.position.position;
                let pc: &str = &self.text[p..p + 1];
                eprintln!("Mismatch position: {i} vs {p} => {c} vs {pc}");
            }
            match c {
                '(' => {
                    self.tokens.push(Token::BracketLeftRound(self.position));
                    self.position.next_column();
                }
                ')' => {
                    self.tokens.push(Token::BracketRightRound(self.position));
                    self.position.next_column();
                }
                '[' => {
                    self.tokens.push(Token::BracketLeftSquare(self.position));
                    self.position.next_column();
                }
                ']' => {
                    self.tokens.push(Token::BracketRightSquare(self.position));
                    self.position.next_column();
                }
                '{' => {
                    self.tokens.push(Token::BracketLeftCurly(self.position));
                    self.position.next_column();
                }
                '}' => {
                    self.tokens.push(Token::BracketRightCurly(self.position));
                    self.position.next_column();
                }
                ';' => {
                    self.tokens.push(Token::Semicolon(self.position));
                    self.position.next_column();
                }
                ',' => {
                    self.tokens.push(Token::Comma(self.position));
                    self.position.next_column();
                }
                // TODO What to do with non-ASCII digits?
                c if c == '_' || c.is_alphabetic() => {
                    let len = self.parse_identifier(self.position);
                    self.position.next_column_step(len);
                    skip = len - 1;
                }
                c if c.is_ascii_digit() => {
                    let len = self.parse_number(self.position);
                    self.position.next_column_step(len);
                    skip = len - 1;
                }
                // This has to go above the punctuation, because '"' is
                // punctuation.
                '"' => {
                    let len = self.parse_string(self.position);
                    self.position.next_column_step(len);
                    skip = len - 1;
                }
                c if c.is_ascii_punctuation() => {
                    let len = self.parse_punctuation(self.position);
                    self.position.next_column_step(len);
                    skip = len - 1;
                }
                '\n' => {
                    self.position.next_line();
                }
                c if c.is_whitespace() && c != '\n' => {
                    self.position.next_column();
                }
                _ => {
                    self.position.next_column();
                }
            }
        }
    }

    pub fn print_csv(&self) {
        for t in &self.tokens {
            let txt = match t {
                Token::Comma(_) => ",".to_string(),
                _ => t.to_raw_text(),
            };
            println!("{},{}", t.get_position().to_csv_string(), txt);
        }
    }
}

fn main() -> Result<(), i32> {
    let args: Vec<String> = env::args().collect();
    dbg!(&args);

    if args.len() != 3 {
        eprintln!("Usage: exe <input> <output>");
        return Err(-1);
    }
    let input_path = Path::new(&args[1]);
    let output_path = Path::new(&args[2]);

    let mut lexer = Lexer::new(&input_path, &output_path).expect("invalid lexer");
    lexer.run();
    lexer.print_csv();
    Ok(())
}
