"""
Restaurant Information Chatbot — Flask Backend
===============================================
• Unlimited continuous conversation (no restart needed)
• Server-side session keeps multi-turn reservation state per browser tab
• Keyword-based NLP: lowercase + punctuation stripping + keyword matching
"""

from flask import Flask, render_template, request, jsonify, session
import string
import uuid

app = Flask(__name__)
# Secret key enables Flask's signed cookie sessions (keeps state per user)
app.secret_key = "spice_ember_secret_2025_xK9#mP"

# ─────────────────────────────────────────────
#  Restaurant Data
# ─────────────────────────────────────────────

RESTAURANT = {
    "name":    "Spice & Ember",
    "tagline": "Premium Desi & Fast Food",
    "address": "42 Food Street, Gulberg III, Lahore",
    "phone":   "+92 300 1234567",
    "email":   "hello@spiceember.pk",
    "hours": {
        "weekdays": "11:00 AM – 11:00 PM  (Mon – Fri)",
        "weekends": "10:00 AM – 12:00 AM  (Sat – Sun)",
    },
    "services":      ["Dine-In", "Takeaway", "Home Delivery"],
    "delivery_time": "30 – 45 minutes",
    "delivery_area": "within 10 km radius",
    "min_order":     "Rs. 500",
}

MENU = {
    "Fast Food": {
        "Classic Beef Burger":      650,
        "Double Smash Burger":      950,
        "Crispy Chicken Burger":    750,
        "Zinger Tower Burger":      850,
        "Loaded Cheese Fries":      450,
        "Chicken Nuggets (10 pcs)": 550,
        "Club Sandwich":            580,
        "Chicken Wrap":             520,
    },
    "Desi Food": {
        "Chicken Karahi":         1_400,
        "Mutton Karahi":          1_900,
        "Beef Biryani (full)":    1_200,
        "Chicken Handi":          1_100,
        "Nihari (per bowl)":        480,
        "Paye (per serving)":       420,
        "Seekh Kabab (6 pcs)":     680,
        "Chicken Tikka (half)":     850,
    },
    "Drinks": {
        "Fresh Lemonade":       200,
        "Mango Shake":          280,
        "Cold Coffee":          320,
        "Strawberry Smoothie":  300,
        "Rooh Afza Sharbat":    150,
        "Soft Drink (can)":     120,
        "Mineral Water":         80,
        "Green Tea":            150,
    },
    "Desserts": {
        "Gulab Jamun (4 pcs)":       220,
        "Kheer (bowl)":              250,
        "Brownie with Ice Cream":    480,
        "Gajar ka Halwa":            280,
        "Chocolate Lava Cake":       520,
        "Kulfi (2 pcs)":             200,
    },
}

CATEGORY_ICONS = {
    "Fast Food": "🍔",
    "Desi Food": "🍛",
    "Drinks":    "🥤",
    "Desserts":  "🍮",
}

# ─────────────────────────────────────────────
#  NLP Helpers
# ─────────────────────────────────────────────

def clean(text: str) -> str:
    """Lowercase + remove punctuation."""
    return text.lower().translate(str.maketrans("", "", string.punctuation))


def has(keywords: list, text: str) -> bool:
    """Return True if ANY keyword appears in text."""
    return any(kw in text for kw in keywords)


# ─────────────────────────────────────────────
#  Session helpers
# ─────────────────────────────────────────────

def get_state() -> dict:
    """Return the current conversation state from Flask session."""
    if "conv" not in session:
        session["conv"] = {"stage": None, "res_name": None, "res_date": None}
    return session["conv"]


def set_state(state: dict):
    """Persist updated state back to Flask session."""
    session["conv"] = state
    session.modified = True


def reset_state():
    """Clear reservation state (keep session alive)."""
    session["conv"] = {"stage": None, "res_name": None, "res_date": None}
    session.modified = True


# ─────────────────────────────────────────────
#  Response Builders
# ─────────────────────────────────────────────

def _welcome():
    return (
        f"👋 Welcome to <strong>{RESTAURANT['name']}</strong>!<br>"
        f"<em>{RESTAURANT['tagline']}</em><br><br>"
        "I'm your virtual assistant. Here's what I can help you with:<br><br>"
        "🍔 <code>menu</code> — View full menu &amp; prices<br>"
        "📅 <code>book table</code> — Reserve a table<br>"
        "🚴 <code>delivery</code> — Delivery info &amp; timing<br>"
        "⏰ <code>hours</code> — Opening hours<br>"
        "📍 <code>location</code> — Find us<br>"
        "📞 <code>contact</code> — Get in touch<br>"
        "💰 <code>prices</code> — Price overview<br><br>"
        "Just type anything — I'm here all day! 😊"
    )


def _full_menu():
    lines = ["🍽️ <strong>Our Complete Menu</strong><br>"]
    for cat, items in MENU.items():
        icon = CATEGORY_ICONS.get(cat, "•")
        lines.append(f"<br><strong>{icon} {cat}</strong>")
        for item, price in items.items():
            lines.append(f"&nbsp;&nbsp;• {item} — <strong>Rs. {price:,}</strong>")
    lines.append("<br><em>Tap a category button for a focused view!</em>")
    return "<br>".join(lines)


