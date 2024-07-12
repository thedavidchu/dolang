struct Transpiler {
    input_path: String,
}

fn main() {
    let input_path = std::env::args().nth(1).expect("expected input path");
    let transpiler = Transpiler {
        input_path: input_path,
    };
    println!("Parsing {}", transpiler.input_path);
}
