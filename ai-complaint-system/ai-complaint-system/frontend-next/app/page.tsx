
"use client";
import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function Home() {
  const [text, setText] = useState("");
  const [loginToken, setLoginToken] = useState<string | null>(null);
  const [cls, setCls] = useState<any>(null);
  const [rt, setRt] = useState<any>(null);

  const login = async () => {
    const r = await fetch(`${API}/auth/login`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({username:"admin", password:"admin123!"})
    });
    const j = await r.json(); setLoginToken(j.access_token);
  };

  const classify = async () => {
    const r = await fetch(`${API}/ml/classify`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({text})
    });
    setCls(await r.json());
  };

  const route = async () => {
    const r = await fetch(`${API}/ml/route`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({text})
    });
    setRt(await r.json());
  };

  const submit = async () => {
    if (!loginToken) await login();
    const fd = new FormData();
    fd.append("title","테스트 신고");
    fd.append("content", text);
    const r = await fetch(`${API}/reports/submit`, {
      method: "POST",
      headers: { Authorization: `Bearer ${loginToken}` },
      body: fd
    });
    alert(await r.text());
  };

  return (
    <main style={{maxWidth:720, margin:"40px auto", padding:20}}>
      <h1>AI 기반 캠퍼스 불편사항 신고(알파)</h1>
      <textarea value={text} onChange={e=>setText(e.target.value)}
        placeholder="신고 내용을 입력하세요" style={{width:"100%",height:140}} />
      <div style={{display:"flex", gap:8, marginTop:10}}>
        <button onClick={classify}>분류</button>
        <button onClick={route}>저신뢰 라우팅</button>
        <button onClick={submit}>신고 제출(메일)</button>
      </div>
      {cls && <pre style={{marginTop:12}}>{JSON.stringify(cls,null,2)}</pre>}
      {rt && <pre style={{marginTop:12}}>{JSON.stringify(rt,null,2)}</pre>}
    </main>
  );
}
