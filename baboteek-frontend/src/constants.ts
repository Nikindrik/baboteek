export const GRAMMAR_RULES = `
=== ЛЕКСИЧЕСКИЕ ПРАВИЛА ===
• Идентификаторы: [a-zA-Z][a-zA-Z0-9_]*
• Числа: [0-9]+ (целые и вещественные)
• Ключевые слова: program, var, begin, end, if, then, else, while, do, read, write, int, bool, true, false
• Операторы сравнения: >, <, >=, <=, =, !=
• Математика: +, -, *, /
• Логика: and, or, not

=== СИНТАКСИС (BNF) ===
<program> ::= "program" "var" <declaration> "begin" <statement> { ";" <statement> } "end"
<declaration> ::= <identifier> { "," <identifier> } ":" <type>
<type> ::= "int" | "bool"
<statement> ::= <compound> | <assignment> | <conditional> | <loop> | <input> | <output>
<assignment> ::= <identifier> ":=" <expression>
<conditional> ::= "if" <expression> "then" <statement> [ "else" <statement> ]
<loop> ::= "while" <expression> "do" <statement>
`;

export const EXAMPLES = [
  {
    title: "Простое сложение",
    code: `program 
var a, b, res: int;
begin
    a := 10;
    b := 20;
    res := a + b;
    write(res)
end.`,
  },
  {
    title: "Ветвление (if-else)",
    code: `program 
var x, y: int;
    is_greater: bool;
begin
    x := 15;
    y := 10;
    if x > y then
        is_greater := true
    else
        is_greater := false;
    write(is_greater)
end.`,
  },
  {
    title: "Цикл (while)",
    code: `program 
var counter, sum: int;
begin
    counter := 1;
    sum := 0;
    while counter < 5 do begin
        sum := sum + counter;
        counter := counter + 1
    end;
    write(sum)
end.`,
  },
];
