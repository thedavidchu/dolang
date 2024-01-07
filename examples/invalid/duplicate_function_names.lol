function duplicate() -> int32 {
    return 0;
}

# Duplicate function already defined.
function duplicate() -> int32 {
    return 1;
}

function main() -> int32 {
    let r: int64 = duplicate();
    return 0;
}