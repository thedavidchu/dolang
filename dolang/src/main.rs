use std::env;
use std::path::Path;

mod lexer;

fn main() -> Result<(), i32> {
    let args: Vec<String> = env::args().collect();
    dbg!(&args);

    if args.len() != 3 {
        eprintln!("Usage: exe <input> <output>");
        return Err(-1);
    }
    let input_path = Path::new(&args[1]);
    let output_path = Path::new(&args[2]);

    let mut lexer = lexer::Lexer::new(&input_path, &output_path).expect("invalid lexer");
    lexer.run();
    lexer.print_csv();
    Ok(())
}
