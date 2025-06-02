use std::cmp::min;
use std::fs;
use std::path::Path;
use std::process::exit;

#[derive(Debug, Clone, Copy)]
pub struct Position {
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

    pub fn to_csv_string(&self) -> String {
        let mut s: String = "".to_string();
        s.push_str(self.position.to_string().as_str());
        s.push_str(",");
        s.push_str(self.line.to_string().as_str());
        s.push_str(",");
        s.push_str(self.column.to_string().as_str());
        return s;
    }
}

#[derive(Debug, Clone)]
pub enum Token {
    /* IDK if this should be a literal or not. */
    LiteralComment(Position, String),
    LiteralUnknownOp(Position, String),

    KeywordReturn(Position),
    KeywordFunction(Position),
    KeywordModule(Position),
    KeywordStruct(Position),
    KeywordIf(Position),
    KeywordElse(Position),
    KeywordLet(Position),
    /* Boolean Operations */
    KeywordAnd(Position),
    KeywordOr(Position),
    KeywordNot(Position),

    Identifier(Position, String),

    LiteralString(Position, String, String),
    LiteralInteger(Position, String, i64),
    LiteralFloat(Position, String, f64),

    BracketLeftRound(Position),
    BracketRightRound(Position),
    BracketLeftSquare(Position),
    BracketRightSquare(Position),
    BracketLeftCurly(Position),
    BracketRightCurly(Position),

    Semicolon(Position),
    Comma(Position),

    OpColon(Position),
    OpSet(Position),
    OpNamespace(Position),
    OpDot(Position),
    OpArrow(Position),

    /* Math Operations */
    OpPlus(Position),
    OpMinus(Position),
    OpDiv(Position),
    OpMul(Position),

    /* Bitwise Operations (TODO) */

    /* Comparison Operations */
    OpEq(Position),
    OpNe(Position),
    OpLt(Position),
    OpGt(Position),
    OpLe(Position),
    OpGe(Position),
}

impl Token {
    pub fn get_position(&self) -> Position {
        match self {
            Token::KeywordReturn(pos) => pos,
            Token::KeywordFunction(pos) => pos,
            Token::KeywordModule(pos) => pos,
            Token::KeywordStruct(pos) => pos,
            Token::KeywordIf(pos) => pos,
            Token::KeywordElse(pos) => pos,
            Token::KeywordLet(pos) => pos,
            /* Boolean Operations */
            Token::KeywordAnd(pos) => pos,
            Token::KeywordOr(pos) => pos,
            Token::KeywordNot(pos) => pos,
            Token::Identifier(pos, _) => &pos,
            /* Literals */
            Token::LiteralString(pos, _, _) => &pos,
            Token::LiteralInteger(pos, _, _) => &pos,
            Token::LiteralFloat(pos, _, _) => &pos,
            /* Comment */
            Token::LiteralComment(pos, _) => &pos,
            Token::LiteralUnknownOp(pos, _) => &pos,
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
            Token::OpColon(pos) => pos,
            Token::OpSet(pos) => pos,
            Token::OpNamespace(pos) => pos,
            Token::OpDot(pos) => pos,
            Token::OpArrow(pos) => pos,

            /* Math Operations */
            Token::OpPlus(pos) => pos,
            Token::OpMinus(pos) => pos,
            Token::OpDiv(pos) => pos,
            Token::OpMul(pos) => pos,

            /* Bitwise Operations (TODO) */


            /* Comparison Operations */
            Token::OpEq(pos) => pos,
            Token::OpNe(pos) => pos,
            Token::OpLt(pos) => pos,
            Token::OpGt(pos) => pos,
            Token::OpLe(pos) => pos,
            Token::OpGe(pos) => pos,
        }
        .clone()
    }

