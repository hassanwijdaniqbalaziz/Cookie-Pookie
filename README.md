# 🍪 COOKIE POOKIE — Freshly Homemade

> **Artisanal, Chewy & Decadent Treats Baked with Love**  
> An interactive, responsive Streamlit web application tailored for the **COOKIE POOKIE** brand.

---

## 🌟 Brand Highlights

* **Brand Name:** COOKIE POOKIE
* **Tagline:** Freshly Homemade
* **Theme:** Artisanal Chocolate Ganache, Golden Roasted Caramel & Vanilla Cream
* **Price Point:** Flat **PKR 200** per handcrafted treat
* **Hotlines:** `0300-8237849` & `0300-8233395`

---

## 🚀 Key Features

### 1. 🏠 Home Sweet Home
* **Smooth Floating Cookie Animation:** High-resolution baked cookie graphics (Choc Chip, Brookie, Brownie) floating gracefully across the screen without ugly unicode emojis or rendering glitches.
* **Hero Banner:** Welcoming brand story highlighting 100% real butter, Belgian chocolate chunks, and small-batch baking.
* **Animated Mascot Display:** Interactive glowing badge featuring the official Cookie Pookie mascot from `assets/logo.jpg`.
* **Value Pillars:** Quick overview of ingredients, quality standards, and customer testimonials.

### 2. 🍪 Handcrafted Signature Menu
* **Flat PKR 200** pricing across all signature treats:
  1. **Choc Chip Cookie:** Classic golden-crisp edges with soft, chewy center and pools of Belgian semi-sweet chocolate chunks.
  2. **BROOKIE:** The ultimate mashup—half decadent fudgy brownie, half golden chocolate chip cookie dough.
  3. **BROWNIE:** Ultra-dense, dark chocolate square with the iconic glossy crinkle crust and chocolate drizzle.
* **Interactive Cookie Box (Cart):**
  * One-click **➕ Add 1** and **➖ Remove** steppers with live quantity tracking.
  * Real-time PKR total calculation.
  * Instant **Clear Box** and **Order** actions.
* **1-Click WhatsApp Ordering:**
  * Generates an automated, pre-formatted order message containing item quantities, pricing breakdown, grand total, and delivery details.
  * Direct WhatsApp links for both **0300-8237849** and **0300-8233395**.

### 3. 🤖 Chat with POOKIE (AI Bakery Assistant)
* **Powered by Google Gemini:** Connected to Google Gemini 3.5 Flash using your provided API key.
* **Grounded in Official Brand Knowledge:** Ingests and trains on the entire documentation (`README.md`), understanding:
  * Recipes, flavors, baking secrets, and ingredient philosophy.
  * Exact prices (flat PKR 200 each).
  * Delivery times (30–45 mins warm delivery) and operating hours (11:00 AM – 1:00 AM).
  * Contact hotlines (`0300-8237849` & `0300-8233395`) and WhatsApp ordering assistance.
* **Interactive Chat Experience:**
  * One-click quick question chips (*"What is a Brookie?"*, *"What are your prices?"*, *"What ingredients do you use?"*, etc.).
  * Multi-turn conversational memory.
  * Intelligent offline fallback ensuring POOKIE can always assist even if internet connectivity drops.

### 4. 📞 Contact Us & Inquiries
* **Click-to-Call Buttons:** Direct telephone dials for fast customer inquiries.
* **Operating Hours:** Detailed schedule (11:00 AM – 1:00 AM daily) and delivery info.
* **Interactive Message Form:** Custom customer feedback and inquiry submission with star ratings and celebratory animations (`st.balloons()`).

---

## 📁 Project Structure

```text
COFFEE WEBSITE/
├── .streamlit/
│   └── config.toml          # Custom theme definition (palette, base mode, toolbar)
├── .venv/                   # Virtual environment with installed dependencies
├── assets/
│   └── logo.jpg             # Official Cookie Pookie mascot & brand logo
├── app.py                   # Main Streamlit web application with POOKIE Chatbot
├── README.md                # Grounded knowledge base for POOKIE AI & project docs
├── requirements.txt         # Required Python packages (streamlit, pillow, google-genai)
└── run.bat                  # 1-click Windows launcher
```

---

## ⚡ Quick Start & Running Locally

### Prerequisites
* Windows OS with Python 3.10+ (or the pre-configured `.venv`).

### Method 1: Double-Click Launcher (Easiest)
Simply double-click the **`run.bat`** file in the project folder.

### Method 2: Terminal / PowerShell
```powershell
# Open terminal inside the project directory
cd "C:\Users\intel\Desktop\COFFEE WEBSITE"

# Launch Streamlit with the project environment
.\.venv\Scripts\streamlit.exe run app.py
```

Once running, navigate to:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## 📦 Dependencies

* [`streamlit`](https://streamlit.io/) — Python reactive web application framework.
* [`pillow`](https://python-pillow.org/) — Image processing and asset management.
* [`google-genai`](https://github.com/googleapis/python-genai) — Official Google Gemini API client.

To reinstall or replicate on another machine:
```powershell
pip install -r requirements.txt
```

---

© 2026 **COOKIE POOKIE**. All rights reserved. Freshly Homemade with Love.
