export interface GrammarSection {
  title: string;
  rules: { name: string; value: string; desc?: string }[];
}

export const LEXICAL_RULES: GrammarSection = {
  title: "Лексические правила",
  rules: [
    { name: "Идентификаторы", value: "[a-zA-Z][a-zA-Z0-9_]*", desc: "Имя переменной или программы" },
    { name: "Числа", value: "[0-9]+", desc: "Поддерживаются целые, вещественные и суффиксы систем счисления" },
    { name: "Ключевые слова", value: "program, var, begin, end, if, then, else, while, do, read, write, int, bool, true, false" },
    { name: "Сравнение", value: ">, <, >=, <=, =, !=" },
    { name: "Математика", value: "+, -, *, /" },
    { name: "Логика", value: "and, or, not" }
  ]
};

export const BNF_RULES: GrammarSection = {
  title: "Синтаксис (BNF-нотация)",
  rules: [
    { name: "<program>", value: '"program" "var" <declaration> "begin" <statement> { ";" <statement> } "end"' },
    { name: "<declaration>", value: '<identifier> { "," <identifier> } ":" <type>' },
    { name: "<type>", value: '"int" | "bool"' },
    { name: "<statement>", value: "<compound> | <assignment> | <conditional> | <loop> | <input> | <output>" },
    { name: "<assignment>", value: '<identifier> ":=" <expression>' },
    { name: "<conditional>", value: '"if" <expression> "then" <statement> [ "else" <statement> ]' },
    { name: "<loop>", value: '"while" <expression> "do" <statement>' },
    { name: "<input>", value: '"read(" <identifier> ")"' },
    { name: "<output>", value: '"write(" <expression> ")"' }
  ]
};

export const DEFAULT_CODE = `program 
var a, o, b, h: %;
	r, re: !;
	flag: $;
begin
    a := 0 + 5;  {Это комментарий}
	r := 1.23e+10;
	o := 1234567o;
	b := 101b;
	h := 1ABCh;
	re := 1.234;
	flag := true;
end.`;