    pub fn get_type_string(&self) -> String {
        match self {
            Token::KeywordReturn(_) => "KeywordReturn",
            Token::KeywordFunction(_) => "KeywordFunction",
            Token::KeywordModule(_) => "KeywordModule",
            Token::KeywordStruct(_) => "KeywordStruct",
            Token::KeywordIf(_) => "KeywordIf",
            Token::KeywordElse(_) => "KeywordElse",
            Token::KeywordLet(_) => "KeywordLet",
            /* Boolean Operations */
            Token::KeywordAnd(_) => "KeywordAnd",
            Token::KeywordOr(_) => "KeywordOr",
            Token::KeywordNot(_) => "KeywordNot",
            Token::Identifier(_, _) => "Identifier",
            /* Literals */
            Token::LiteralString(_, _, _) => "LiteralString",
            Token::LiteralInteger(_, _, _) => "LiteralInteger",
            Token::LiteralFloat(_, _, _) => "LiteralFloat",
            /* Comment */
            Token::LiteralComment(_, _) => "LiteralComment",
            Token::LiteralUnknownOp(_, _) => "LiteralUnknownOp",
            /* Brackets */
            Token::BracketLeftRound(_) => "BracketLeftRound",
            Token::BracketRightRound(_) => "BracketRightRound",
            Token::BracketLeftSquare(_) => "BracketLeftSquare",
            Token::BracketRightSquare(_) => "BracketRightSquare",
            Token::BracketLeftCurly(_) => "BracketLeftCurly",
            Token::BracketRightCurly(_) => "BracketRightCurly",
            /* Non-repeating punctuation */
            Token::Semicolon(_) => "Semicolon",
            Token::Comma(_) => "Comma",
            /* Possbily repeating punctuation */
            Token::OpColon(_) => "OpColon",
            Token::OpSet(_) => "OpSet",
            Token::OpNamespace(_) => "OpNamespace",
            Token::OpDot(_) => "OpDot",
            Token::OpArrow(_) => "OpArrow",

            /* Math Operations */
            Token::OpPlus(_) => "OpPlus",
            Token::OpMinus(_) => "OpMinus",
            Token::OpDiv(_) => "OpDiv",
            Token::OpMul(_) => "OpMul",

            /* Bitwise Operations (TODO) */

            /* Comparison Operations */
            Token::OpEq(_) => "OpEq",
            Token::OpNe(_) => "OpNe",
            Token::OpLt(_) => "OpLt",
            Token::OpGt(_) => "OpGt",
            Token::OpLe(_) => "OpLe",
            Token::OpGe(_) => "OpGe",
        }
        .to_string()
    }

    pub fn to_raw_text(&self) -> String {
        match self {
            Token::KeywordReturn(_) => "return",
            Token::KeywordFunction(_) => "function",
            Token::KeywordModule(_) => "module",
            Token::KeywordStruct(_) => "struct",
            Token::KeywordIf(_) => "if",
            Token::KeywordElse(_) => "else",
            Token::KeywordLet(_) => "let",
            /* Boolean Operations */
            Token::KeywordAnd(_) => "and",
            Token::KeywordOr(_) => "or",
            Token::KeywordNot(_) => "not",
            Token::Identifier(_, id) => id.as_str(),
            /* Literals */
            Token::LiteralString(_, id, _) => id.as_str(),
            Token::LiteralInteger(_, id, _) => id.as_str(),
            Token::LiteralFloat(_, id, _) => id.as_str(),
            /* Comment */
            Token::LiteralComment(_, id) => id.as_str(),
            Token::LiteralUnknownOp(_, id) => id.as_str(),
            /* Brackets */
            Token::BracketLeftRound(_) => "(",
            Token::BracketRightRound(_) => ")",
            Token::BracketLeftSquare(_) => "[",
            Token::BracketRightSquare(_) => "]",
            Token::BracketLeftCurly(_) => "{",
            Token::BracketRightCurly(_) => "}",
            /* Non-repeating punctuation */
            Token::Semicolon(_) => ";",
            Token::Comma(_) => ",",
            /* Possbily repeating punctuation */
            Token::OpColon(_) => ":",
            Token::OpSet(_) => "=",
            Token::OpNamespace(_) => "::",
            Token::OpDot(_) => ".",
            Token::OpArrow(_) => "->",

            /* Math Operations */
            Token::OpPlus(_) => "+",
            Token::OpMinus(_) => "-",
            Token::OpDiv(_) => "/",
            Token::OpMul(_) => "*",

            /* Bitwise Operations (TODO) */

            /* Comparison Operations */
            Token::OpEq(_) => "==",
            Token::OpNe(_) => "!=",
            Token::OpLt(_) => "<",
            Token::OpGt(_) => ">",
            Token::OpLe(_) => "<=",
            Token::OpGe(_) => ">=",
        }
        .to_string()
    }

