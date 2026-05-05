/**
 * Spice & Ember — Restaurant Chatbot JS
 * =======================================
 * • Sends messages to Flask /get via fetch (no page reload)
 * • Chat runs FOREVER — there is no stop condition
 * • Server manages conversation state (reservation flow etc.)
 * • UI: typing indicator, auto-scroll, auto-resize textarea, timestamps
 */

"use strict";

// ── DOM references ──────────────────────────────────────────────────────────
const chatBox   = document.getElementById("chat-box");
const input     = document.getElementById("user-input");
const sendBtn   = document.getElementById("send-btn");

// ── Helpers ─────────────────────────────────────────────────────────────────

/** Scroll chat to the very bottom smoothly. */
function scrollBottom() {
  chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: "smooth" });
}

/** Current time formatted as HH:MM AM/PM */
function nowTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/** Escape user text to prevent XSS (bot HTML is trusted from server). */
function esc(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ── Render helpers ──────────────────────────────────────────────────────────

/**
 * Append a message bubble to #chat-box.
 * @param {string} who   "user" | "bot"
 * @param {string} html  Content — user text is escaped, bot HTML is trusted
 */
function appendMessage(who, html) {
  const row = document.createElement("div");
  row.className = `msg-row ${who}`;

  // Bot gets an avatar icon
  if (who === "bot") {
    const av = document.createElement("div");
    av.className = "msg-avatar";
    av.textContent = "🍽";
    row.appendChild(av);
  }

  // Bubble
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = html;

  // Timestamp
  const ts = document.createElement("div");
  ts.className = "msg-time";
  ts.textContent = nowTime();

  const wrapper = document.createElement("div");
  wrapper.style.display = "flex";
  wrapper.style.flexDirection = "column";
  if (who === "user") wrapper.style.alignItems = "flex-end";

  wrapper.appendChild(bubble);
  wrapper.appendChild(ts);
  row.appendChild(wrapper);

  chatBox.appendChild(row);
  scrollBottom();
}

/** Show animated typing indicator while waiting for response. */
function showTyping() {
  removeTyping(); // safety — never duplicate
  const row = document.createElement("div");
  row.className = "typing-row";
  row.id        = "typing-ind";

  const av = document.createElement("div");
  av.className = "msg-avatar";
  av.textContent = "🍽";

  const bub = document.createElement("div");
  bub.className = "typing-bubble";
  bub.innerHTML = `
    <span class="tdot"></span>
    <span class="tdot"></span>
    <span class="tdot"></span>`;

  row.appendChild(av);
  row.appendChild(bub);
  chatBox.appendChild(row);
  scrollBottom();
}

/** Remove typing indicator. */
function removeTyping() {
  const el = document.getElementById("typing-ind");
  if (el) el.remove();
}

// ── Core send/receive loop ───────────────────────────────────────────────────
// This is the heart of "unlimited chat":
// sendMessage() → fetch /get → appendMessage(bot) → done.
// The function can be called again and again — nothing ever stops it.

/**
 * Read user input, render it, POST to Flask, render bot reply.
 * Can be called unlimited times.
 */
async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  // Render user bubble immediately
  appendMessage("user", esc(text));
  input.value = "";
  autoResize();

  // Disable send while waiting (prevents double-send)
  sendBtn.disabled = true;
  showTyping();

  // Add a tiny random delay so the typing indicator is visible
  const delay = 400 + Math.random() * 450;
  await new Promise(r => setTimeout(r, delay));

  try {
    const res = await fetch("/get", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      // NOTE: NO session data sent — server manages state via Flask session cookie
      body: JSON.stringify({ msg: text }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    removeTyping();
    appendMessage("bot", data.response);

  } catch (err) {
    removeTyping();
    appendMessage("bot",
      `⚠️ <strong>Connection error</strong> — couldn't reach the server.<br>
       Please make sure <code>app.py</code> is running, then try again.<br>
       <em>(${esc(err.message)})</em>`
    );
  }

  // Re-enable — ready for the NEXT message (chat continues forever)
  sendBtn.disabled = false;
  input.focus();
}

// ── Quick-action buttons ─────────────────────────────────────────────────────

/** Called by quick-action sidebar buttons. Injects text and sends. */
function quickSend(text) {
  input.value = text;
  sendMessage();
}

// ── Reset chat ───────────────────────────────────────────────────────────────

/** Clear UI and reset server-side conversation state (reservation flow etc.) */
async function resetChat() {
  // Clear visual chat (keep date chip)
  const chip = chatBox.querySelector(".date-chip");
  chatBox.innerHTML = "";
  if (chip) chatBox.appendChild(chip);

  // Tell server to clear state
  try {
    await fetch("/reset", { method: "POST" });
  } catch (_) { /* ignore */ }

  // Show welcome again after a small pause
  setTimeout(() => {
    appendMessage("bot",
      "🔄 Chat reset! I'm ready to help again.<br><br>" +
      "Type <code>hello</code> to see what I can do, or just ask away! 😊"
    );
    input.focus();
  }, 150);
}

// ── Textarea auto-resize ─────────────────────────────────────────────────────

function autoResize() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 130) + "px";
}

input.addEventListener("input", autoResize);

// ── Keyboard handling ────────────────────────────────────────────────────────
// Enter → send, Shift+Enter → newline

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) sendMessage();
  }
});

// ── Button click ─────────────────────────────────────────────────────────────
sendBtn.addEventListener("click", () => {
  if (!sendBtn.disabled) sendMessage();
});

// ── Boot welcome message ─────────────────────────────────────────────────────

window.addEventListener("DOMContentLoaded", () => {
  // Small delay so fonts load before first render
  setTimeout(() => {
    appendMessage("bot",
      "👋 Welcome to <strong>Spice & Ember</strong>!<br>" +
      "<em>Premium Desi & Fast Food</em><br><br>" +
      "I'm your virtual assistant — here to help <strong>all day, every day</strong>! 🔥<br><br>" +
      "Here's what I can do:<br>" +
      "🍔 <code>menu</code> — Full menu & prices<br>" +
      "📅 <code>book table</code> — Reserve a table<br>" +
      "🚴 <code>delivery</code> — Delivery info<br>" +
      "⏰ <code>hours</code> — Opening times<br>" +
      "📍 <code>location</code> — Find us<br>" +
      "📞 <code>contact</code> — Get in touch<br><br>" +
      "Just type anything below — the chat never stops! 😊"
    );
    input.focus();
  }, 350);
});
