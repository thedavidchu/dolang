/// @brief  The parser for my grammar.
/// @todo   1. Filter out comments more intelligently.
/// @todo   2. Parse from a Concrete Syntax Tree to an Abstract Syntax Tree.
///         That means convert comma-separated things into vectors.
use std::backtrace::Backtrace;

use crate::lexer::{self, Lexer, Token};

pub enum Node {
    Dummy {},
    Empty {},
    Statement {
        x: Box<Node>,
    },
    LitStr {
        x: Token,
    },
    LitInt {
        x: Token,
    },
    LitFloat {
        x: Token,
    },
    Id {
        x: Token,
    },
    DefFunc {
        name: Box<Node>,
        params: Box<Node>,
        rets: Box<Node>,
        body: Vec<Box<Node>>,
    },
    DefStruct {},
    IfElseStatement {
        cond: Box<Node>,
        if_block: Vec<Box<Node>>,
        else_block: Vec<Box<Node>>,
    },
    // This is either a 'let' statement or function parameter.
    DefVar {
        name: Box<Node>,
        // r#type: Option<Box<Node>>, value: Option<Box<Node>>,
    },
    ModuleImport {
        x: Box<Node>,
    },
    Return {
        x: Box<Node>,
    },
    ExprArrow {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprColon {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprAnd {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprOr {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprNot {
        x: Box<Node>,
    },
    ExprNamespace {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprMul {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprDiv {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprAdd {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprSub {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprPos {
        x: Box<Node>,
    },
    ExprNeg {
        x: Box<Node>,
    },
    ExprEq {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprNeq {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprGt {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprLt {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprGe {
        x: Box<Node>,
        y: Box<Node>,
    },
    ExprLe {
        x: Box<Node>,
        y: Box<Node>,
    },
    Set {
        x: Box<Node>,
        y: Box<Node>,
    },
    Comma {
        x: Box<Node>,
        y: Box<Node>,
    },
    Call {
        x: Box<Node>,
        y: Box<Node>,
    },
    Access {
        x: Box<Node>,
        y: Box<Node>,
    },
    BracketRound {
        x: Box<Node>,
    },
    BracketSquare {
        x: Box<Node>,
    },
}

impl Node {
    fn to_string(&self) -> String {
        match self {
            Node::Empty {} => String::from(""),
            Node::ExprNot { x } => String::from("not ") + x.to_string().as_str(),
            Node::ExprAnd { x, y } => x.to_string() + " and " + y.to_string().as_str(),
            Node::ExprOr { x, y } => x.to_string() + " or " + y.to_string().as_str(),
            Node::Return { x } => String::from("return ") + x.to_string().as_str(),
            Node::Id { x } => x.to_raw_text(),
            Node::LitFloat { x } => x.to_raw_text(),
            Node::LitInt { x } => x.to_raw_text(),
            Node::LitStr { x } => x.to_raw_text(),
            Node::Access { x, y } => x.to_string() + "[" + y.to_string().as_str() + "]",
            Node::BracketRound { x } => String::from("(") + x.to_string().as_str() + ")",
            Node::BracketSquare { x } => String::from("[") + x.to_string().as_str() + "]",
            Node::Call { x, y } => x.to_string() + "(" + y.to_string().as_str() + ")",
            Node::ModuleImport { x } => String::from("module ") + x.to_string().as_str(),
            Node::Set { x, y } => x.to_string() + " = " + y.to_string().as_str(),
            Node::Statement { x } => x.to_string() + "; ",
            Node::DefFunc {
                name,
                params,
                rets,
                body,
            } => {
                String::from("function ")
                    + name.to_string().as_str()
                    + "("
                    + params.to_string().as_str()
                    + ") -> "
                    + rets.to_string().as_str()
                    + " {"
                    + body
                        .iter()
                        .map(|x| x.to_string())
                        .collect::<Vec<String>>()
                        .join("")
                        .as_str()
                    + "}"
            }
            Node::IfElseStatement {
                cond,
                if_block,
                else_block,
            } => {
                String::from("if ")
                    + cond.to_string().as_str()
                    + " { "
                    + if_block
                        .iter()
                        .map(|x| x.to_string())
                        .collect::<Vec<String>>()
                        .join("")
                        .as_str()
                    + " } else { "
                    + else_block
                        .iter()
                        .map(|x| x.to_string())
                        .collect::<Vec<String>>()
                        .join("")
                        .as_str()
                    + "} "
            }
            Node::DefVar { name } => String::from("let ") + name.to_string().as_str(),
            Node::ExprAdd { x, y } => x.to_string() + " + " + y.to_string().as_str(),
            Node::ExprSub { x, y } => x.to_string() + " - " + y.to_string().as_str(),
            Node::ExprMul { x, y } => x.to_string() + " * " + y.to_string().as_str(),
            Node::ExprDiv { x, y } => x.to_string() + " / " + y.to_string().as_str(),
            Node::ExprEq { x, y } => x.to_string() + " == " + y.to_string().as_str(),
            Node::ExprNeq { x, y } => x.to_string() + " != " + y.to_string().as_str(),
            Node::ExprGe { x, y } => x.to_string() + " >= " + y.to_string().as_str(),
            Node::ExprGt { x, y } => x.to_string() + " > " + y.to_string().as_str(),
            Node::ExprLe { x, y } => x.to_string() + " <= " + y.to_string().as_str(),
            Node::ExprLt { x, y } => x.to_string() + " < " + y.to_string().as_str(),
            Node::ExprColon { x, y } => x.to_string() + ": " + y.to_string().as_str(),
            Node::ExprNamespace { x, y } => x.to_string() + "::" + y.to_string().as_str(),
            Node::Comma { x, y } => x.to_string() + ", " + y.to_string().as_str(),
            _ => String::from("?"),
        }
    }
}

pub struct Parser<'a> {
    lexer: lexer::Lexer<'a>,
    pos: usize,
    ast: Vec<Node>,
    // HACK: This stores a flat vector of ALL the nodes; this is to // simplify ownership.
    // I'm confused by rust, so I'll just increment this to change the data structure.
    todo: usize,
}

/// @note   Based on primarily on Python and secondarily on C/C++.
/// @todo   Maybe base it on Rust/Go.
fn get_priority(token: &Token) -> f32 {
    match token {
        // Namespace Binary operators
        Token::OpNamespace(_) => 16.0,
        // Access operators
        Token::OpDot(_) => 15.0,
        Token::OpArrow(_) => 15.0,
        // Postfix operators
        Token::BracketLeftSquare(_) => 14.0,
        Token::BracketLeftRound(_) => 14.0,
        // // Prefix operators
        // "*_" => 13.0,
        // "&_" => 13.0,
        // "~_" => 13.0,
        // "!_" => 13.0,
        // "+_" => 13.0,
        // "-_" => 13.0,
        // Binary operators
        // > Multiplicative (*, /; TODO: //, %)
        Token::OpMul(_) => 12.0,
        Token::OpDiv(_) => 12.0,
        // > Additive
        Token::OpPlus(_) => 11.0,
        Token::OpMinus(_) => 11.0,
        // // >  Shifts
        // ">>" => 10.0,
        // "<<" => 10.0,
        // // > Bitwise
        // // >> Bitwise AND
        // "&" => 9.0,
        // // >> Bitwise XOR
        // "^" => 8.0,
        // // >> Bitwise OR
        // "|" => 7.0,
        Token::OpColon(_) => 6.0,
        // > Comparison
        Token::OpLt(_) => 5.0,
        Token::OpLe(_) => 5.0,
        Token::OpEq(_) => 5.0,
        Token::OpNe(_) => 5.0,
        Token::OpGt(_) => 5.0,
        Token::OpGe(_) => 5.0,
        // > Boolean
        Token::KeywordNot(_) => 4.0,
        Token::KeywordAnd(_) => 3.0,
        Token::KeywordOr(_) => 2.0,
        // > Other operations
        Token::OpSet(_) => 1.0,
        Token::Comma(_) => 0.0,
        _ => -1.0,
    }
}

impl Parser<'_> {
    pub fn new<'a>(lexer: Lexer<'a>) -> Result<Parser<'a>, &'static str> {
        Ok(Parser {
            lexer,
            pos: 0,
            ast: Vec::new(),
            todo: 0,
        })
    }

    fn get_token<'a>(&'a self) -> Result<Token, ()> {
        if self.pos >= self.lexer.tokens.len() {
            return Err(());
        }
        Ok(self.lexer.tokens[self.pos].clone())
    }

    fn next_token<'a>(&'a mut self) {
        if self.pos < self.lexer.tokens.len() {
            self.pos += 1;
        }
    }

    fn eat_next_token<'a>(&'a mut self, expected: &str) -> Result<Token, ()> {
        let token = self.get_token()?;
        match token {
            Token::Identifier(_, _) => (),
            /* Literals */
            Token::LiteralString(_, _, _) => (),
            Token::LiteralInteger(_, _, _) => (),
            Token::LiteralFloat(_, _, _) => (),
            /* Comment */
            Token::LiteralComment(_, _) => (),
            Token::LiteralUnknownOp(_, _) => (),
            _ => {
                if expected == "" || expected.contains(&token.to_raw_text()) {
                } else {
                    self.lexer.print_error(&token);
                    eprintln!("Got {}, expected {}", token.to_raw_text(), expected);
                    eprintln!("Backtrace: {}", Backtrace::force_capture());
                    panic!("Unexpected token");
                }
            }
        }
        self.next_token();
        return Ok(token);
    }

    /// @brief  Parse an expression leading with an identifier.
    fn parse_binop_rhs<'a>(
        &'a mut self,
        min_expr_priority: f32,
        mut lhs: Node,
    ) -> Result<Node, ()> {
        // TODO Eat the tokens correctly.
        loop {
            let op_tk_0 = self.get_token()?;
            let priority_0 = get_priority(&op_tk_0);
            if priority_0 < min_expr_priority {
                return Ok(lhs);
            }
            match op_tk_0 {
                Token::BracketLeftRound(_) | Token::BracketLeftSquare(_) => (),
                _ => self.next_token(),
            }
            let mut rhs = self.parse_expr()?;

            let op_tk_1 = self.get_token()?;
            let priority_1 = get_priority(&op_tk_1);
            if priority_0 < priority_1 {
                rhs = self.parse_binop_rhs(priority_0 + 1.0, rhs)?;
            }
            lhs = match op_tk_0 {
                Token::OpNamespace(_) => Node::ExprNamespace {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpPlus(_) => Node::ExprAdd {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpMinus(_) => Node::ExprSub {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpMul(_) => Node::ExprMul {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpDiv(_) => Node::ExprDiv {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpArrow(_) => Node::ExprArrow {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpSet(_) => Node::Set {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpColon(_) => Node::ExprColon {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::KeywordAnd(_) => Node::ExprAnd {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::KeywordOr(_) => Node::ExprOr {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpEq(_) => Node::ExprEq {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpNe(_) => Node::ExprNeq {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpGe(_) => Node::ExprGe {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpGt(_) => Node::ExprGt {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpLe(_) => Node::ExprLe {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpLt(_) => Node::ExprLt {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::BracketLeftRound(_) => Node::Call {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::BracketLeftSquare(_) => Node::Access {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::Comma(_) => Node::Comma {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                // TODO ...
                _ => panic!(
                    "unrecognized op: '{}' of type '{}'",
                    op_tk_0.to_raw_text(),
                    op_tk_0.get_type_string()
                ),
            }
        }
    }

    fn parse_bracket_expr<'a>(&'a mut self) -> Result<Node, ()> {
        let s: &str = match self.get_token()? {
            Token::BracketLeftCurly(_) => {
                self.eat_next_token("{");
                "}"
            }
            Token::BracketLeftRound(_) => {
                self.eat_next_token("(");
                ")"
            }
            Token::BracketLeftSquare(_) => "]",
            _ => panic!("expected left bracket: {{ ( ["),
        };
        let x = match self.get_token()? {
            Token::BracketRightRound(_) | Token::BracketRightSquare(_) => Node::Empty {},
            _ => self.parse_expr()?,
        };
        match self.get_token()? {
            Token::BracketRightCurly(_) => {
                assert!(s == "}");
                self.eat_next_token(s);
                panic!("curly bracket expressions not supported!");
            }
            Token::BracketRightRound(_) => {
                assert!(s == ")");
                self.eat_next_token(s);
                Ok(Node::BracketRound { x: Box::new(x) })
            }
            Token::BracketRightSquare(_) => {
                assert!(s == "]");
                self.eat_next_token(s);
                Ok(Node::BracketSquare { x: Box::new(x) })
            }
            _ => panic!("expected right bracket: ] ) }}"),
        }
    }

    /// @brief  Parse an expression starting with a primary.
    /// @note   A 'primary' is a simple unit in the grammar that can be
    ///         unambiguously parsed. For example,
    ///         1. Literal (e.g. '1.0', '"Hello, World!\n"')
    ///         2. Function call (e.g. 'f(x)')
    ///         3. Object access (e.g. 'x[y]')
    ///         4. Prefix operators (e.g. '+x', '++x')
    ///         5. Postfix operators (e.g. 'x++')
    ///         Source: https://stackoverflow.com/questions/15675427/what-is-a-primary-expression
    fn parse_expr<'a>(&'a mut self) -> Result<Node, ()> {
        let x = self.get_token()?;
        return match x {
            Token::Identifier(_, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, Node::Id { x })
            }
            Token::BracketLeftRound(_) | Token::BracketLeftSquare(_) => self.parse_bracket_expr(),
            // Literals
            Token::LiteralFloat(_, _, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, Node::LitFloat { x })
            }
            Token::LiteralInteger(_, _, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, Node::LitInt { x })
            }
            Token::LiteralString(_, _, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, Node::LitStr { x })
            }
            // Prefix operators
            Token::OpMinus(_) => {
                self.eat_next_token("-")?;
                return Ok(Node::ExprNeg {
                    x: Box::new(self.parse_expr()?),
                });
            }
            Token::OpPlus(_) => {
                self.eat_next_token("+")?;
                return Ok(Node::ExprPos {
                    x: Box::new(self.parse_expr()?),
                });
            }
            Token::KeywordNot(_) => {
                self.eat_next_token("not")?;
                return Ok(Node::ExprNot {
                    x: Box::new(self.parse_expr()?),
                });
            }
            // If/Else
            Token::KeywordIf(_) => {
                self.eat_next_token("if")?;
                let if_cond = self.parse_expr()?;
                let if_block = self.parse_statements()?;
                let else_block = if let Token::KeywordElse(_) = self.get_token()? {
                    self.parse_statements()?
                } else {
                    Vec::new()
                };
                return Ok(Node::IfElseStatement {
                    cond: Box::new(if_cond),
                    if_block: if_block,
                    else_block: else_block,
                });
            }
            Token::KeywordReturn(_) => {
                self.eat_next_token("return")?;
                return Ok(Node::Return {
                    x: Box::new(self.parse_expr()?),
                });
            }
            Token::KeywordLet(_) => {
                self.eat_next_token("let")?;
                return Ok(Node::DefVar {
                    name: Box::new(self.parse_expr()?),
                });
            }
            Token::LiteralComment(_, _) => {
                self.eat_next_token("")?;
                return self.parse_expr();
            }
            _ => {
                self.lexer.print_error(&x);
                panic!("unhandled token '{}'", x.to_raw_text())
            }
        };
    }

    /// @brief  Parse statements in "{<expr>; <expr>;}".
    fn parse_statements<'a>(&'a mut self) -> Result<Vec<Box<Node>>, ()> {
        self.eat_next_token("{")?;
        let mut r: Vec<Box<Node>> = Vec::new();
        loop {
            match self.get_token()? {
                Token::BracketRightCurly(_) => {
                    self.eat_next_token("}")?;
                    return Ok(r);
                }
                // NOTE If-statement is already a statement
                Token::KeywordIf(_) => r.push(Box::new(self.parse_expr()?)),
                _ => {
                    r.push(Box::new(Node::Statement {
                        x: Box::new(self.parse_expr()?),
                    }));
                    self.eat_next_token(";")?;
                }
            }
        }
    }

    /// @brief  Parse parameters in "(n: int, m: int)" or "{n: int, m: int}".
    /// @todo   Allow trailing commas
    fn parse_params<'a>(&'a mut self) {}

    fn parse_function_def<'a>(&'a mut self) -> Result<Node, ()> {
        self.eat_next_token("function")?;
        // TODO 1. Support namespaces
        // TODO 2. Make safe (i.e. don't just unwrap it)
        let name = Node::Id {
            x: self.eat_next_token("")?,
        };
        let name = Box::new(self.parse_binop_rhs(get_priority(&Token::parse_dummy("::")), name)?);
        let params = Box::new(self.parse_bracket_expr()?);
        self.eat_next_token("->")?;
        let rets = Box::new(self.parse_expr()?);
        let body = self.parse_statements()?;
        Ok(Node::DefFunc {
            name,
            params,
            rets,
            body,
        })
    }

    fn parse_struct_def<'a>(&'a mut self) -> Result<Node, ()> {
        self.eat_next_token("struct")?;
        Ok(Node::Dummy {})
    }

    fn parse_let_def<'a>(&'a mut self) -> Result<Node, ()> {
        self.eat_next_token("let")?;
        Ok(Node::Dummy {})
    }

    fn parse_module_import<'a>(&'a mut self) -> Result<Node, ()> {
        self.eat_next_token("module")?;
        let node = self.parse_expr()?;
        self.eat_next_token(";")?;
        Ok(Node::Statement {
            x: Box::new(Node::ModuleImport { x: Box::new(node) }),
        })
    }

    pub fn parse_module(&mut self) -> Result<(), ()> {
        while let Ok(t) = self.get_token() {
            match t {
                Token::KeywordModule(_) => {
                    let x = self.parse_module_import()?;
                    self.ast.push(x);
                }
                Token::KeywordFunction(_) => {
                    let x = self.parse_function_def()?;
                    self.ast.push(x);
                }
                Token::KeywordStruct(_) => {
                    let x = self.parse_struct_def()?;
                    self.ast.push(x);
                }
                Token::KeywordLet(_) => {
                    let x = self.parse_let_def()?;
                    self.ast.push(x);
                }
                Token::LiteralComment(_, _) => {
                    self.eat_next_token("")?;
                }
                _ => {
                    self.lexer.print_error(&t);
                    panic!(
                        "unrecognized module-level token at {}: '{}' of type '{}'",
                        t.get_position().to_csv_string(),
                        t.to_raw_text(),
                        t.get_type_string()
                    )
                }
            }
        }
        Ok(())
    }

    pub fn print(&self) {
        for x in &self.ast {
            println!("{}", x.to_string());
        }
    }
}
