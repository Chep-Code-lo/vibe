let token = localStorage.getItem('token') || '';
let currentSessionId = null;
let questions = [];
let qIndex = 0;

const el = (id) => document.getElementById(id);
const authSection = el('authSection');
const studySection = el('studySection');
const quizSection = el('quizSection');
const resultSection = el('resultSection');

function setMsg(id, msg) { el(id).textContent = msg || ''; }

async function api(path, method = 'GET', body) {
  const res = await fetch(path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

function ensureLoggedInUI() {
  if (token) {
    studySection.classList.remove('hidden');
    loadTopics();
  }
}

async function login() {
  try {
    const data = await api('/api/v1/auth/login', 'POST', {
      email: el('email').value,
      password: el('password').value,
    });
    token = data.data.accessToken;
    localStorage.setItem('token', token);
    setMsg('authMsg', 'Đăng nhập thành công');
    ensureLoggedInUI();
  } catch (e) {
    setMsg('authMsg', e.message);
  }
}

async function register() {
  try {
    const data = await api('/api/v1/auth/register', 'POST', {
      email: el('email').value,
      password: el('password').value,
      fullName: el('fullName').value || 'Student',
    });
    token = data.data.accessToken;
    localStorage.setItem('token', token);
    setMsg('authMsg', 'Đăng ký thành công');
    ensureLoggedInUI();
  } catch (e) {
    setMsg('authMsg', e.message);
  }
}

async function loadTopics() {
  try {
    const data = await api('/api/v1/topics');
    const select = el('topicSelect');
    select.innerHTML = '';
    data.data.forEach((t) => {
      const opt = document.createElement('option');
      opt.value = t.id;
      opt.textContent = `${t.name} - ${t.description || ''}`;
      select.appendChild(opt);
    });
  } catch (e) {
    setMsg('topicMsg', e.message);
  }
}

async function startQuiz() {
  try {
    const topicId = el('topicSelect').value;
    const s = await api('/api/v1/sessions', 'POST', { topicId });
    currentSessionId = s.data.sessionId;
    const q = await api(`/api/v1/questions?topicId=${encodeURIComponent(topicId)}`);
    questions = q.data;
    qIndex = 0;
    quizSection.classList.remove('hidden');
    resultSection.classList.add('hidden');
    renderQuestion();
  } catch (e) {
    setMsg('topicMsg', e.message);
  }
}

function renderQuestion() {
  const q = questions[qIndex];
  if (!q) {
    submitSession();
    return;
  }
  el('questionText').textContent = `Câu ${qIndex + 1}: ${q.content}`;
  const box = el('options');
  box.innerHTML = '';
  q.options.forEach((o) => {
    const btn = document.createElement('button');
    btn.className = 'opt';
    btn.textContent = o.content;
    btn.onclick = () => answerQuestion(q.id, o.id);
    box.appendChild(btn);
  });
  setMsg('quizMsg', '');
}

async function answerQuestion(questionId, selectedOptionId) {
  try {
    const res = await api(`/api/v1/sessions/${currentSessionId}/attempts`, 'POST', {
      questionId,
      selectedOptionId,
      latencyMs: Math.floor(Math.random() * 6000) + 500,
    });
    setMsg('quizMsg', res.data.isCorrect ? '✅ Đúng rồi' : '❌ Sai - hệ thống sẽ phân tích lỗi tư duy của bạn');
  } catch (e) {
    setMsg('quizMsg', e.message);
  }
}

async function nextQuestion() {
  qIndex += 1;
  renderQuestion();
}

async function submitSession() {
  try {
    const result = await api(`/api/v1/sessions/${currentSessionId}/submit`, 'POST');
    el('resultBox').textContent = JSON.stringify(result.data, null, 2);
    const analytics = await api('/api/v1/me/analytics/errors');
    el('analyticsBox').textContent = JSON.stringify(analytics.data, null, 2);
    resultSection.classList.remove('hidden');
    quizSection.classList.add('hidden');
  } catch (e) {
    setMsg('quizMsg', e.message);
  }
}

el('btnLogin').onclick = login;
el('btnRegister').onclick = register;
el('btnStart').onclick = startQuiz;
el('btnNext').onclick = nextQuestion;
ensureLoggedInUI();
