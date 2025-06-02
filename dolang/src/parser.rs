/// @brief  The parser for my grammar.
/// @todo   1. Filter out comments more intelligently.
/// @todo   2. Parse from a Concrete Syntax Tree to an Abstract Syntax Tree.
///         That means convert comma-separated things into vectors.
use std::backtrace::Backtrace;

use crate::lexer::{self, Lexer, Token};

pub enum CstNode {
    Dummy {},
    Empty {},
    Statement {
        x: Box<CstNode>,
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
        name: Box<CstNode>,
        params: Box<CstNode>,
        rets: Box<CstNode>,
        body: Vec<Box<CstNode>>,
    },
    DefStruct {},
    IfElseStatement {
        cond: Box<CstNode>,
        if_block: Vec<Box<CstNode>>,
        else_block: Vec<Box<CstNode>>,
    },
    // This is either a 'let' statement or function parameter.
    StatementDefVar {
        name: Box<CstNode>,
        // r#type: Option<Box<Node>>, value: Option<Box<Node>>,
    },
    ModuleImport {
        x: Box<CstNode>,
    },
    Return {
        x: Box<CstNode>,
    },
    ExprArrow {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprColon {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprAnd {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprOr {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprNot {
        x: Box<CstNode>,
    },
    ExprNamespace {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprMul {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprDiv {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprAdd {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprSub {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprPos {
        x: Box<CstNode>,
    },
    ExprNeg {
        x: Box<CstNode>,
    },
    ExprEq {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprNeq {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprGt {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprLt {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprGe {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    ExprLe {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    Set {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    Comma {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    Call {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    Access {
        x: Box<CstNode>,
        y: Box<CstNode>,
    },
    BracketRound {
        x: Box<CstNode>,
    },
    BracketSquare {
        x: Box<CstNode>,
    },
}

impl CstNode {
    fn to_string(&self) -> String {
        match self {
            CstNode::Empty {} => String::from(""),
            CstNode::ExprNot { x } => String::from("not ") + x.to_string().as_str(),
            CstNode::ExprAnd { x, y } => x.to_string() + " and " + y.to_string().as_str(),
            CstNode::ExprOr { x, y } => x.to_string() + " or " + y.to_string().as_str(),
            CstNode::Return { x } => String::from("return ") + x.to_string().as_str(),
            CstNode::Id { x } => x.to_raw_text(),
            CstNode::LitFloat { x } => x.to_raw_text(),
            CstNode::LitInt { x } => x.to_raw_text(),
            CstNode::LitStr { x } => x.to_raw_text(),
            CstNode::Access { x, y } => x.to_string() + "[" + y.to_string().as_str() + "]",
            CstNode::BracketRound { x } => String::from("(") + x.to_string().as_str() + ")",
            CstNode::BracketSquare { x } => String::from("[") + x.to_string().as_str() + "]",
            CstNode::Call { x, y } => x.to_string() + "(" + y.to_string().as_str() + ")",
            CstNode::ModuleImport { x } => String::from("module ") + x.to_string().as_str(),
            CstNode::Set { x, y } => x.to_string() + " = " + y.to_string().as_str(),
            CstNode::Statement { x } => x.to_string() + "; ",
            CstNode::DefFunc {
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
            CstNode::IfElseStatement {
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
            CstNode::StatementDefVar { name } => {
                String::from("let ") + name.to_string().as_str() + ";"
            }
            CstNode::ExprAdd { x, y } => x.to_string() + " + " + y.to_string().as_str(),
            CstNode::ExprSub { x, y } => x.to_string() + " - " + y.to_string().as_str(),
            CstNode::ExprMul { x, y } => x.to_string() + " * " + y.to_string().as_str(),
            CstNode::ExprDiv { x, y } => x.to_string() + " / " + y.to_string().as_str(),
            CstNode::ExprEq { x, y } => x.to_string() + " == " + y.to_string().as_str(),
            CstNode::ExprNeq { x, y } => x.to_string() + " != " + y.to_string().as_str(),
            CstNode::ExprGe { x, y } => x.to_string() + " >= " + y.to_string().as_str(),
            CstNode::ExprGt { x, y } => x.to_string() + " > " + y.to_string().as_str(),
            CstNode::ExprLe { x, y } => x.to_string() + " <= " + y.to_string().as_str(),
            CstNode::ExprLt { x, y } => x.to_string() + " < " + y.to_string().as_str(),
            CstNode::ExprColon { x, y } => x.to_string() + ": " + y.to_string().as_str(),
            CstNode::ExprNamespace { x, y } => x.to_string() + "::" + y.to_string().as_str(),
            CstNode::Comma { x, y } => x.to_string() + ", " + y.to_string().as_str(),
            _ => String::from("?"),
        }
    }
}

pub struct Parser<'a> {
    lexer: lexer::Lexer<'a>,
    pos: usize,
    // Initially a Concrete Syntax Tree, but gradually lowered into an AST.
    cst: Vec<CstNode>,
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
            cst: Vec::new(),
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
                    eprintln!(
                        "Expected '{}', got {} of type '{}'",
                        expected,
                        token.to_raw_text(),
                        token.get_type_string()
                    );
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
        mut lhs: CstNode,
    ) -> Result<CstNode, ()> {
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
                Token::OpNamespace(_) => CstNode::ExprNamespace {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpPlus(_) => CstNode::ExprAdd {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpMinus(_) => CstNode::ExprSub {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpMul(_) => CstNode::ExprMul {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpDiv(_) => CstNode::ExprDiv {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpArrow(_) => CstNode::ExprArrow {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpSet(_) => CstNode::Set {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpColon(_) => CstNode::ExprColon {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::KeywordAnd(_) => CstNode::ExprAnd {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::KeywordOr(_) => CstNode::ExprOr {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpEq(_) => CstNode::ExprEq {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpNe(_) => CstNode::ExprNeq {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpGe(_) => CstNode::ExprGe {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpGt(_) => CstNode::ExprGt {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpLe(_) => CstNode::ExprLe {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::OpLt(_) => CstNode::ExprLt {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::BracketLeftRound(_) => CstNode::Call {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::BracketLeftSquare(_) => CstNode::Access {
                    x: Box::new(lhs),
                    y: Box::new(rhs),
                },
                Token::Comma(_) => CstNode::Comma {
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

    fn parse_bracket_expr<'a>(&'a mut self) -> Result<CstNode, ()> {
        let s: &str = match self.get_token()? {
            Token::BracketLeftCurly(_) => {
                self.eat_next_token("{")?;
                "}"
            }
            Token::BracketLeftRound(_) => {
                self.eat_next_token("(")?;
                ")"
            }
            Token::BracketLeftSquare(_) => "]",
            _ => panic!("expected left bracket: {{ ( ["),
        };
        let x = match self.get_token()? {
            Token::BracketRightRound(_) | Token::BracketRightSquare(_) => CstNode::Empty {},
            _ => self.parse_expr()?,
        };
        match self.get_token()? {
            Token::BracketRightCurly(_) => {
                assert!(s == "}");
                self.eat_next_token(s)?;
                panic!("curly bracket expressions not supported!");
            }
            Token::BracketRightRound(_) => {
                assert!(s == ")");
                self.eat_next_token(s)?;
                Ok(CstNode::BracketRound { x: Box::new(x) })
            }
            Token::BracketRightSquare(_) => {
                assert!(s == "]");
                self.eat_next_token(s)?;
                Ok(CstNode::BracketSquare { x: Box::new(x) })
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
    fn parse_expr<'a>(&'a mut self) -> Result<CstNode, ()> {
        let x = self.get_token()?;
        return match x {
            Token::Identifier(_, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, CstNode::Id { x })
            }
            Token::BracketLeftRound(_) | Token::BracketLeftSquare(_) => self.parse_bracket_expr(),
            // Literals
            Token::LiteralFloat(_, _, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, CstNode::LitFloat { x })
            }
            Token::LiteralInteger(_, _, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, CstNode::LitInt { x })
            }
            Token::LiteralString(_, _, _) => {
                self.eat_next_token("")?;
                self.parse_binop_rhs(0.0, CstNode::LitStr { x })
            }
            // Prefix operators
            Token::OpMinus(_) => {
                self.eat_next_token("-")?;
                return Ok(CstNode::ExprNeg {
                    x: Box::new(self.parse_expr()?),
                });
            }
            Token::OpPlus(_) => {
                self.eat_next_token("+")?;
                return Ok(CstNode::ExprPos {
                    x: Box::new(self.parse_expr()?),
                });
            }
            Token::KeywordNot(_) => {
                self.eat_next_token("not")?;
                return Ok(CstNode::ExprNot {
                    x: Box::new(self.parse_expr()?),
                });
            }
            // If/Else
            Token::KeywordIf(_) => {
                self.eat_next_token("if")?;
                let if_cond = self.parse_expr()?;
                let if_block = self.parse_statements()?;
                let else_block = if let Token::KeywordElse(_) = self.get_token()? {
                    self.eat_next_token("else")?;
                    self.parse_statements()?
                } else {
                    Vec::new()
                };
                return Ok(CstNode::IfElseStatement {
                    cond: Box::new(if_cond),
                    if_block: if_block,
                    else_block: else_block,
                });
            }
            Token::KeywordReturn(_) => {
                self.eat_next_token("return")?;
                return Ok(CstNode::Return {
                    x: Box::new(self.parse_expr()?),
                });
            }
            Token::KeywordLet(_) => {
                self.eat_next_token("let")?;
                return Ok(CstNode::StatementDefVar {
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
    fn parse_statements<'a>(&'a mut self) -> Result<Vec<Box<CstNode>>, ()> {
        self.eat_next_token("{")?;
        let mut r: Vec<Box<CstNode>> = Vec::new();
        loop {
            match self.get_token()? {
                Token::BracketRightCurly(_) => {
                    self.eat_next_token("}")?;
                    return Ok(r);
                }
                // NOTE If-statement is already a statement
                Token::KeywordIf(_) => r.push(Box::new(self.parse_expr()?)),
                Token::KeywordLet(_) => {
                    r.push(Box::new(self.parse_var_def()?));
                }
                _ => {
                    r.push(Box::new(CstNode::Statement {
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

    fn parse_function_def<'a>(&'a mut self) -> Result<CstNode, ()> {
        self.eat_next_token("function")?;
        // TODO 1. Support namespaces
        // TODO 2. Make safe (i.e. don't just unwrap it)
        let name = CstNode::Id {
            x: self.eat_next_token("")?,
        };
        let name = Box::new(self.parse_binop_rhs(get_priority(&Token::parse_dummy("::")), name)?);
        let params = Box::new(self.parse_bracket_expr()?);
        self.eat_next_token("->")?;
        let rets = Box::new(self.parse_expr()?);
        let body = self.parse_statements()?;
        Ok(CstNode::DefFunc {
            name,
            params,
            rets,
            body,
        })
    }

    fn parse_struct_def<'a>(&'a mut self) -> Result<CstNode, ()> {
        self.eat_next_token("struct")?;
        Ok(CstNode::Dummy {})
    }

    fn parse_var_def<'a>(&'a mut self) -> Result<CstNode, ()> {
        self.eat_next_token("let")?;
        let node = CstNode::StatementDefVar {
            name: Box::new(self.parse_expr()?),
        };
        self.eat_next_token(";")?;
        Ok(node)
    }

    fn parse_module_import<'a>(&'a mut self) -> Result<CstNode, ()> {
        self.eat_next_token("module")?;
        let node = self.parse_expr()?;
        self.eat_next_token(";")?;
        Ok(CstNode::Statement {
            x: Box::new(CstNode::ModuleImport { x: Box::new(node) }),
        })
    }

    pub fn parse_module(&mut self) -> Result<(), ()> {
        while let Ok(t) = self.get_token() {
            match t {
                Token::KeywordModule(_) => {
                    let x = self.parse_module_import()?;
                    self.cst.push(x);
                }
                Token::KeywordFunction(_) => {
                    let x = self.parse_function_def()?;
                    self.cst.push(x);
                }
                Token::KeywordStruct(_) => {
                    let x = self.parse_struct_def()?;
                    self.cst.push(x);
                }
                Token::KeywordLet(_) => {
                    let x = self.parse_var_def()?;
                    self.cst.push(x);
                }
                Token::LiteralComment(_, _) => {
                    self.eat_next_token("")?;
                }
                _ => {
                    self.lexer.print_error(&t);
                    eprintln!("Backtrace: {}", Backtrace::force_capture());
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
        for x in &self.cst {
            println!("{}", x.to_string());
        }
    }
}
