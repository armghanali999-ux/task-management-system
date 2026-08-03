(() => {
  "use strict";

  const token = () => localStorage.getItem("auth-token") || "";
  const headers = (json = false) => ({
    ...(json ? { "Content-Type": "application/json" } : {}),
    ...(token() ? { Authorization: `Token ${token()}` } : {}),
  });
  const payload = (form) => Object.fromEntries(new FormData(form).entries());
  const escapeHtml = (value = "") => String(value).replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[char]);
  const items = (data) => Array.isArray(data) ? data : (data.results || []);

  async function api(url, options = {}) {
    const response = await fetch(url, { ...options, headers: { ...headers(Boolean(options.body)), ...(options.headers || {}) } });
    const data = response.status === 204 ? null : await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || data.detail || JSON.stringify(data));
    return data;
  }

  function errorFor(form, error) {
    const box = form.querySelector("[data-form-error]");
    if (box) { box.textContent = error.message; box.hidden = false; }
  }

  async function authenticate(form, endpoint) {
    try {
      const data = await api(endpoint, { method: "POST", body: JSON.stringify(payload(form)) });
      localStorage.setItem("auth-token", data.token);
      localStorage.setItem("taskflow-user", JSON.stringify(data.user));
      location.assign("/dashboard/");
    } catch (error) { errorFor(form, error); }
  }

  async function loadProjects() {
    const host = document.querySelector("[data-project-list]");
    const projects = items(await api("/api/projects/"));
    if (host) host.innerHTML = projects.length ? projects.map((project) => `<div class="col-md-6"><a class="card card-body text-decoration-none h-100" href="/projects/${project.id}/"><div class="d-flex justify-content-between"><h2 class="h5">${escapeHtml(project.title)}</h2><span class="badge bg-primary">${escapeHtml(project.status_display)}</span></div><p class="text-muted mb-2">${project.task_count} tasks</p><div class="progress"><div class="progress-bar" style="width:${project.progress}%">${project.progress}%</div></div></a></div>`).join("") : "<p>No projects yet.</p>";
    const select = document.querySelector("[data-project-options]");
    if (select) select.insertAdjacentHTML("beforeend", projects.map((project) => `<option value="${project.id}">${escapeHtml(project.title)}</option>`).join(""));
    return projects;
  }

  async function loadTasks() {
    const host = document.querySelector("[data-task-list]");
    const tasks = items(await api("/api/tasks/"));
    if (host) host.innerHTML = tasks.length ? tasks.map((task) => `<tr><td><a href="/tasks/${task.id}/">${escapeHtml(task.title)}</a></td><td>${escapeHtml(task.status_display)}</td><td><span class="badge bg-secondary">${escapeHtml(task.priority_display)}</span></td><td>${task.due_date || "—"}</td></tr>`).join("") : '<tr><td colspan="4">No tasks yet.</td></tr>';
  }

  async function loadDetail() {
    const id = location.pathname.split("/").filter(Boolean).pop();
    const projectHost = document.querySelector("[data-project-detail]");
    if (projectHost) {
      const project = await api(`/api/projects/${id}/`);
      projectHost.innerHTML = `<div class="d-flex justify-content-between"><h1>${escapeHtml(project.title)}</h1><span class="badge bg-primary align-self-start">${escapeHtml(project.status_display)}</span></div><p>${escapeHtml(project.description)}</p><p><strong>Owner:</strong> ${escapeHtml(project.owner?.display_name || project.owner?.email)} · <strong>Progress:</strong> ${project.progress}% · <strong>Deadline:</strong> ${project.end_date || "Not set"}</p>`;
    }
    const taskHost = document.querySelector("[data-task-detail]");
    if (taskHost) {
      const task = await api(`/api/tasks/${id}/`);
      taskHost.innerHTML = `<div class="d-flex justify-content-between"><h1>${escapeHtml(task.title)}</h1><span class="badge bg-primary align-self-start">${escapeHtml(task.status_display)}</span></div><p>${escapeHtml(task.description)}</p><p><strong>Priority:</strong> ${escapeHtml(task.priority_display)} · <strong>Due:</strong> ${task.due_date || "Not set"}</p>`;
      renderComments(task.comments || []);
    }
  }

  function renderComments(comments) {
    const host = document.querySelector("[data-comment-list]");
    if (host) host.innerHTML = comments.length ? comments.map((comment) => `<article class="list-group-item"><strong>${escapeHtml(comment.author?.display_name || comment.author?.email)}</strong><p class="mb-0">${escapeHtml(comment.content)}</p><small>${new Date(comment.created_at).toLocaleString()}</small></article>`).join("") : "<p>No comments yet.</p>";
  }

  async function loadActivity() {
    const activity = items(await api("/api/activity/"));
    const markup = activity.length ? activity.map((entry) => `<article class="list-group-item"><strong>${escapeHtml(entry.activity_type_display)}</strong><p class="mb-0">${escapeHtml(entry.description)}</p><small>${new Date(entry.created_at).toLocaleString()}</small></article>`).join("") : "<p>No activity yet.</p>";
    document.querySelectorAll("[data-activity-list], [data-recent-activity]").forEach((host) => { host.innerHTML = markup; });
  }

  async function loadProfile() {
    const user = await api("/api/users/me/");
    const form = document.querySelector('[data-form="profile"]');
    Object.entries(user).forEach(([name, value]) => { if (form.elements[name] && typeof value !== "object") form.elements[name].value = value || ""; });
    localStorage.setItem("taskflow-user", JSON.stringify(user));
  }

  document.addEventListener("DOMContentLoaded", async () => {
    const authenticated = Boolean(token());
    document.querySelectorAll("[data-authenticated-nav]").forEach((node) => { node.hidden = !authenticated; });
    document.querySelectorAll("[data-anonymous-nav]").forEach((node) => { node.hidden = authenticated; });
    const user = JSON.parse(localStorage.getItem("taskflow-user") || "null");
    document.querySelectorAll("[data-user-email]").forEach((node) => { node.textContent = user?.email || "Account"; });
    document.querySelector('[data-form="login"]')?.addEventListener("submit", (event) => { event.preventDefault(); authenticate(event.currentTarget, "/api/users/login/"); });
    document.querySelector('[data-form="register"]')?.addEventListener("submit", (event) => { event.preventDefault(); authenticate(event.currentTarget, "/api/users/register/"); });
    document.querySelector('[data-action="logout"]')?.addEventListener("click", async () => { try { await api("/api/users/logout/", { method: "POST" }); } finally { localStorage.removeItem("auth-token"); localStorage.removeItem("taskflow-user"); location.assign("/"); } });
    if (!authenticated && document.querySelector("[data-dashboard], [data-project-list], [data-task-list], [data-activity-list], [data-form='profile']")) { location.assign("/login/"); return; }
    try {
      if (document.querySelector("[data-project-list], [data-project-options]")) await loadProjects();
      if (document.querySelector("[data-task-list]")) await loadTasks();
      if (document.querySelector("[data-project-detail], [data-task-detail]")) await loadDetail();
      if (document.querySelector("[data-activity-list], [data-recent-activity]")) await loadActivity();
      if (document.querySelector('[data-form="profile"]')) await loadProfile();
    } catch (error) { showNotification(error.message, "danger"); }
  });

  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!form.matches('[data-form="project"], [data-form="task"], [data-form="comment"], [data-form="profile"]')) return;
    event.preventDefault();
    const kind = form.dataset.form;
    const id = location.pathname.split("/").filter(Boolean).pop();
    const routes = { project: ["/api/projects/", "POST"], task: ["/api/tasks/", "POST"], comment: [`/api/tasks/${id}/add_comment/`, "POST"], profile: ["/api/users/update_profile/", "PATCH"] };
    try { await api(routes[kind][0], { method: routes[kind][1], body: JSON.stringify(payload(form)) }); location.reload(); } catch (error) { errorFor(form, error); }
  });
})();
