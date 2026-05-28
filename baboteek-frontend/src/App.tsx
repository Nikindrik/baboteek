import React, { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import axios from "axios";
import {
  Play,
  BookOpen,
  FolderOpen,
  LogIn,
  UserPlus,
  LogOut,
  X,
  AlertTriangle,
  CheckCircle,
  Clock,
} from "lucide-react";
import { API_URL } from "./config";
import { EXAMPLES, GRAMMAR_RULES } from "./constants";
import { configureBaboteekLanguage } from "./monacoConfig";

interface ErrorDetail {
  message: string;
  row: number;
  column: number;
}

interface CompileResult {
  stage: string;
  is_success: boolean;
  message?: string;
  errors: ErrorDetail[];
}

interface HistoryItem {
  id: number;
  code: string;
  is_success: boolean;
  stage: string;
  created_at: string;
}

export default function App() {
  const [code, setCode] = useState<string>(EXAMPLES[0].code);
  const [result, setResult] = useState<CompileResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Авторизация
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [username, setUsername] = useState<string | null>(localStorage.getItem("username"));
  const [authMode, setAuthMode] = useState<"login" | "register" | null>(null);
  const [authForm, setAuthForm] = useState({ username: "", password: "" });
  const [authError, setAuthError] = useState<string | null>(null);

  // Боковые панели
  const [showGrammar, setShowGrammar] = useState(false);
  const [showExamples, setShowExamples] = useState(false);

  // Перенесли функцию fetchHistory внутрь эффекта, решив проблемы 1, 2 и 3
  useEffect(() => {
    if (!token) {
      return;
    }

    const fetchHistory = async () => {
      try {
        const res = await axios.get(`${API_URL}/compiler/history`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setHistory(res.data);
      } catch (err) {
        console.error("Failed to fetch history", err);
      }
    };

    fetchHistory();
  }, [token]);

  const handleCompile = async () => {
    try {
      setResult(null);
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.post(`${API_URL}/compiler/compile`, { code }, { headers });
      setResult(res.data);

      // Если авторизован, обновляем историю
      if (token) {
        const historyRes = await axios.get(`${API_URL}/compiler/history`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setHistory(historyRes.data);
      }
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response && err.response.data) {
        setResult(err.response.data.detail);
      } else {
        alert("Server error occurred during compilation");
      }
    }
  };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    try {
      if (authMode === "register") {
        await axios.post(`${API_URL}/auth/register`, authForm);
        setAuthMode("login");
        alert("Registration successful! Please login.");
      } else {
        const formData = new FormData();
        formData.append("username", authForm.username);
        formData.append("password", authForm.password);

        const res = await axios.post(`${API_URL}/auth/login`, formData);
        localStorage.setItem("token", res.data.access_token);
        localStorage.setItem("username", authForm.username);
        setToken(res.data.access_token);
        setUsername(authForm.username);
        setAuthMode(null);
        setAuthForm({ username: "", password: "" });
      }
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response) {
        setAuthError(err.response.data.detail || "Authentication failed");
      } else {
        setAuthError("Authentication failed");
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setToken(null);
    setUsername(null);
    setHistory([]); // Сразу очищаем историю здесь синхронно, решая проблему каскадного рендеринга
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Шапка */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-rose-500 flex items-center justify-center font-bold text-white shadow-lg shadow-rose-500/20">
            B
          </div>
          <span className="font-bold text-lg tracking-wider">BABOTEEK IDE</span>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={() => {
              setShowGrammar(true);
              setShowExamples(false);
            }}
            className="flex items-center space-x-2 px-3 py-1.5 text-sm rounded-md hover:bg-slate-800 transition"
          >
            <BookOpen className="w-4 h-4 text-rose-500" />
            <span>Грамматика</span>
          </button>

          <button
            onClick={() => {
              setShowExamples(true);
              setShowGrammar(false);
            }}
            className="flex items-center space-x-2 px-3 py-1.5 text-sm rounded-md hover:bg-slate-800 transition"
          >
            <FolderOpen className="w-4 h-4 text-sky-500" />
            <span>Примеры</span>
          </button>

          {username ? (
            <div className="flex items-center space-x-3 bg-slate-800/50 pl-3 pr-1 py-1 rounded-full border border-slate-700/50">
              <span className="text-sm font-medium text-slate-200">{username}</span>
              <button
                onClick={handleLogout}
                className="p-1.5 hover:bg-rose-500/10 text-rose-400 rounded-full transition"
                title="Выйти"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setAuthMode("login")}
                className="flex items-center space-x-1 px-3 py-1.5 text-sm font-medium bg-slate-800 hover:bg-slate-700 rounded-md transition"
              >
                <LogIn className="w-4 h-4" />
                <span>Войти</span>
              </button>
              <button
                onClick={() => setAuthMode("register")}
                className="flex items-center space-x-1 px-3 py-1.5 text-sm font-medium bg-rose-600 hover:bg-rose-500 rounded-md transition"
              >
                <UserPlus className="w-4 h-4" />
                <span>Регистрация</span>
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Рабочее пространство */}
      <main className="flex flex-1 overflow-hidden">
        {/* Боковая панель: Грамматика */}
        {showGrammar && (
          <div className="w-96 border-r border-slate-800 bg-slate-900 p-6 overflow-y-auto relative animate-fade-in">
            <button
              onClick={() => setShowGrammar(false)}
              className="absolute top-4 right-4 p-1 hover:bg-slate-800 rounded-md"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="font-bold text-lg text-rose-500 mb-4 flex items-center space-x-2">
              <BookOpen className="w-5 h-5" />
              <span>Правила языка</span>
            </h3>
            <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed">
              {GRAMMAR_RULES}
            </pre>
          </div>
        )}

        {/* Боковая панель: Примеры */}
        {showExamples && (
          <div className="w-80 border-r border-slate-800 bg-slate-900 p-6 overflow-y-auto relative">
            <button
              onClick={() => setShowExamples(false)}
              className="absolute top-4 right-4 p-1 hover:bg-slate-800 rounded-md"
            >
              <X className="w-4 h-4" />
            </button>
            <h3 className="font-bold text-lg text-sky-500 mb-4 flex items-center space-x-2">
              <FolderOpen className="w-5 h-5" />
              <span>Примеры программ</span>
            </h3>
            <div className="space-y-3">
              {EXAMPLES.map((ex, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setCode(ex.code);
                    setShowExamples(false);
                  }}
                  className="w-full text-left p-3 rounded-lg border border-slate-800 hover:border-sky-500/50 hover:bg-sky-500/5 transition group"
                >
                  <span className="font-semibold text-sm block text-slate-200 group-hover:text-sky-400">
                    {ex.title}
                  </span>
                  <span className="text-xs text-slate-500 block mt-1">Нажмите, чтобы вставить</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Редактор и вывод */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 min-h-[50%] relative">
            <Editor
              height="100%"
              defaultLanguage="baboteek"
              theme="baboteek-dark"
              value={code}
              onChange={(val) => setCode(val || "")}
              beforeMount={configureBaboteekLanguage}
              options={{
                fontSize: 14,
                fontFamily: "Fira Code, JetBrains Mono, Courier New, monospace",
                minimap: { enabled: false },
                lineNumbers: "on",
                padding: { top: 16 },
              }}
            />
            {/* Кнопка запуска компиляции */}
            <button
              onClick={handleCompile}
              className="absolute bottom-6 right-6 flex items-center space-x-2 px-5 py-2.5 bg-rose-600 hover:bg-rose-500 rounded-lg font-semibold shadow-lg shadow-rose-600/20 hover:shadow-rose-600/30 transition-all active:scale-95 z-10"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>Запустить</span>
            </button>
          </div>

          {/* Панель результатов */}
          <div className="h-64 border-t border-slate-800 bg-slate-900/50 flex flex-col">
            <div className="px-6 py-3 border-b border-slate-800 bg-slate-900 flex justify-between items-center">
              <span className="text-xs font-bold tracking-wider text-slate-400 uppercase">
                Панель результатов
              </span>
              {result && (
                <span
                  className={`text-xs px-2 py-0.5 rounded-full font-semibold uppercase ${
                    result.is_success
                      ? "bg-emerald-500/10 text-emerald-400"
                      : "bg-rose-500/10 text-rose-400"
                  }`}
                >
                  {result.stage}
                </span>
              )}
            </div>

            <div className="flex-1 p-6 overflow-y-auto font-mono text-sm">
              {result ? (
                result.is_success ? (
                  <div className="flex items-start space-x-3 text-emerald-400 bg-emerald-500/5 p-4 rounded-lg border border-emerald-500/20">
                    <CheckCircle className="w-5 h-5 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-slate-200">Компиляция успешна!</span>
                      <p className="text-xs text-emerald-500/80 mt-1">{result.message}</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {result.errors.map((err, idx) => (
                      <div
                        key={idx}
                        className="flex items-start space-x-3 text-rose-400 bg-rose-500/5 p-4 rounded-lg border border-rose-500/20"
                      >
                        <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
                        <div>
                          <span className="font-bold text-slate-200">
                            Ошибка разбора ({result.stage})
                          </span>
                          <p className="text-xs text-rose-400/80 mt-1">{err.message}</p>
                          <span className="text-xs text-slate-500 block mt-2">
                            Строка: <b className="text-slate-400">{err.row}</b>, Колонка:{" "}
                            <b className="text-slate-400">{err.column}</b>
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-1">
                  <span>Готов к работе.</span>
                  <span className="text-xs">Нажмите "Запустить" для проверки кода.</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Сайдбар: История (только для авторизованных) */}
        {token && (
          <div className="w-72 border-l border-slate-800 bg-slate-900 p-6 overflow-y-auto flex flex-col">
            <h3 className="font-bold text-sm text-slate-400 mb-4 flex items-center space-x-2 tracking-wider uppercase">
              <Clock className="w-4 h-4 text-rose-500" />
              <span>История</span>
            </h3>

            <div className="space-y-3 flex-1 overflow-y-auto">
              {history.length > 0 ? (
                history.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setCode(item.code)}
                    className="w-full text-left p-2.5 rounded-lg border border-slate-800 hover:bg-slate-800 transition flex items-center justify-between"
                  >
                    <div className="min-w-0">
                      <span className="text-xs font-semibold text-slate-300 block truncate">
                        {item.code.split("\n")[0] || "Empty Code"}
                      </span>
                      <span className="text-[10px] text-slate-500 mt-0.5 block">
                        {new Date(item.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <span
                      className={`w-2 h-2 rounded-full shrink-0 ml-2 ${
                        item.is_success ? "bg-emerald-500" : "bg-rose-500"
                      }`}
                    />
                  </button>
                ))
              ) : (
                <div className="text-xs text-slate-600 text-center py-8">История пока пуста</div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Окна Авторизации (Модалка) */}
      {authMode && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl w-96 relative shadow-2xl">
            <button
              onClick={() => setAuthMode(null)}
              className="absolute top-4 right-4 p-1 hover:bg-slate-800 rounded-md"
            >
              <X className="w-4 h-4" />
            </button>

            <h3 className="font-bold text-xl text-slate-100 mb-6">
              {authMode === "register" ? "Создать аккаунт" : "Войти в систему"}
            </h3>

            <form onSubmit={handleAuth} className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase block mb-1.5">
                  Username
                </label>
                <input
                  type="text"
                  required
                  value={authForm.username}
                  onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none rounded-lg px-3 py-2 text-sm text-slate-100"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-400 uppercase block mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={authForm.password}
                  onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 focus:border-rose-500 focus:ring-1 focus:ring-rose-500 outline-none rounded-lg px-3 py-2 text-sm text-slate-100"
                />
              </div>

              {authError && (
                <div className="text-xs text-rose-500 bg-rose-500/5 border border-rose-500/10 p-3 rounded-lg">
                  {authError}
                </div>
              )}

              <button
                type="submit"
                className="w-full py-2.5 bg-rose-600 hover:bg-rose-500 rounded-lg font-semibold text-sm shadow-lg shadow-rose-600/20 transition"
              >
                {authMode === "register" ? "Зарегистрироваться" : "Войти"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
