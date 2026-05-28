import { Monaco } from "@monaco-editor/react";

export const configureBaboteekLanguage = (monaco: Monaco) => {
  monaco.languages.register({ id: "baboteek" });

  monaco.languages.setMonarchTokensProvider("baboteek", {
    keywords: [
      "program",
      "var",
      "begin",
      "end",
      "if",
      "then",
      "else",
      "while",
      "do",
      "read",
      "write",
      "int",
      "bool",
      "true",
      "false",
    ],
    operators: [":=", ">", "<", ">=", "<=", "=", "!=", "+", "-", "*", "/", "and", "or", "not"],
    tokenizer: {
      root: [
        // Ключевые слова и идентификаторы
        [
          /[a-zA-Z_]\w*/,
          {
            cases: {
              "@keywords": "keyword",
              "@default": "identifier",
            },
          },
        ],
        [/[{}()[\]]/, "bracket"],
        [
          /[<>:=!+-*/]+/,
          {
            cases: {
              "@operators": "operator",
              "@default": "",
            },
          },
        ],
        [/\d+/, "number"],
        [/\{[^}]*\}/, "comment"],
      ],
    },
  });

  monaco.editor.defineTheme("baboteek-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "F43F5E", fontStyle: "bold" }, // Rose-500
      { token: "identifier", foreground: "38BDF8" }, // Sky-400
      { token: "number", foreground: "F59E0B" }, // Amber-500
      { token: "operator", foreground: "10B981" }, // Emerald-500
      { token: "comment", foreground: "64748B", fontStyle: "italic" }, // Slate-500
    ],
    colors: {
      "editor.background": "#0f172a",
    },
  });
};