def _category_menu(cat: str):
    items = MENU[cat]
    icon  = CATEGORY_ICONS.get(cat, "•")
    lines = [f"{icon} <strong>{cat} Menu</strong><br>"]
    for item, price in items.items():
        lines.append(f"• {item} — <strong>Rs. {price:,}</strong>")
    lines.append(f"<br>Want to see another category? Just type its name!")
    return "<br>".join(lines)


# ─────────────────────────────────────────────
#  Main Chatbot Logic
# ─────────────────────────────────────────────

def chatbot_response(user_msg: str) -> str:
    """
    Processes user_msg, reads/writes Flask session for state,
    returns an HTML response string.
    This function is called on EVERY message — chat runs forever.
    """
    msg   = clean(user_msg)
    state = get_state()
    stage = state.get("stage")

    # ── Multi-turn reservation flow ──────────────────────────────────────
    if stage == "awaiting_name":
        name = user_msg.strip().title()
        state["res_name"] = name
        state["stage"]    = "awaiting_date"
        set_state(state)
        return (
            f"Thanks, <strong>{name}</strong>! 😊<br>"
            "What <strong>date</strong> would you like to reserve?<br>"
            "<em>Example: 20 May 2025</em>"
        )

    if stage == "awaiting_date":
        state["res_date"] = user_msg.strip()
        state["stage"]    = "awaiting_time"
        set_state(state)
        return (
            f"Perfect — <strong>{user_msg.strip()}</strong> it is!<br>"
            "What <strong>time</strong> would you prefer?<br>"
            "<em>Example: 7:30 PM</em>"
        )

    if stage == "awaiting_time":
        time_val  = user_msg.strip()
        name      = state.get("res_name", "Guest")
        date_val  = state.get("res_date", "N/A")
        reset_state()
        return (
            "✅ <strong>Reservation Confirmed!</strong><br><br>"
            f"👤 <strong>Name :</strong> {name}<br>"
            f"📅 <strong>Date :</strong> {date_val}<br>"
            f"🕐 <strong>Time :</strong> {time_val}<br><br>"
            f"We look forward to hosting you at <strong>{RESTAURANT['name']}</strong>!<br>"
            f"Please arrive 5 minutes early.<br>"
            f"For changes call <strong>{RESTAURANT['phone']}</strong>.<br><br>"
            "Is there anything else I can help you with? 😊"
        )

    # ── Cancel reservation mid-flow ──────────────────────────────────────
    if stage and has(["cancel", "stop", "quit", "exit", "nevermind", "back"], msg):
        reset_state()
        return "No problem! Reservation cancelled. How else can I help you? 😊"

    # ── Greetings ────────────────────────────────────────────────────────
    if has(["hi", "hello", "hey", "salam", "assalam", "good morning",
            "good evening", "good afternoon", "hiya", "howdy", "start"], msg):
        return _welcome()

    # ── About / Name ─────────────────────────────────────────────────────
    if has(["who are you", "your name", "restaurant name", "about you",
            "tell me about", "what is this"], msg):
        return (
            f"🍽️ We are <strong>{RESTAURANT['name']}</strong> — "
            f"{RESTAURANT['tagline']}.<br><br>"
            "We serve authentic Desi cuisine, delicious Fast Food, "
            "refreshing Drinks &amp; indulgent Desserts — all under one roof!"
        )

    # ── Hours ─────────────────────────────────────────────────────────────
    if has(["hour", "open", "close", "timing", "schedule", "when do you",
            "what time", "time"], msg):
        return (
            f"⏰ <strong>Opening Hours</strong><br><br>"
            f"📅 {RESTAURANT['hours']['weekdays']}<br>"
            f"🎉 {RESTAURANT['hours']['weekends']}<br><br>"
            "We're open every day — come visit us!"
        )

    # ── Location ─────────────────────────────────────────────────────────
    if has(["location", "address", "where", "direction", "find you",
            "how to reach", "map", "situated", "place"], msg):
        return (
            f"📍 <strong>Our Location</strong><br><br>"
            f"<strong>{RESTAURANT['address']}</strong><br><br>"
            "Look for the big red signboard on Food Street — you can't miss us! 😄<br>"
            "Need directions? Call us and we'll guide you."
        )

    # ── Contact ──────────────────────────────────────────────────────────
    if has(["contact", "phone", "number", "call", "reach", "whatsapp",
            "email", "get in touch"], msg):
        return (
            f"📞 <strong>Contact Us</strong><br><br>"
            f"📱 Phone / WhatsApp: <strong>{RESTAURANT['phone']}</strong><br>"
            f"📧 Email: <strong>{RESTAURANT['email']}</strong><br><br>"
            "Our team is available during opening hours. We'd love to hear from you!"
        )

    # ── Services ─────────────────────────────────────────────────────────
    if has(["service", "offer", "facility", "facilities", "option",
            "available", "provide"], msg):
        svcs = " &nbsp;|&nbsp; ".join(f"✅ {s}" for s in RESTAURANT["services"])
        return (
            f"🏪 <strong>Our Services</strong><br><br>"
            f"{svcs}<br><br>"
            "We aim to make every meal memorable — dine with us or enjoy at home!"
        )

    # ── Full Menu ─────────────────────────────────────────────────────────
    if has(["menu", "food", "what do you have", "show food", "list",
            "dishes", "items", "what can i eat", "all items", "full menu"], msg):
        return _full_menu()

    # ── Category-specific ─────────────────────────────────────────────────
    for cat in MENU:
        words = [w.lower() for w in cat.split()]
        if cat.lower() in msg or all(w in msg for w in words):
            return _category_menu(cat)

    # ── Reservation / Booking ─────────────────────────────────────────────
    if has(["book", "reserve", "reservation", "table", "seat",
            "booking", "want to book", "want to reserve"], msg):
        state["stage"] = "awaiting_name"
        set_state(state)
        return (
            "📅 <strong>Table Reservation</strong><br><br>"
            "I'd love to help you reserve a table!<br>"
            "Let's get the details:<br><br>"
            "First, may I have your <strong>full name</strong>?"
        )

    # ── Delivery ─────────────────────────────────────────────────────────
    if has(["delivery", "deliver", "home delivery", "bring", "send",
            "rider", "order online", "home order"], msg):
        return (
            f"🚴 <strong>Delivery Information</strong><br><br>"
            f"✅ Yes, we offer home delivery!<br>"
            f"⏱️ Estimated Time: <strong>{RESTAURANT['delivery_time']}</strong><br>"
            f"📍 Coverage Area: <strong>{RESTAURANT['delivery_area']}</strong><br>"
            f"💰 Minimum Order: <strong>{RESTAURANT['min_order']}</strong><br><br>"
            f"📞 To place an order call/WhatsApp: <strong>{RESTAURANT['phone']}</strong>"
        )

    # ── Prices ───────────────────────────────────────────────────────────
    if has(["price", "cost", "how much", "rate", "cheap", "expensive",
            "charges", "pricing", "affordable"], msg):
        return (
            "💰 <strong>Price Overview</strong><br><br>"
            "🍔 Fast Food: <strong>Rs. 450 – 950</strong><br>"
            "🍛 Desi Food: <strong>Rs. 420 – 1,900</strong><br>"
            "🥤 Drinks: <strong>Rs. 80 – 320</strong><br>"
            "🍮 Desserts: <strong>Rs. 200 – 520</strong><br><br>"
            "Type a category name for the full price list!"
        )

    # ── Thanks ────────────────────────────────────────────────────────────
    if has(["thank", "thanks", "shukria", "great", "awesome",
            "perfect", "nice", "good", "excellent", "wonderful"], msg):
        return (
            f"😊 You're most welcome! We're always happy to help.<br><br>"
            "Is there anything else you'd like to know about "
            f"<strong>{RESTAURANT['name']}</strong>? 🍽️"
        )

    # ── Bye ───────────────────────────────────────────────────────────────
    if has(["bye", "goodbye", "ciao", "later", "see you",
            "khuda hafiz", "take care", "gotta go"], msg):
        return (
            f"👋 <strong>Goodbye!</strong> Thank you for choosing "
            f"<strong>{RESTAURANT['name']}</strong>.<br>"
            "Come back anytime — we're always here for you! 🌟<br><br>"
            "<em>(The chat is still open — feel free to ask more!)</em>"
        )

    # ── Help ──────────────────────────────────────────────────────────────
    if has(["help", "assist", "support", "guide", "what can you do"], msg):
        return _welcome()

    # ── Fallback ──────────────────────────────────────────────────────────
    return (
        "🤔 I didn't quite catch that — but I'm still here!<br><br>"
        "Here's what I can help with:<br>"
        "• <code>menu</code> — Full menu &amp; prices<br>"
        "• <code>book table</code> — Make a reservation<br>"
        "• <code>delivery</code> — Delivery details<br>"
        "• <code>hours</code> — Opening times<br>"
        "• <code>location</code> — Find us<br>"
        "• <code>contact</code> — Reach us<br><br>"
        "Just type any of the above — I'll keep chatting as long as you need! 😊"
    )


# ─────────────────────────────────────────────
#  Flask Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main chat page."""
    # Give every browser tab a unique session identity
    if "uid" not in session:
        session["uid"] = str(uuid.uuid4())
    return render_template("index.html", restaurant=RESTAURANT)


@app.route("/get", methods=["POST"])
def get_response():
    """
    Endpoint called by JS fetch() on every message.
    Accepts JSON { "msg": "..." } and returns JSON { "response": "..." }.
    Runs forever — no session is destroyed here.
    """
    data     = request.get_json(force=True)
    user_msg = data.get("msg", "").strip()

    if not user_msg:
        return jsonify({"response": "Please type a message! I'm listening... 😊"})

    reply = chatbot_response(user_msg)
    return jsonify({"response": reply})


@app.route("/reset", methods=["POST"])
def reset_chat():
    """Optional: clear conversation state without clearing session."""
    reset_state()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # debug=True → auto-reload on code changes (dev only)
    app.run(debug=True)
