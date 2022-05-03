Notes of Portability in C
=========================

1. Variable Names
	* Internal variables are only guaranteed unique for the first 31 characters.
	(you can stick an arbitrary number of insignificant letters after???)
	* External variables (and function names) are only guaranteed unique for the
	first 6 characters. I think this refers specifically to external function
	names.
2. Using Libraries
	* Use the standard libraries where possible to promote portability. For
	example, the character encoding is not guaranteed to be ASCII. This also
	means one should use `'a'` to represent characters rather than numeric
	values.
3. Global Variables
	* Declare global variables as `extern <type> <name>;` at the top of the
	function if you want the user to be able to quickly see that the function
	uses global variables.
	* I am not sure whether the variable's scope will have to be the whole
	project or just the translation unit or either?
4. Explicitly Mark Unsigned and Long Numbers
	* `123L` is a `long`, `123U` is an `unsigned`, and `123UL` is an
	`unsigned long`.
	* For floating-point numbers, the default is `double`. That is, `123.0` is a
	`double`, `123.0F` is a `float`, and `123.0L` is a `long double`.
5. Immutability of `const`
	* Do not modify a `const` variable. Doing so is machine defined.
6. Constraints on Numeric Values with Certain Operators
	* Use `%` only on integral types.
	* `%` and `/` only for positive numbers, because truncation up or down is
	machine defined. Underflow/zero/overflow is machine defined.
	* Do not compare unsigned to negative signed values, because the negative
	signed value will be promoted.
		* E.g. -1L < 1U, because -1L < 1L (promotion ok). BUT: -1L > 1UL,
		because -1L goes to the maximum `unsigned long`.
	* Do not use `>>` on negative signed values. Whether to pad with 1 or 0 is
	machine defined.
8. Automatic cast if header of function available.
	* E.g. `double sqrt(double x)` means `sqrt(12L)` is equivalent to
	`sqrt((double)12L)`.
9. Wrap assignments that you take the value of in parentheses.
	* E.g. `if (!(x = get_value())) { /* ... */ }`.
10. Do not convert `double` to `float`, because rounding/truncation is machine
defined.
11. True is non-zero, not necessarily 1. This means, do not check
`if (x == true)`; check `if (x != false)` or `if (x)`.