    #[allow(unused)]
    pub fn parse_dummy(s: &str) -> Self {
        let p = Position {
            position: 0,
            line: 0,
            column: 0,
        };
        match s {
            "return" => Token::KeywordReturn(p),
            "function" => Token::KeywordFunction(p),
            "module" => Token::KeywordModule(p),
            "struct" => Token::KeywordStruct(p),
            "if" => Token::KeywordIf(p),
            "else" => Token::KeywordElse(p),
            "let" => Token::KeywordLet(p),
            /* Boolean Operations */
            "and" => Token::KeywordAnd(p),
            "or" => Token::KeywordOr(p),
            "not" => Token::KeywordNot(p),
            /* Brackets */
            "(" => Token::BracketLeftRound(p),
            ")" => Token::BracketRightRound(p),
            "[" => Token::BracketLeftSquare(p),
            "]" => Token::BracketRightSquare(p),
            "{" => Token::BracketLeftCurly(p),
            "}" => Token::BracketRightCurly(p),
            /* Non-repeating punctuation */
            ";" => Token::Semicolon(p),
            "," => Token::Comma(p),
            /* Possbily repeating punctuation */
            ":" => Token::OpColon(p),
            "=" => Token::OpSet(p),
            "::" => Token::OpNamespace(p),
            "." => Token::OpDot(p),
            "->" => Token::OpArrow(p),

            /* Math Operations */
            "+" => Token::OpPlus(p),
            "-" => Token::OpMinus(p),
            "/" => Token::OpDiv(p),
            "*" => Token::OpMul(p),

            /* Bitwise Operations (TODO) */

            /* Comparison Operations */
            "==" => Token::OpEq(p),
            "!=" => Token::OpNe(p),
            "<" => Token::OpLt(p),
            ">" => Token::OpGt(p),
            "<=" => Token::OpLe(p),
            ">=" => Token::OpGe(p),

            /* Literals */
            s if s.starts_with("\"") => Token::LiteralString(
                p,
                String::from(s),
                String::from(s)[1..s.len() - 1].parse().expect("blah"),
            ),
            /* Comment */
            s if s.starts_with("/*") => Token::LiteralComment(p, String::from(s)),
            // TODO Parse identifier and integers
            _ => Token::LiteralUnknownOp(p, String::from(s)),
        }
    }

    #[allow(unused)]
    pub fn is_literal(&self) -> bool {
        match self {
            Self::LiteralComment(_, _)
            | Self::LiteralFloat(_, _, _)
            | Self::LiteralInteger(_, _, _)
            | Self::LiteralString(_, _, _)
            | Self::LiteralUnknownOp(_, _) => true,
            _ => false,
        }
    }
}

/** @brief  A greedy lexer. Every token is acquired greedily.
 *
 *  @note   Punctuation (that doesn't include brackets or underscores or
 *          commas or semicolons) will be greedily combined.
 */
