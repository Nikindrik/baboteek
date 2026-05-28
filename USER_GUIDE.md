# Baboteek Web IDE: User Guide

<p align="center">
  <img src="https://raw.githubusercontent.com/lucide-react/lucide/main/icons/graduation-cap.svg" alt="User Guide" width="80" height="80">
</p>

This guide explains how to use the Baboteek Web IDE, write valid programs, understand the built-in compiler, and troubleshoot compilation errors.

## 🚀 Basic Workflow

1.  **Authentication**: Click **Register** on the top right to create an account, then **Login**.
2.  **Using Examples**: Open the **Examples (Примеры)** drawer in the top navigation bar. Click a preset (e.g., *While Loop*) to paste the boilerplate code directly into the editor.
3.  **Compiling**: Press the red **Run (Запустить)** button (or press `Ctrl + Enter` inside the editor) to run the static analysis pipeline.

---

## 📝 Writing Code

All programs in the Baboteek language must follow a strict structural template:

```pascal
program 
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
end.
```

### Essential Rules:
*   **The Dot**: A program *must* end with a dot `.` immediately following the closing `end` keyword.
*   **Semicolons**: Use semicolons `;` to separate statements within `begin ... end` blocks.
*   **Types**: 
    *   `int`: represents integer values (e.g., `42`, `100d`, `101b` for binary).
    *   `bool`: represents logical states (`true` or `false`).

---

## 🔍 Resolving Compilation Errors

The compiler analyzes your code in three sequential stages. If an error is found, the execution halts immediately and highlights the issue in the **Result Panel** at the bottom of the screen.

### 1. Lexical Errors (Stage: `lexical`)
Occur when you write characters that are not part of the language alphabet.
*   *Example Error*: `Unexpected character '@'`
*   *Cause*: Using operators or symbols like `@`, `#`, `?`, or cyrillic letters outside of comments.

### 2. Syntax Errors (Stage: `syntax`)
Occur when the grammatical structure of your code is broken.
*   *Example Error*: `Expected DELIMITER ';', but got KEYWORD 'end'`
*   *Cause*: Forgetting a semicolon `;` at the end of an assignment or expression statement.

### 3. Semantic Errors (Stage: `semantic`)
Occur when your program has correct grammar but contains logical type or scope contradictions.
*   *Example Error*: `Variable 'z' is not declared`
*   *Cause*: Trying to use variable `z` in an expression without declaring it first in the `var` section.
*   *Example Error*: `Type mismatch: cannot assign bool to int`
*   *Cause*: Trying to assign a relational expression (like `x > 5` which resolves to `bool`) to a variable declared as `int`.