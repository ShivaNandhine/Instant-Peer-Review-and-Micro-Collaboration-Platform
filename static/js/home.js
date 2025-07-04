// static/js/home.js

document.addEventListener("DOMContentLoaded", () => {
  loadAllProjects();
  setupSearch();
  setupLogout();
  document.querySelector('.notif-icon')?.addEventListener('click', loadNotifications);
});

async function loadAllProjects() {
  const res = await fetch("/get_all_projects");
  const allProjects = await res.json();
  const container = document.querySelector(".feed");
  container.innerHTML = "";

  for (let proj of allProjects) {
    const commentsRes = await fetch(`/get_comments/${proj._id}`);
    const comments = await commentsRes.json();

    const likesRes = await fetch(`/get_likes/${proj._id}`);
    const likeCount = (await likesRes.json()).count;

    const card = document.createElement("div");
    card.classList.add("idea-card");
    card.id = proj._id;

    card.innerHTML = `
      <div class="idea-header">
        <img src="/static/img/avatar1.jpg" class="avatar" />
        <div class="user-info">
          <h3>${proj.title}</h3>
          <small>by ${proj.user_id} · ${timeSince(new Date(proj.created_at))} ago</small>
        </div>
      </div>
      <p>${proj.description}</p>
      <div><span class="stage-label">Stage:</span> <span class="stage-tag">${proj.stage}</span></div>
      <div class="idea-tags">${proj.tags.split(" ").map(t => `<span>#${t}</span>`).join(" ")}</div>
      <div class="idea-footer">
        <span onclick="likeProject('${proj._id}', this)" data-count="${likeCount}">❤️ ${likeCount}</span>
        <span class="comment-count" data-count="${comments.length}">💬 ${comments.length}</span>
      </div>
      <div class="comment-bar">
        <input type="text" placeholder="Add a comment..." onkeypress="handleComment(event, '${proj._id}')" />
      </div>
      <ul class="comments" id="${proj._id}-comments">
        ${comments.map(c => `<li><strong>${c.user_id}:</strong> ${c.text}</li>`).join("")}
      </ul>
    `;
    container.appendChild(card);
  }
}

async function likeProject(projectId, element) {
  const res = await fetch('/toggle_like', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ project_id: projectId })
  });
  const result = await res.json();

  if (result.status === "success") {
    element.dataset.count = result.count;
    element.innerHTML = `❤️ ${result.count}`;
    element.classList.add("liked");
  }
}

async function handleComment(event, projectId) {
  if (event.key === "Enter" && event.target.value.trim()) {
    const text = event.target.value.trim();
    const res = await fetch("/add_comment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId, text })
    });

    const result = await res.json();
    if (result.status === "success") {
      const ul = document.getElementById(`${projectId}-comments`);
      const li = document.createElement("li");
      li.innerHTML = `<strong>You:</strong> ${text}`;
      ul.appendChild(li);

      event.target.value = "";
      const countSpan = document.querySelector(`#${projectId} .comment-count`);
      let current = parseInt(countSpan.dataset.count || "0");
      countSpan.dataset.count = current + 1;
      countSpan.innerHTML = `💬 ${current + 1}`;
    }
  }
}

async function loadNotifications() {
  const res = await fetch('/get_notifications');
  const data = await res.json();
  const notifList = document.querySelector('.notif-list');
  notifList.innerHTML = "";

  data.forEach(n => {
    const li = document.createElement('li');
    li.classList.add("notif-item");
    li.innerHTML = `
      <div class="notif-icon-box">🔔</div>
      <div class="notif-content">
        <p>${n.message}</p>
        <span class="notif-time">${new Date(n.timestamp).toLocaleString()}</span>
      </div>
      <span class="notif-dismiss" onclick="dismissNotification('${n._id}', this)">✖</span>
    `;
    notifList.appendChild(li);
  });
}

async function dismissNotification(notifId, el) {
  await fetch(`/dismiss_notification/${notifId}`, {
    method: "DELETE"
  });
  el.parentElement.remove();
}

function setupLogout() {
  const logoutLink = document.querySelector(".user-dropdown a[href='index.html']");
  logoutLink?.addEventListener("click", async e => {
    e.preventDefault();
    await fetch("/logout");
    window.location.href = "/";
  });
}

function setupSearch() {
  const input = document.querySelector(".search-bar input");
  input?.addEventListener("keyup", async () => {
    const query = input.value.trim().toLowerCase();
    const res = await fetch("/search_projects?q=" + query);
    const filtered = await res.json();
    const container = document.querySelector(".feed");
    container.innerHTML = "";

    for (let proj of filtered) {
      const commentsRes = await fetch(`/get_comments/${proj._id}`);
      const comments = await commentsRes.json();

      const likesRes = await fetch(`/get_likes/${proj._id}`);
      const likeCount = (await likesRes.json()).count;

      const card = document.createElement("div");
      card.classList.add("idea-card");
      card.id = proj._id;
      card.innerHTML = `
        <div class="idea-header">
          <img src="/static/img/avatar1.jpg" class="avatar" />
          <div class="user-info">
            <h3>${proj.title}</h3>
            <small>by ${proj.user_id}</small>
          </div>
        </div>
        <p>${proj.description}</p>
        <div><span class="stage-label">Stage:</span> <span class="stage-tag">${proj.stage}</span></div>
        <div class="idea-tags">${proj.tags.split(" ").map(t => `<span>#${t}</span>`).join(" ")}</div>
        <div class="idea-footer">
          <span onclick="likeProject('${proj._id}', this)" data-count="${likeCount}">❤️ ${likeCount}</span>
          <span class="comment-count" data-count="${comments.length}">💬 ${comments.length}</span>
        </div>
        <div class="comment-bar">
          <input type="text" placeholder="Add a comment..." onkeypress="handleComment(event, '${proj._id}')" />
        </div>
        <ul class="comments" id="${proj._id}-comments">
          ${comments.map(c => `<li><strong>${c.user_id}:</strong> ${c.text}</li>`).join("")}
        </ul>
      `;
      container.appendChild(card);
    }
  });
}

function timeSince(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  const intervals = [
    [31536000, "year"], [2592000, "month"], [86400, "day"],
    [3600, "hour"], [60, "minute"], [1, "second"]
  ];
  for (const [interval, label] of intervals) {
    const count = Math.floor(seconds / interval);
    if (count >= 1) return `${count} ${label}${count > 1 ? "s" : ""}`;
  }
  return "just now";
}