pub struct Lexer<'a> {
    pub input_path: &'a Path,
    pub output_path: &'a Path,
    text: String,
    position: Position,
    pub tokens: Vec<Token>,
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
            "return" => self.tokens.push(Token::KeywordReturn(position)),
            "function" => self.tokens.push(Token::KeywordFunction(position)),
            "module" => self.tokens.push(Token::KeywordModule(position)),
            "struct" => self.tokens.push(Token::KeywordStruct(position)),
            "if" => self.tokens.push(Token::KeywordIf(position)),
            "else" => self.tokens.push(Token::KeywordElse(position)),
            "let" => self.tokens.push(Token::KeywordLet(position)),
            "and" => self.tokens.push(Token::KeywordAnd(position)),
            "or" => self.tokens.push(Token::KeywordOr(position)),
            "not" => self.tokens.push(Token::KeywordNot(position)),
            _ => self
                .tokens
                .push(Token::Identifier(position, raw_text.to_string())),
        }
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
        self.tokens
            .push(Token::LiteralInteger(position, raw_text.to_string(), value));
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
        self.tokens
            .push(Token::LiteralString(start, raw_text.to_string(), value));
        length
    }

    fn is_comment(&self, i: usize) -> bool {
        &self.text[i..min(i + 2, self.text.len())] == "/*"
    }

    /// @note   We already know this is punctuation.
    fn parse_comment(&mut self, start: Position) -> (Position, usize) {
        let mut length: usize = 2;
        let mut almost_end: bool = false;
        let mut pos = start.clone();
        if &self.text[start.position..start.position + 2] != "/*" {
            return (start, 0);
        }
        pos.next_column_step(2);
        for c in self.text[start.position + 2..].chars() {
            match c {
                '*' => {
                    pos.next_column();
                    length += 1;
                    almost_end = true;
                }
                c if almost_end && c == '/' => {
                    /* Push the position to the next character. */
                    pos.next_column();
                    length += 1;
                    let raw_text = &self.text[start.position..start.position + length];
                    self.tokens
                        .push(Token::LiteralComment(start, raw_text.to_string()));
                    return (pos, length);
                }
                /* Comments can span multiple lines. */
                '\n' => {
                    pos.next_line();
                    length += 1;
                    almost_end = false;
                }
                _ => {
                    pos.next_column();
                    length += 1;
                    almost_end = false;
                }
            }
        }
        panic!("reached EOF without finishing string!");
    }

    /// @note   This function does NOT parse comments.
    fn parse_punctuation(&mut self, start: Position) -> usize {
        let mut length: usize = 0;

        for c in self.text[start.position..].chars() {
            match c {
                // These must occur above the ASCII punctuation arm
                // otherwise they'll be sucked in as well.
                '(' | ')' | '[' | ']' | '{' | '}' => break,
                c if c.is_ascii_punctuation() => length += 1,
                _ => break,
            }
        }
        let raw_text = &self.text[start.position..start.position + length];
        match raw_text {
            ":" => self.tokens.push(Token::OpColon(start)),
            "=" => self.tokens.push(Token::OpSet(start)),
            "::" => self.tokens.push(Token::OpNamespace(start)),
            "." => self.tokens.push(Token::OpDot(start)),
            "->" => self.tokens.push(Token::OpArrow(start)),

            /* Math Operations */
            "+" => self.tokens.push(Token::OpPlus(start)),
            "-" => self.tokens.push(Token::OpMinus(start)),
            "/" => self.tokens.push(Token::OpDiv(start)),
            "*" => self.tokens.push(Token::OpMul(start)),

            /* Bitwise Operations (TODO) */

            /* Comparison Operations */
            "==" => self.tokens.push(Token::OpEq(start)),
            "!=" => self.tokens.push(Token::OpNe(start)),
            "<" => self.tokens.push(Token::OpLt(start)),
            ">" => self.tokens.push(Token::OpGt(start)),
            "<=" => self.tokens.push(Token::OpLe(start)),
            ">=" => self.tokens.push(Token::OpGe(start)),
            _ => {
                eprintln!("unrecognized op '{raw_text}'");
                self.tokens
                    .push(Token::LiteralUnknownOp(start, raw_text.to_string()))
            }
        }
        length
    }

    pub fn lex_module(&mut self) {
        // HACK This is just to prevent a reference to the Lexer from
        //      being created.
        let text = self.text.clone();
        let mut skip: usize = 0;
        for (i, c) in text.chars().enumerate() {
            if skip > 0 {
                skip -= 1;
                continue;
            }
            if i != self.position.position {
                let p = self.position.position;
                let pc: &str = &self.text[p..p + 1];
                eprintln!("Mismatch position: {i} vs {p} => {c} vs {pc}");
                exit(-1);
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
                // If this is the end, then
                c if c == '/' && self.is_comment(i) => {
                    let (pos, len) = self.parse_comment(self.position);
                    self.position = pos;
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

    #[allow(unused)]
    pub fn print_error(&self, t: &Token) {
        let Position {
            position: p,
            line: l,
            column: c,
        } = t.get_position();
        let lines: Vec<String> = self.text.lines().map(String::from).collect();
        eprintln!("{}", "-".repeat(80));
        eprintln!("| Error on {:?}:{}:{}", self.input_path, l, c);
        eprintln!("| > {}", lines[l - 1]);
        eprintln!(
            "|   {}{}",
            " ".repeat(c - 1),
            "^".repeat(t.to_raw_text().len())
        );
        eprintln!("{}", "-".repeat(80));
    }

    #[allow(unused)]
    pub fn print_csv(&self) {
        for t in &self.tokens {
            let txt = match t {
                Token::Comma(_) => "\",\"".to_string(),
                _ => t.to_raw_text(),
            };
            println!("{},{}", t.get_position().to_csv_string(), txt);
        }
    }

    #[allow(unused)]
    pub fn print_single_line(&self) {
        for t in &self.tokens {
            print!("{} ", t.to_raw_text());
        }
        println!("");
    }
}
