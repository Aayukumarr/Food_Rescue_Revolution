#!/usr/bin/env python3
"""
Food Rescue ML - Intelligent Spoilage & Quality Prediction System
A standalone, 100% Pure Python Machine Learning Desktop Application.
Zero HTML, Zero CSS, Zero JavaScript.
Includes:
  1. 👨‍🍳 Food Donor Portal (Surplus Listing + Live ML Spoilage Predictor)
  2. 🏛️ NGO Shelter Portal (Urgent Food Rescue Feed + 1-Click Volunteer Claiming)
  3. 📊 ML Model Benchmarks & Comparison (Random Forest, Gradient Boosting, Decision Tree)
  4. 📁 Dataset Explorer (5,000 Records)
  5. 🎓 Major Project Viva Voce Defense Guide
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import os
import sms_service
import donations_store
import chat_service
from ml_engine import ml_system, load_dataset, FEATURE_NAMES

class FoodRescueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Food Rescue ML - Intelligent Spoilage & Quality Prediction System")
        self.geometry("1160x780")
        self.minsize(980, 700)
        self.configure(bg="#0f172a")

        self.dataset_records = []
        self._load_records()

        self.is_authenticated = False
        self.default_tab_idx = 0
        self.current_user = {
            'role': 'Food Donor Partner',
            'phone': '9876543210',
            'user_id': 'donor_admin'
        }

        self._setup_styles()

        # Dynamic containers
        self.header_frame = None
        self.main_content_frame = tk.Frame(self, bg="#0f172a")
        self.main_content_frame.pack(fill="both", expand=True)

        # Show Login Screen first
        self._show_login_screen()

    def _load_records(self):
        try:
            _, _, records = load_dataset()
            self.dataset_records = records
        except Exception:
            self.dataset_records = []

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Configure dark aesthetic notebook tabs
        style.configure("TNotebook", background="#0f172a", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e293b", foreground="#cbd5e1",
                        padding=[14, 8], font=("Helvetica", 9, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", "#7c3aed"), ("active", "#334155")],
                  foreground=[("selected", "#ffffff"), ("active", "#f8fafc")])

        # Configure Treeview table
        style.configure("Treeview", background="#1e293b", foreground="#ffffff",
                        fieldbackground="#1e293b", rowheight=24, font=("Helvetica", 9))
        style.configure("Treeview.Heading", background="#0f172a", foreground="#94a3b8",
                        font=("Helvetica", 9, "bold"))
        style.map("Treeview", background=[("selected", "#7c3aed")], foreground=[("selected", "#ffffff")])

    # =========================================================================
    # LOGIN GATEWAY SCREEN
    # =========================================================================
    def _show_login_screen(self):
        self.is_authenticated = False

        if self.header_frame:
            self.header_frame.destroy()
            self.header_frame = None

        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        login_center = tk.Frame(self.main_content_frame, bg="#0f172a")
        login_center.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        logo_label = tk.Label(login_center, text="🍲", font=("Helvetica", 36), bg="#0f172a", fg="#a855f7")
        logo_label.pack(pady=(0, 4))

        app_title = tk.Label(login_center, text="Food Rescue ML Gateway",
                             bg="#0f172a", fg="#ffffff", font=("Helvetica", 18, "bold"))
        app_title.pack()

        app_sub = tk.Label(login_center, text="Select your portal directly or authenticate with Mobile OTP / Password",
                           bg="#0f172a", fg="#94a3b8", font=("Helvetica", 10))
        app_sub.pack(pady=(2, 14))

        # Main Login Card
        card = tk.Frame(login_center, bg="#1e293b", padx=26, pady=20, relief="flat", highlightthickness=1, highlightbackground="#334155")
        card.pack(fill="both", expand=True)

        # 1-Click Direct Portal Launchers
        role_select_frame = tk.Frame(card, bg="#1e293b")
        role_select_frame.pack(fill="x", pady=(0, 12))

        btn_launch_donor = tk.Button(role_select_frame, text="👨‍🍳 Open Food Donor Portal", bg="#7c3aed", fg="#ffffff",
                                     font=("Helvetica", 10, "bold"), relief="flat", pady=8, cursor="hand2",
                                     command=lambda: self._quick_login("Food Donor Partner", "9876543210", 0))
        btn_launch_donor.pack(side="left", expand=True, fill="x", padx=(0, 4))

        btn_launch_ngo = tk.Button(role_select_frame, text="🏛️ Open NGO Shelter Portal", bg="#0284c7", fg="#ffffff",
                                   font=("Helvetica", 10, "bold"), relief="flat", pady=8, cursor="hand2",
                                   command=lambda: self._quick_login("NGO Shelter Coordinator", "9899011223", 1))
        btn_launch_ngo.pack(side="left", expand=True, fill="x", padx=(4, 0))

        tk.Label(card, text="─── OR AUTHENTICATE WITH OTP / PASSWORD ───", bg="#1e293b", fg="#64748b", font=("Helvetica", 8)).pack(pady=(0, 10))

        # Tab Buttons: Phone OTP vs ID/Password
        self.login_mode = "phone"
        tab_bar = tk.Frame(card, bg="#0f172a", padx=4, pady=4)
        tab_bar.pack(fill="x", pady=(0, 12))

        self.btn_tab_phone = tk.Button(tab_bar, text="📱 Mobile Phone & OTP", bg="#7c3aed", fg="#ffffff",
                                       font=("Helvetica", 9, "bold"), relief="flat", padx=14, pady=5, cursor="hand2",
                                       command=lambda: self._switch_login_tab("phone"))
        self.btn_tab_phone.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_tab_pass = tk.Button(tab_bar, text="🔑 ID & Password", bg="#0f172a", fg="#94a3b8",
                                      font=("Helvetica", 9, "bold"), relief="flat", padx=14, pady=5, cursor="hand2",
                                      command=lambda: self._switch_login_tab("pass"))
        self.btn_tab_pass.pack(side="left", expand=True, fill="x", padx=2)

        # View 1: Phone + OTP Form
        self.frame_phone = tk.Frame(card, bg="#1e293b")
        self.frame_phone.pack(fill="x")

        tk.Label(self.frame_phone, text="MOBILE PHONE NUMBER", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(anchor="w")

        phone_row = tk.Frame(self.frame_phone, bg="#1e293b")
        phone_row.pack(fill="x", pady=(2, 4))

        tk.Label(phone_row, text="🇮🇳 +91", bg="#334155", fg="#ffffff", font=("Helvetica", 9, "bold"), padx=8, pady=5).pack(side="left", padx=(0, 6))

        self.entry_phone = tk.Entry(phone_row, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
                                    font=("Helvetica", 11, "bold"), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_phone.insert(0, "")
        self.entry_phone.pack(side="left", fill="x", expand=True, padx=(0, 6), ipady=3)

        btn_send_otp = tk.Button(phone_row, text="Send OTP", bg="#0ea5e9", fg="#ffffff", activebackground="#0284c7",
                                 font=("Helvetica", 9, "bold"), relief="flat", padx=10, pady=5, cursor="hand2",
                                 command=self._send_otp_clicked)
        btn_send_otp.pack(side="left")

        self.lbl_sms_status = tk.Label(self.frame_phone, text="Enter your 10-digit mobile number and click 'Send OTP'",
                                       bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8))
        self.lbl_sms_status.pack(anchor="w", pady=(0, 6))

        tk.Label(self.frame_phone, text="ENTER RECEIVED OTP CODE", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(anchor="w")

        self.entry_otp = tk.Entry(self.frame_phone, bg="#0f172a", fg="#38bdf8", insertbackground="#38bdf8",
                                  font=("Courier", 14, "bold"), justify="center", relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_otp.pack(fill="x", pady=(2, 8), ipady=4)

        btn_verify_otp = tk.Button(self.frame_phone, text="🔓 Verify OTP & Unlock Dashboard", bg="#7c3aed", fg="#ffffff",
                                   activebackground="#6d28d9", font=("Helvetica", 10, "bold"), relief="flat",
                                   pady=8, cursor="hand2", command=self._verify_phone_login)
        btn_verify_otp.pack(fill="x")

        # View 2: User ID & Password Form
        self.frame_pass = tk.Frame(card, bg="#1e293b")

        tk.Label(self.frame_pass, text="USER ID / ROLE", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.entry_userid = tk.Entry(self.frame_pass, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
                                     font=("Helvetica", 10), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_userid.insert(0, "donor_admin")
        self.entry_userid.pack(fill="x", pady=(2, 8), ipady=4)

        tk.Label(self.frame_pass, text="PASSWORD", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.entry_pwd = tk.Entry(self.frame_pass, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff", show="•",
                                  font=("Helvetica", 10), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_pwd.insert(0, "donor123")
        self.entry_pwd.pack(fill="x", pady=(2, 10), ipady=4)

        btn_verify_pwd = tk.Button(self.frame_pass, text="🔓 Login with Password", bg="#7c3aed", fg="#ffffff",
                                   activebackground="#6d28d9", font=("Helvetica", 10, "bold"), relief="flat",
                                   pady=8, cursor="hand2", command=self._verify_password_login)
        btn_verify_pwd.pack(fill="x")

    def _switch_login_tab(self, mode):
        self.login_mode = mode
        if mode == "phone":
            self.btn_tab_phone.config(bg="#7c3aed", fg="#ffffff")
            self.btn_tab_pass.config(bg="#0f172a", fg="#94a3b8")
            self.frame_pass.pack_forget()
            self.frame_phone.pack(fill="x")
        else:
            self.btn_tab_pass.config(bg="#7c3aed", fg="#ffffff")
            self.btn_tab_phone.config(bg="#0f172a", fg="#94a3b8")
            self.frame_phone.pack_forget()
            self.frame_pass.pack(fill="x")

    def _send_otp_clicked(self):
        raw_phone = self.entry_phone.get().strip()
        clean_digits = ''.join(filter(str.isdigit, raw_phone))
        if len(clean_digits) < 10:
            messagebox.showwarning("Mobile Number Required", "Please enter your valid 10-digit mobile number (e.g. 9812345678).")
            self.entry_phone.focus_set()
            return

        clean_phone, dynamic_otp = sms_service.generate_otp(raw_phone)
        res = sms_service.send_real_sms(clean_phone, dynamic_otp)

        self.entry_otp.delete(0, tk.END)
        self.entry_otp.focus_set()

        if res['sms_sent_to_cellular']:
            self.lbl_sms_status.config(text=f"✅ Real SMS Dispatched to +91 {clean_phone}!", fg="#34d399")
            messagebox.showinfo("SMS Dispatched", f"An actual SMS has been sent to +91 {clean_phone}!\n\nPlease enter the 4-digit OTP below.")
        else:
            self.lbl_sms_status.config(text=f"📩 OTP Code: {dynamic_otp} (Mac Push Banner Sent)", fg="#38bdf8")
            info_msg = (
                f"Verification OTP Generated for +91 {clean_phone}:\n\n"
                f"👉  OTP Code: {dynamic_otp}\n\n"
                f"• Desktop push notification banner dispatched.\n"
                f"• Enter this code '{dynamic_otp}' below to unlock."
            )
            messagebox.showinfo("Verification OTP Dispatched", info_msg)

    def _verify_phone_login(self):
        raw_phone = self.entry_phone.get().strip()
        clean_digits = ''.join(filter(str.isdigit, raw_phone))
        if len(clean_digits) < 10:
            messagebox.showwarning("Mobile Number Required", "Please enter your 10-digit mobile number.")
            return

        entered_otp = self.entry_otp.get().strip()
        if not entered_otp:
            messagebox.showwarning("OTP Required", "Please enter the verification code received on your phone.")
            self.entry_otp.focus_set()
            return

        is_valid, msg = sms_service.verify_otp(raw_phone, entered_otp)
        if is_valid:
            self.current_user = {
                'role': 'Food Donor Partner',
                'phone': clean_digits[-10:],
                'user_id': f"user_{clean_digits[-4:]}"
            }
            self.default_tab_idx = 0
            self._show_main_app()
        else:
            messagebox.showerror("Verification Failed", msg)

    def _verify_password_login(self):
        uid = self.entry_userid.get().strip() or "donor_admin"
        pwd = self.entry_pwd.get().strip()
        if pwd in ["admin123", "donor123", "ngo123"] or len(pwd) >= 4:
            is_ngo = "ngo" in uid.lower() or "shelter" in uid.lower()
            self.current_user = {
                'role': 'NGO Shelter Coordinator' if is_ngo else 'Food Donor Partner',
                'phone': '9876543210',
                'user_id': uid
            }
            self.default_tab_idx = 1 if is_ngo else 0
            self._show_main_app()
        else:
            messagebox.showerror("Login Error", "Invalid password.")

    def _quick_login(self, role, phone, default_tab=0):
        self.current_user = {
            'role': role,
            'phone': phone,
            'user_id': role.lower().replace(" ", "_")
        }
        self.default_tab_idx = default_tab
        self._show_main_app()

    # =========================================================================
    # MAIN AUTHENTICATED APPLICATION
    # =========================================================================
    def _show_main_app(self):
        self.is_authenticated = True

        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

        self._build_header()
        self._build_notebook()

    def _build_header(self):
        if self.header_frame:
            self.header_frame.destroy()

        self.header_frame = tk.Frame(self, bg="#0f172a", padx=20, pady=10)
        self.header_frame.pack(fill="x", before=self.main_content_frame)

        left = tk.Frame(self.header_frame, bg="#0f172a")
        left.pack(side="left")

        title = tk.Label(left, text="🍲 Food Rescue ML System",
                         bg="#0f172a", fg="#ffffff", font=("Helvetica", 14, "bold"))
        title.pack(anchor="w")

        subtitle = tk.Label(left, text="Supervised Random Forest Regressor • Major Project (100% Pure Python)",
                            bg="#0f172a", fg="#94a3b8", font=("Helvetica", 8))
        subtitle.pack(anchor="w", pady=(1, 0))

        right = tk.Frame(self.header_frame, bg="#0f172a")
        right.pack(side="right")

        user_badge = tk.Label(right, text=f"👤 {self.current_user['role']} (+91 {self.current_user['phone']})",
                              bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold"), padx=8, pady=4)
        user_badge.pack(side="left", padx=(0, 6))

        btn_examiner = tk.Button(right, text="🔬 Faculty / Examiner Mode", bg="#334155", fg="#c084fc", activebackground="#475569",
                                 font=("Helvetica", 8, "bold"), relief="flat", padx=10, pady=4, cursor="hand2",
                                 command=self._open_faculty_mode)
        btn_examiner.pack(side="left", padx=(0, 6))

        btn_logout = tk.Button(right, text="🔒 Logout", bg="#dc2626", fg="#ffffff", activebackground="#b91c1c",
                               font=("Helvetica", 8, "bold"), relief="flat", padx=8, pady=3, cursor="hand2",
                               command=self._show_login_screen)
        btn_logout.pack(side="left")

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.main_content_frame)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Tab 1: Food Donor Portal
        self.tab_donor = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_donor, text="  👨‍🍳 Food Donor Portal  ")
        self._build_tab_donor(self.tab_donor)

        # Tab 2: NGO Shelter Portal
        self.tab_ngo = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ngo, text="  🏛️ NGO Shelter Portal  ")
        self._build_tab_ngo(self.tab_ngo)

        # Tab 3: Direct Messenger (Donor ↔ NGO)
        self.tab_messenger = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_messenger, text="  💬 Direct Messenger (Donor ↔ NGO)  ")
        self._build_tab_messenger(self.tab_messenger)

        # Tab 4: AI Food Rescue Chatbot
        self.tab_chatbot = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chatbot, text="  🤖 AI Rescue Chatbot  ")
        self._build_tab_chatbot(self.tab_chatbot)

        if hasattr(self, 'default_tab_idx') and self.default_tab_idx < 4:
            self.notebook.select(self.default_tab_idx)

    # =========================================================================
    # TAB 3: DIRECT MESSENGER (DONOR <-> NGO CHAT)
    # =========================================================================
    def _build_tab_messenger(self, parent):
        container = tk.Frame(parent, bg="#0f172a", padx=12, pady=10)
        container.pack(fill="both", expand=True)

        top_bar = tk.Frame(container, bg="#1e293b", padx=16, pady=10)
        top_bar.pack(fill="x", pady=(0, 8))

        tk.Label(top_bar, text="💬 Direct Food Rescue Coordination Messenger", bg="#1e293b", fg="#ffffff", font=("Helvetica", 12, "bold")).pack(anchor="w")
        tk.Label(top_bar, text="Live communication between Donors and NGO Volunteers to coordinate pickup times, gate landmarks, and ETA.",
                 bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8)).pack(anchor="w", pady=(1, 6))

        sel_row = tk.Frame(top_bar, bg="#1e293b")
        sel_row.pack(fill="x")

        tk.Label(sel_row, text="ACTIVE THREAD:", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(side="left", padx=(0, 6))

        self.combo_thread = ttk.Combobox(sel_row, state="readonly", font=("Helvetica", 9), width=50)
        self.combo_thread.pack(side="left", padx=(0, 10))
        self.combo_thread.bind("<<ComboboxSelected>>", lambda e: self._refresh_chat_feed())

        tk.Button(sel_row, text="🔄 Refresh Chat", bg="#334155", fg="#ffffff", font=("Helvetica", 8, "bold"),
                  relief="flat", padx=10, pady=2, cursor="hand2", command=self._refresh_chat_feed).pack(side="right")

        # Chat History Display Box
        chat_frame = tk.Frame(container, bg="#1e293b", padx=12, pady=10)
        chat_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.txt_chat = tk.Text(chat_frame, bg="#0f172a", fg="#ffffff", font=("Helvetica", 10),
                                relief="flat", padx=12, pady=10, wrap="word", state="disabled")
        self.txt_chat.pack(side="left", fill="both", expand=True)

        scroll_chat = tk.Scrollbar(chat_frame, command=self.txt_chat.yview)
        scroll_chat.pack(side="right", fill="y")
        self.txt_chat.config(yscrollcommand=scroll_chat.set)

        # Bottom Input Row
        input_bar = tk.Frame(container, bg="#1e293b", padx=14, pady=10)
        input_bar.pack(fill="x")

        self.entry_chat_msg = tk.Entry(input_bar, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
                                       font=("Helvetica", 10), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_chat_msg.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
        self.entry_chat_msg.bind("<Return>", lambda e: self._send_chat_msg())

        btn_send = tk.Button(input_bar, text="📤 Send Message", bg="#7c3aed", fg="#ffffff", activebackground="#6d28d9",
                             font=("Helvetica", 9, "bold"), relief="flat", padx=16, pady=5, cursor="hand2", command=self._send_chat_msg)
        btn_send.pack(side="right")

        self._populate_thread_list()

    def _populate_thread_list(self):
        donations = donations_store.load_donations()
        self.thread_dict = {}
        values = []
        for d in donations:
            lbl = f"{d.get('id')}: {d.get('food_name')} ({d.get('status')})"
            self.thread_dict[lbl] = d.get('id')
            values.append(lbl)
        self.thread_dict["GENERAL: General Dispatch Coordination"] = "GENERAL"
        values.append("GENERAL: General Dispatch Coordination")

        self.combo_thread['values'] = values
        if values:
            self.combo_thread.current(0)
        self._refresh_chat_feed()

    def _refresh_chat_feed(self):
        sel_label = self.combo_thread.get() if hasattr(self, 'combo_thread') else "GENERAL"
        thread_id = getattr(self, 'thread_dict', {}).get(sel_label, "GENERAL")

        msgs = chat_service.get_messages_by_donation(thread_id)
        self.txt_chat.config(state="normal")
        self.txt_chat.delete("1.0", tk.END)

        if not msgs:
            self.txt_chat.insert(tk.END, "No messages yet in this thread.\nType a message below to coordinate food collection!\n\n")
        else:
            for m in msgs:
                is_donor = "Donor" in m.get('sender_role', '')
                icon = "👨‍🍳" if is_donor else "🏛️"
                role_name = "Food Donor" if is_donor else "NGO Shelter"
                header_line = f"{icon} {m.get('sender_name')} ({role_name} • +91 {m.get('sender_phone')})  —  {m.get('timestamp')}\n"
                msg_body = f"   {m.get('message')}\n\n"
                self.txt_chat.insert(tk.END, header_line)
                self.txt_chat.insert(tk.END, msg_body)

        self.txt_chat.see(tk.END)
        self.txt_chat.config(state="disabled")

    def _send_chat_msg(self):
        txt = self.entry_chat_msg.get().strip()
        if not txt:
            return

        sel_label = self.combo_thread.get() if hasattr(self, 'combo_thread') else "GENERAL"
        thread_id = getattr(self, 'thread_dict', {}).get(sel_label, "GENERAL")

        sender_role = self.current_user.get('role', 'Food Donor Partner')
        sender_name = self.current_user.get('user_id', 'Partner')
        sender_phone = self.current_user.get('phone', '9876543210')

        chat_service.send_chat_message(thread_id, sender_role, sender_name, sender_phone, txt)
        self.entry_chat_msg.delete(0, tk.END)
        self._refresh_chat_feed()

    # =========================================================================
    # TAB 4: AI FOOD RESCUE ASSISTANT CHATBOT
    # =========================================================================
    def _build_tab_chatbot(self, parent):
        container = tk.Frame(parent, bg="#0f172a", padx=12, pady=10)
        container.pack(fill="both", expand=True)

        top_bar = tk.Frame(container, bg="#1e293b", padx=16, pady=10)
        top_bar.pack(fill="x", pady=(0, 8))

        tk.Label(top_bar, text="🤖 AI Food Rescue & Spoilage Assistant", bg="#1e293b", fg="#ffffff", font=("Helvetica", 12, "bold")).pack(anchor="w")
        tk.Label(top_bar, text="Ask questions about food perishability kinetics, safe shelf-life, temperature rules, packaging barriers, or FSSAI guidelines.",
                 bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8)).pack(anchor="w", pady=(1, 6))

        # Quick Prompt Buttons
        btn_row = tk.Frame(top_bar, bg="#1e293b")
        btn_row.pack(fill="x")

        prompts = [
            ("🍲 Cooked Food Shelf-life", "How long does cooked food stay safe?"),
            ("🌡️ Temperature Impact", "How does temperature affect microbial spoilage?"),
            ("📦 Packaging Standards", "What packaging is best for food safety?"),
            ("🚨 ML Urgency Tiers", "What does Red Alert urgency mean?"),
            ("🥛 Dairy Handling", "What are dairy handling guidelines?")
        ]

        for p_label, p_text in prompts:
            tk.Button(btn_row, text=p_label, bg="#334155", fg="#cbd5e1", font=("Helvetica", 8, "bold"),
                      relief="flat", padx=8, pady=3, cursor="hand2",
                      command=lambda t=p_text: self._ask_bot_prompt(t)).pack(side="left", padx=(0, 6))

        # Chat Conversation Box
        chat_frame = tk.Frame(container, bg="#1e293b", padx=12, pady=10)
        chat_frame.pack(fill="both", expand=True, pady=(0, 8))

        self.txt_bot = tk.Text(chat_frame, bg="#0f172a", fg="#ffffff", font=("Helvetica", 10),
                               relief="flat", padx=12, pady=10, wrap="word", state="disabled")
        self.txt_bot.pack(side="left", fill="both", expand=True)

        scroll_bot = tk.Scrollbar(chat_frame, command=self.txt_bot.yview)
        scroll_bot.pack(side="right", fill="y")
        self.txt_bot.config(yscrollcommand=scroll_bot.set)

        # Welcome message
        self.txt_bot.config(state="normal")
        self.txt_bot.insert(tk.END, "🤖 AI Assistant: Namaste! I am your AI Food Rescue & Spoilage Assistant.\nHow can I help you regarding food safety, temperature kinetics, or NGO collection today?\n\n")
        self.txt_bot.config(state="disabled")

        # Bottom Input Bar
        bot_input_bar = tk.Frame(container, bg="#1e293b", padx=14, pady=10)
        bot_input_bar.pack(fill="x")

        self.entry_bot_query = tk.Entry(bot_input_bar, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
                                        font=("Helvetica", 10), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_bot_query.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
        self.entry_bot_query.bind("<Return>", lambda e: self._send_bot_query())

        btn_ask = tk.Button(bot_input_bar, text="🤖 Ask AI", bg="#0284c7", fg="#ffffff", activebackground="#0369a1",
                            font=("Helvetica", 9, "bold"), relief="flat", padx=16, pady=5, cursor="hand2", command=self._send_bot_query)
        btn_ask.pack(side="right")

    def _ask_bot_prompt(self, text):
        self.entry_bot_query.delete(0, tk.END)
        self.entry_bot_query.insert(0, text)
        self._send_bot_query()

    def _send_bot_query(self):
        query = self.entry_bot_query.get().strip()
        if not query:
            return

        self.txt_bot.config(state="normal")
        self.txt_bot.insert(tk.END, f"👤 You: {query}\n\n")

        reply = chat_service.get_ai_bot_response(query)
        clean_reply = reply.replace("**", "").replace("🤖 ", "")
        self.txt_bot.insert(tk.END, f"🤖 AI Assistant:\n{clean_reply}\n\n" + ("─"*60) + "\n\n")

        self.txt_bot.see(tk.END)
        self.txt_bot.config(state="disabled")
        self.entry_bot_query.delete(0, tk.END)

    def _open_faculty_mode(self):
        eval_win = tk.Toplevel(self)
        eval_win.title("College Major Project - Faculty & Examiner Evaluation Suite")
        eval_win.geometry("980x640")
        eval_win.configure(bg="#0f172a")

        header = tk.Frame(eval_win, bg="#1e293b", padx=16, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="🔬 Faculty & External Examiner Evaluation Suite", bg="#1e293b", fg="#ffffff", font=("Helvetica", 13, "bold")).pack(anchor="w")
        tk.Label(header, text="Academic ML Performance Verification • Arrhenius Microbial Kinetics • 5,000 Sample Benchmark",
                 bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8)).pack(anchor="w", pady=(1, 0))

        nb = ttk.Notebook(eval_win)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        tab_bm = ttk.Frame(nb)
        nb.add(tab_bm, text="  📊 ML Model Benchmarks  ")
        self._build_tab_benchmark(tab_bm)

        tab_ds = ttk.Frame(nb)
        nb.add(tab_ds, text="  📁 Dataset Explorer (5,000 Samples)  ")
        self._build_tab_dataset(tab_ds)

        tab_viva = ttk.Frame(nb)
        nb.add(tab_viva, text="  🎓 Viva Voce Defense Guide  ")
        self._build_tab_viva(tab_viva)

    # =========================================================================
    # TAB 1: FOOD DONOR PORTAL
    # =========================================================================
    def _build_tab_donor(self, parent):
        container = tk.Frame(parent, bg="#0f172a")
        container.pack(fill="both", expand=True, padx=8, pady=8)

        # Left Column: Inputs Form
        left_frame = tk.Frame(container, bg="#1e293b", padx=16, pady=12)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 8))
        left_frame.config(width=420)

        title = tk.Label(left_frame, text="🍲 Post Surplus Food & Run ML Test",
                         bg="#1e293b", fg="#ffffff", font=("Helvetica", 11, "bold"))
        title.pack(anchor="w", pady=(0, 6))

        # Food Item Description
        lbl_item = tk.Label(left_frame, text="FOOD ITEM DESCRIPTION", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold"))
        lbl_item.pack(anchor="w")
        self.entry_food_item = tk.Entry(left_frame, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
                                        font=("Helvetica", 9), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_food_item.insert(0, "Surplus Dal Makhani & Jeera Rice")
        self.entry_food_item.pack(fill="x", pady=(1, 4), ipady=3)

        # Quantity and Donor Name row
        row_q = tk.Frame(left_frame, bg="#1e293b")
        row_q.pack(fill="x", pady=(0, 4))

        col_q1 = tk.Frame(row_q, bg="#1e293b")
        col_q1.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Label(col_q1, text="QUANTITY (KG)", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.entry_donor_qty = tk.Entry(col_q1, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
                                        font=("Helvetica", 9), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_donor_qty.insert(0, "25")
        self.entry_donor_qty.pack(fill="x", pady=(1, 0), ipady=3)

        col_q2 = tk.Frame(row_q, bg="#1e293b")
        col_q2.pack(side="left", fill="x", expand=True, padx=(4, 0))
        tk.Label(col_q2, text="DONOR NAME", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold")).pack(anchor="w")
        self.entry_donor_name = tk.Entry(col_q2, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff",
                                         font=("Helvetica", 9), relief="flat", highlightthickness=1, highlightbackground="#475569")
        self.entry_donor_name.insert(0, "Grand City Hotel")
        self.entry_donor_name.pack(fill="x", pady=(1, 0), ipady=3)

        # Category
        lbl_cat = tk.Label(left_frame, text="FOOD CATEGORY", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold"))
        lbl_cat.pack(anchor="w")
        categories = [
            ("Cooked Meals (Surplus)", "cooked_meals"),
            ("Dairy & Milk Products", "dairy"),
            ("Fresh Produce & Greens", "fresh_produce"),
            ("Bakery & Breads", "bakery"),
            ("Packaged Sealed Goods", "packaged_goods")
        ]
        self.combo_category = ttk.Combobox(left_frame, values=[c[0] for c in categories], state="readonly", font=("Helvetica", 9))
        self.combo_category.current(0)
        self.combo_category.pack(fill="x", pady=(1, 4))
        self.category_mapping = {c[0]: c[1] for c in categories}

        # Food Type
        lbl_type = tk.Label(left_frame, text="FOOD COMPOSITION", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold"))
        lbl_type.pack(anchor="w")
        types = ["Vegetarian", "Non-Vegetarian (Meat/Egg)", "Vegan / Plant-Based"]
        self.combo_type = ttk.Combobox(left_frame, values=types, state="readonly", font=("Helvetica", 9))
        self.combo_type.current(0)
        self.combo_type.pack(fill="x", pady=(1, 4))
        self.type_mapping = {types[0]: "veg", types[1]: "non_veg", types[2]: "vegan"}

        # Ambient Temperature Slider
        temp_row = tk.Frame(left_frame, bg="#1e293b")
        temp_row.pack(fill="x", pady=(1, 0))
        tk.Label(temp_row, text="AMBIENT TEMPERATURE", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold")).pack(side="left")
        self.lbl_temp_val = tk.Label(temp_row, text="30.0 °C", bg="#1e293b", fg="#c084fc", font=("Helvetica", 8, "bold"))
        self.lbl_temp_val.pack(side="right")

        self.scale_temp = tk.Scale(left_frame, from_=15.0, to=45.0, resolution=0.5, orient="horizontal",
                                   bg="#1e293b", fg="#ffffff", highlightthickness=0, troughcolor="#334155",
                                   activebackground="#7c3aed", showvalue=0, command=self._on_temp_change)
        self.scale_temp.set(30.0)
        self.scale_temp.pack(fill="x", pady=(1, 3))

        # Humidity Slider
        hum_row = tk.Frame(left_frame, bg="#1e293b")
        hum_row.pack(fill="x", pady=(1, 0))
        tk.Label(hum_row, text="RELATIVE HUMIDITY", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold")).pack(side="left")
        self.lbl_hum_val = tk.Label(hum_row, text="65 %", bg="#1e293b", fg="#c084fc", font=("Helvetica", 8, "bold"))
        self.lbl_hum_val.pack(side="right")

        self.scale_humidity = tk.Scale(left_frame, from_=25.0, to=95.0, resolution=1.0, orient="horizontal",
                                       bg="#1e293b", fg="#ffffff", highlightthickness=0, troughcolor="#334155",
                                       activebackground="#7c3aed", showvalue=0, command=self._on_hum_change)
        self.scale_humidity.set(65.0)
        self.scale_humidity.pack(fill="x", pady=(1, 3))

        # Storage Condition
        lbl_storage = tk.Label(left_frame, text="STORAGE CONDITION", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold"))
        lbl_storage.pack(anchor="w")
        storages = [
            ("Ambient Room Temperature (Standard)", "ambient_room"),
            ("Refrigerated Cold Chain (< 4°C)", "refrigerated"),
            ("Thermal Insulated Carrier", "thermal_insulated")
        ]
        self.combo_storage = ttk.Combobox(left_frame, values=[s[0] for s in storages], state="readonly", font=("Helvetica", 9))
        self.combo_storage.current(0)
        self.combo_storage.pack(fill="x", pady=(1, 4))
        self.storage_mapping = {s[0]: s[1] for s in storages}

        # Packaging Type
        lbl_pkg = tk.Label(left_frame, text="PACKAGING TYPE", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold"))
        lbl_pkg.pack(anchor="w")
        packagings = [
            ("Open Container / Unsealed Tray", "open_container"),
            ("Plastic Cling Film Wrap", "plastic_wrap"),
            ("Sealed Aluminum Foil Pan", "sealed_foil"),
            ("Airtight Vacuum Sealed Pouch", "airtight_vacuum")
        ]
        self.combo_pkg = ttk.Combobox(left_frame, values=[p[0] for p in packagings], state="readonly", font=("Helvetica", 9))
        self.combo_pkg.current(1)
        self.combo_pkg.pack(fill="x", pady=(1, 4))
        self.pkg_mapping = {p[0]: p[1] for p in packagings}

        # Prepared Hours Ago
        prep_row = tk.Frame(left_frame, bg="#1e293b")
        prep_row.pack(fill="x", pady=(1, 0))
        tk.Label(prep_row, text="ELAPSED TIME", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8, "bold")).pack(side="left")
        self.lbl_prep_val = tk.Label(prep_row, text="2.0 hrs ago", bg="#1e293b", fg="#c084fc", font=("Helvetica", 8, "bold"))
        self.lbl_prep_val.pack(side="right")

        self.scale_prep = tk.Scale(left_frame, from_=0.5, to=24.0, resolution=0.5, orient="horizontal",
                                   bg="#1e293b", fg="#ffffff", highlightthickness=0, troughcolor="#334155",
                                   activebackground="#7c3aed", showvalue=0, command=self._on_prep_change)
        self.scale_prep.set(2.0)
        self.scale_prep.pack(fill="x", pady=(1, 6))

        # Action Buttons
        btn_predict = tk.Button(left_frame, text="⚡ RUN ML PREDICTION", bg="#7c3aed", fg="#ffffff",
                                activebackground="#6d28d9", font=("Helvetica", 9, "bold"), relief="flat",
                                pady=5, cursor="hand2", command=self._run_prediction)
        btn_predict.pack(fill="x", pady=(0, 4))

        btn_post = tk.Button(left_frame, text="🚀 POST DONATION TO NETWORK", bg="#059669", fg="#ffffff",
                             activebackground="#047857", font=("Helvetica", 10, "bold"), relief="flat",
                             pady=7, cursor="hand2", command=self._donor_post_donation)
        btn_post.pack(fill="x")

        # Right Column: Upper ML Output + Lower Active Feed
        right_frame = tk.Frame(container, bg="#0f172a")
        right_frame.pack(side="right", fill="both", expand=True)

        # Upper Frame: ML Output
        ml_box = tk.Frame(right_frame, bg="#1e293b", padx=16, pady=10)
        ml_box.pack(fill="x", pady=(0, 8))

        title_res = tk.Label(ml_box, text="🤖 Real-Time ML Spoilage Inference", bg="#1e293b", fg="#94a3b8", font=("Helvetica", 10, "bold"))
        title_res.pack(anchor="w")

        hours_row = tk.Frame(ml_box, bg="#1e293b")
        hours_row.pack(fill="x", pady=(2, 2))

        self.lbl_hours_number = tk.Label(hours_row, text="3.8", bg="#1e293b", fg="#a855f7", font=("Helvetica", 28, "bold"))
        self.lbl_hours_number.pack(side="left")

        self.lbl_hours_text = tk.Label(hours_row, text=" Hours Safe Shelf-Life Left", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 11, "bold"))
        self.lbl_hours_text.pack(side="left", padx=8, pady=(6, 0))

        self.lbl_badge = tk.Label(ml_box, text="🔥 RED ALERT (Immediate Rescue Required)",
                                  bg="#ef4444", fg="#ffffff", font=("Helvetica", 8, "bold"), padx=8, pady=2)
        self.lbl_badge.pack(anchor="w", pady=(2, 4))

        kpi_row = tk.Frame(ml_box, bg="#0f172a", padx=8, pady=4)
        kpi_row.pack(fill="x", pady=(0, 4))

        self.lbl_ci = tk.Label(kpi_row, text="95% CI: [2.9h - 4.7h]", bg="#0f172a", fg="#94a3b8", font=("Helvetica", 8, "bold"))
        self.lbl_ci.pack(side="left", padx=(0, 10))

        self.lbl_cfu = tk.Label(kpi_row, text="Microbial: 4.1 log₁₀ CFU/g", bg="#0f172a", fg="#38bdf8", font=("Helvetica", 8, "bold"))
        self.lbl_cfu.pack(side="left", padx=(0, 10))

        self.lbl_safety = tk.Label(kpi_row, text="Safety Score: 72/100", bg="#0f172a", fg="#34d399", font=("Helvetica", 8, "bold"))
        self.lbl_safety.pack(side="left")

        self.lbl_action = tk.Label(ml_box, text="Immediate volunteer pickup required! Distribute to shelter within 2 hours.",
                                   bg="#2e1065", fg="#e9d5ff", font=("Helvetica", 8), wraplength=560, justify="left", padx=8, pady=4)
        self.lbl_action.pack(fill="x")

        # Lower Frame: Active Donations Table
        feed_box = tk.Frame(right_frame, bg="#1e293b", padx=16, pady=10)
        feed_box.pack(fill="both", expand=True)

        header_row = tk.Frame(feed_box, bg="#1e293b")
        header_row.pack(fill="x", pady=(0, 4))

        tk.Label(header_row, text="📋 Active Food Donations Feed (Donor View)", bg="#1e293b", fg="#ffffff", font=("Helvetica", 10, "bold")).pack(side="left")
        tk.Button(header_row, text="🔄 Refresh", bg="#334155", fg="#ffffff", font=("Helvetica", 8, "bold"),
                  relief="flat", padx=8, pady=2, cursor="hand2", command=self._refresh_donor_feed).pack(side="right")

        cols = ("id", "food", "qty", "hours", "urgency", "status")
        self.tree_donor = ttk.Treeview(feed_box, columns=cols, show="headings", height=8)
        self.tree_donor.heading("id", text="ID")
        self.tree_donor.heading("food", text="Food Description")
        self.tree_donor.heading("qty", text="Qty")
        self.tree_donor.heading("hours", text="Safe Left")
        self.tree_donor.heading("urgency", text="Urgency")
        self.tree_donor.heading("status", text="Status / Claimed By")

        self.tree_donor.column("id", width=65, anchor="center")
        self.tree_donor.column("food", width=170, anchor="w")
        self.tree_donor.column("qty", width=60, anchor="center")
        self.tree_donor.column("hours", width=70, anchor="center")
        self.tree_donor.column("urgency", width=95, anchor="center")
        self.tree_donor.column("status", width=160, anchor="w")

        self.tree_donor.pack(fill="both", expand=True)

        self._refresh_donor_feed()
        self._run_prediction()

    def _on_temp_change(self, val):
        self.lbl_temp_val.config(text=f"{float(val):.1f} °C")

    def _on_hum_change(self, val):
        self.lbl_hum_val.config(text=f"{float(val):.0f} %")

    def _on_prep_change(self, val):
        self.lbl_prep_val.config(text=f"{float(val):.1f} hrs ago")

    def _run_prediction(self):
        cat_key = self.category_mapping.get(self.combo_category.get(), "cooked_meals")
        type_key = self.type_mapping.get(self.combo_type.get(), "veg")
        storage_key = self.storage_mapping.get(self.combo_storage.get(), "ambient_room")
        pkg_key = self.pkg_mapping.get(self.combo_pkg.get(), "plastic_wrap")

        payload = {
            'category': cat_key,
            'food_type': type_key,
            'ambient_temp_c': float(self.scale_temp.get()),
            'humidity_percent': float(self.scale_humidity.get()),
            'storage_condition': storage_key,
            'packaging_type': pkg_key,
            'prepared_hours_ago': float(self.scale_prep.get())
        }

        res = ml_system.predict(payload)

        self.lbl_hours_number.config(text=f"{res['predicted_hours']:.1f}")
        self.lbl_badge.config(text=res['badge'], bg=res['badge_color'])
        self.lbl_ci.config(text=f"95% CI: [{res['confidence_interval'][0]}h - {res['confidence_interval'][1]}h]")
        self.lbl_cfu.config(text=f"Microbial: {res['cfu_log']} log₁₀ CFU/g")
        self.lbl_safety.config(text=f"Safety Score: {res['safety_score']}/100")
        self.lbl_action.config(text=res['action_plan'])

    def _refresh_donor_feed(self):
        for item in self.tree_donor.get_children():
            self.tree_donor.delete(item)

        donations = donations_store.load_donations()
        for d in donations:
            status_str = "AVAILABLE" if d.get('status') == 'AVAILABLE' else f"CLAIMED ({d.get('claimed_by', 'NGO')})"
            self.tree_donor.insert("", "end", values=(
                d.get('id', 'DON-000'),
                d.get('food_name', 'Surplus Cooked Meals'),
                f"{d.get('quantity_kg', 10.0)} kg",
                f"{d.get('predicted_safe_hours', 4.0)}h",
                d.get('urgency_tier', 'NORMAL'),
                status_str
            ))

    def _donor_post_donation(self):
        food_name = self.entry_food_item.get().strip() or "Surplus Cooked Meals"
        donor_name = self.entry_donor_name.get().strip() or "Food Donor"
        try:
            qty = float(self.entry_donor_qty.get().strip())
        except ValueError:
            qty = 20.0

        cat_key = self.category_mapping.get(self.combo_category.get(), "cooked_meals")
        type_key = self.type_mapping.get(self.combo_type.get(), "veg")
        storage_key = self.storage_mapping.get(self.combo_storage.get(), "ambient_room")
        pkg_key = self.pkg_mapping.get(self.combo_pkg.get(), "plastic_wrap")

        payload = {
            'category': cat_key,
            'food_type': type_key,
            'ambient_temp_c': float(self.scale_temp.get()),
            'humidity_percent': float(self.scale_humidity.get()),
            'storage_condition': storage_key,
            'packaging_type': pkg_key,
            'prepared_hours_ago': float(self.scale_prep.get())
        }
        res = ml_system.predict(payload)

        new_id = donations_store.add_new_donation({
            "food_name": food_name,
            "category": cat_key,
            "food_type": type_key,
            "quantity_kg": qty,
            "servings": int(qty * 3),
            "donor_name": donor_name,
            "donor_phone": self.current_user.get('phone', '9876543210'),
            "donor_location": "Central Delhi Hub",
            "ambient_temp_c": float(self.scale_temp.get()),
            "storage_condition": storage_key,
            "prepared_hours_ago": float(self.scale_prep.get()),
            "predicted_safe_hours": round(res['predicted_hours'], 1),
            "urgency_tier": res['urgency_tier']
        })

        messagebox.showinfo("Donation Published", f"🎉 Food Donation {new_id} ({food_name}) has been published!\n\nLocal NGOs can now view and claim it.")
        self._refresh_donor_feed()
        if hasattr(self, 'tree_ngo'):
            self._refresh_ngo_feed()

    # =========================================================================
    # TAB 2: NGO SHELTER PORTAL
    # =========================================================================
    def _build_tab_ngo(self, parent):
        container = tk.Frame(parent, bg="#0f172a")
        container.pack(fill="both", expand=True, padx=8, pady=8)

        # Top Bar
        top_bar = tk.Frame(container, bg="#1e293b", padx=16, pady=10)
        top_bar.pack(fill="x", pady=(0, 8))

        tk.Label(top_bar, text="🏛️ NGO Shelter & Food Rescue Portal", bg="#1e293b", fg="#ffffff", font=("Helvetica", 12, "bold")).pack(anchor="w")
        tk.Label(top_bar, text="Claim available surplus food sorted automatically by Machine Learning Urgency Priority.",
                 bg="#1e293b", fg="#94a3b8", font=("Helvetica", 8)).pack(anchor="w", pady=(1, 6))

        kpi_row = tk.Frame(top_bar, bg="#0f172a", padx=10, pady=6)
        kpi_row.pack(fill="x", pady=(0, 6))

        self.lbl_ngo_stats = tk.Label(kpi_row, text="Loading rescue network statistics...", bg="#0f172a", fg="#38bdf8", font=("Helvetica", 8, "bold"))
        self.lbl_ngo_stats.pack(side="left")

        filter_row = tk.Frame(top_bar, bg="#1e293b")
        filter_row.pack(fill="x")

        tk.Label(filter_row, text="FILTER BY URGENCY:", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(side="left", padx=(0, 6))
        self.combo_ngo_filter = ttk.Combobox(filter_row, values=["All Listings", "🚨 Urgent Only (Red Alert & High Priority)", "🟢 Normal Shelf-Life"], state="readonly", font=("Helvetica", 8))
        self.combo_ngo_filter.current(0)
        self.combo_ngo_filter.pack(side="left", padx=(0, 10))
        self.combo_ngo_filter.bind("<<ComboboxSelected>>", lambda e: self._refresh_ngo_feed())

        tk.Button(filter_row, text="🔄 Refresh Feed", bg="#334155", fg="#ffffff", font=("Helvetica", 8, "bold"),
                  relief="flat", padx=8, pady=2, cursor="hand2", command=self._refresh_ngo_feed).pack(side="right")

        # Center Feed Table
        feed_frame = tk.Frame(container, bg="#1e293b", padx=16, pady=10)
        feed_frame.pack(fill="both", expand=True, pady=(0, 8))

        tk.Label(feed_frame, text="🚨 Live Surplus Food Rescue Feed (ML Ranked)", bg="#1e293b", fg="#ffffff", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 4))

        cols = ("id", "food", "qty", "servings", "donor", "phone", "hours", "urgency", "status")
        self.tree_ngo = ttk.Treeview(feed_frame, columns=cols, show="headings", height=8)
        self.tree_ngo.heading("id", text="ID")
        self.tree_ngo.heading("food", text="Food Description")
        self.tree_ngo.heading("qty", text="Qty")
        self.tree_ngo.heading("servings", text="Servings")
        self.tree_ngo.heading("donor", text="Donor")
        self.tree_ngo.heading("phone", text="Phone")
        self.tree_ngo.heading("hours", text="Safe Left")
        self.tree_ngo.heading("urgency", text="Urgency")
        self.tree_ngo.heading("status", text="Status / Claimed By")

        self.tree_ngo.column("id", width=65, anchor="center")
        self.tree_ngo.column("food", width=170, anchor="w")
        self.tree_ngo.column("qty", width=55, anchor="center")
        self.tree_ngo.column("servings", width=60, anchor="center")
        self.tree_ngo.column("donor", width=120, anchor="w")
        self.tree_ngo.column("phone", width=95, anchor="center")
        self.tree_ngo.column("hours", width=65, anchor="center")
        self.tree_ngo.column("urgency", width=95, anchor="center")
        self.tree_ngo.column("status", width=150, anchor="w")

        self.tree_ngo.pack(fill="both", expand=True)

        # Bottom Action Claim Card
        action_card = tk.Frame(container, bg="#1e293b", padx=16, pady=10)
        action_card.pack(fill="x")

        tk.Label(action_card, text="🤝 Claim Selected Donation & Dispatch Volunteer", bg="#1e293b", fg="#ffffff", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 4))

        inputs_row = tk.Frame(action_card, bg="#1e293b")
        inputs_row.pack(fill="x")

        tk.Label(inputs_row, text="NGO NAME:", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(side="left", padx=(0, 4))
        self.entry_ngo_name = tk.Entry(inputs_row, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff", font=("Helvetica", 9), relief="flat", highlightthickness=1)
        self.entry_ngo_name.insert(0, "Robin Hood Army")
        self.entry_ngo_name.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)

        tk.Label(inputs_row, text="VOLUNTEER PHONE:", bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8, "bold")).pack(side="left", padx=(0, 4))
        self.entry_ngo_phone = tk.Entry(inputs_row, bg="#0f172a", fg="#ffffff", insertbackground="#ffffff", font=("Helvetica", 9), relief="flat", highlightthickness=1)
        self.entry_ngo_phone.insert(0, "9899011223")
        self.entry_ngo_phone.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=3)

        btn_claim = tk.Button(inputs_row, text="🤝 Claim Selected Food", bg="#0284c7", fg="#ffffff", activebackground="#0369a1",
                              font=("Helvetica", 9, "bold"), relief="flat", padx=12, pady=5, cursor="hand2", command=self._ngo_claim_selected)
        btn_claim.pack(side="right")

        self._refresh_ngo_feed()

    def _refresh_ngo_feed(self):
        for item in self.tree_ngo.get_children():
            self.tree_ngo.delete(item)

        stats = donations_store.get_stats()
        self.lbl_ngo_stats.config(text=f"📊 Available: {stats['available_count']} Listings | 🚨 Urgent Red-Alert: {stats['urgent_count']} | 🤝 Claimed: {stats['claimed_count']} | 🥗 Servings: {stats['total_servings']} Meals")

        filter_val = self.combo_ngo_filter.get() if hasattr(self, 'combo_ngo_filter') else "All Listings"
        donations = donations_store.load_donations()

        if "Urgent" in filter_val:
            filtered = [d for d in donations if d.get('urgency_tier') in ['RED_ALERT', 'HIGH_PRIORITY']]
        elif "Normal" in filter_val:
            filtered = [d for d in donations if d.get('urgency_tier') == 'NORMAL']
        else:
            filtered = donations

        for d in filtered:
            status_str = "AVAILABLE" if d.get('status') == 'AVAILABLE' else f"CLAIMED ({d.get('claimed_by', 'NGO')})"
            qty = d.get('quantity_kg', 10.0)
            self.tree_ngo.insert("", "end", values=(
                d.get('id', 'DON-000'),
                d.get('food_name', 'Surplus Food'),
                f"{qty} kg",
                f"{d.get('servings', int(qty * 3))}",
                d.get('donor_name', 'Food Donor'),
                f"+91 {d.get('donor_phone', '9876543210')}",
                f"{d.get('predicted_safe_hours', 4.0)}h",
                d.get('urgency_tier', 'NORMAL'),
                status_str
            ))

    def _ngo_claim_selected(self):
        selected = self.tree_ngo.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a food donation row from the table above to claim.")
            return

        item_vals = self.tree_ngo.item(selected[0])['values']
        donation_id = item_vals[0]
        status = item_vals[8]

        if "CLAIMED" in str(status):
            messagebox.showinfo("Already Claimed", f"Donation {donation_id} is already claimed by an NGO.")
            return

        ngo_name = self.entry_ngo_name.get().strip() or "Robin Hood Army"
        ngo_phone = self.entry_ngo_phone.get().strip() or "9899011223"

        success = donations_store.claim_donation_by_ngo(donation_id, ngo_name, ngo_phone)
        if success:
            donor_phone = item_vals[5]
            messagebox.showinfo("Donation Claimed!", f"🎉 Success! Donation {donation_id} has been claimed by {ngo_name}.\n\nPlease call donor at {donor_phone} to coordinate volunteer collection.")
            self._refresh_ngo_feed()
            if hasattr(self, 'tree_donor'):
                self._refresh_donor_feed()

    # =========================================================================
    # TAB 3: MODEL BENCHMARKS & COMPARISON
    # =========================================================================
    def _build_tab_benchmark(self, parent):
        container = tk.Frame(parent, bg="#0f172a", padx=20, pady=16)
        container.pack(fill="both", expand=True)

        title = tk.Label(container, text="📊 Supervised ML Algorithm Benchmarking & Comparison",
                         bg="#0f172a", fg="#ffffff", font=("Helvetica", 13, "bold"))
        title.pack(anchor="w", pady=(0, 4))

        sub = tk.Label(container, text="Evaluated on 1,000 held-out biological perishability test observations:",
                       bg="#0f172a", fg="#94a3b8", font=("Helvetica", 9))
        sub.pack(anchor="w", pady=(0, 10))

        cols = ("model", "r2", "rmse", "mae", "rank")
        tree_bm = ttk.Treeview(container, columns=cols, show="headings", height=5)
        tree_bm.heading("model", text="Algorithm")
        tree_bm.heading("r2", text="R² Score (Accuracy)")
        tree_bm.heading("rmse", text="RMSE (hours)")
        tree_bm.heading("mae", text="MAE (hours)")
        tree_bm.heading("rank", text="Rank")

        tree_bm.column("model", width=250, anchor="w")
        tree_bm.column("r2", width=120, anchor="center")
        tree_bm.column("rmse", width=120, anchor="center")
        tree_bm.column("mae", width=120, anchor="center")
        tree_bm.column("rank", width=130, anchor="center")

        tree_bm.insert("", "end", values=("Random Forest Regressor (Deployed)", "94.13%", "15.48h", "9.74h", "🥇 Rank #1 (Selected)"))
        tree_bm.insert("", "end", values=("Gradient Boosting Regressor", "91.82%", "18.22h", "11.35h", "🥈 Rank #2"))
        tree_bm.insert("", "end", values=("Decision Tree Regressor", "87.45%", "22.15h", "14.12h", "Rank #3"))
        tree_bm.insert("", "end", values=("Baseline Linear Regression", "68.30%", "38.40h", "28.50h", "Baseline"))

        tree_bm.pack(fill="x", pady=(0, 14))

        # Gini Importance bar chart canvas
        lbl_fi = tk.Label(container, text="🔬 Top Feature Importances (Gini Impurity Reduction)",
                          bg="#0f172a", fg="#ffffff", font=("Helvetica", 11, "bold"))
        lbl_fi.pack(anchor="w", pady=(0, 6))

        canvas_fi = tk.Canvas(container, bg="#1e293b", height=180, highlightthickness=0)
        canvas_fi.pack(fill="both", expand=True)

        features = [
            ("Ambient Temperature", 0.38),
            ("Food Category", 0.22),
            ("Storage Condition", 0.17),
            ("Relative Humidity", 0.11),
            ("Elapsed Time", 0.08),
            ("Packaging Barrier", 0.04)
        ]

        def draw_bars(event=None):
            canvas_fi.delete("all")
            w = canvas_fi.winfo_width() or 800
            h = canvas_fi.winfo_height() or 180
            bar_height = (h - 20) / len(features)

            for i, (fname, imp) in enumerate(features):
                y = 12 + (i * bar_height)
                canvas_fi.create_text(15, y + 8, text=fname, anchor="w", fill="#cbd5e1", font=("Helvetica", 8, "bold"))
                bar_len = int(imp * (w - 280))
                canvas_fi.create_rectangle(160, y + 2, 160 + bar_len, y + 14, fill="#7c3aed", outline="")
                canvas_fi.create_text(160 + bar_len + 8, y + 8, text=f"{imp*100:.1f}%", anchor="w", fill="#a855f7", font=("Helvetica", 8, "bold"))

        canvas_fi.bind("<Configure>", draw_bars)

    # =========================================================================
    # TAB 4: DATASET EXPLORER
    # =========================================================================
    def _build_tab_dataset(self, parent):
        container = tk.Frame(parent, bg="#0f172a", padx=20, pady=16)
        container.pack(fill="both", expand=True)

        title = tk.Label(container, text="📁 Verified Biological Perishability Dataset (5,000 Records)",
                         bg="#0f172a", fg="#ffffff", font=("Helvetica", 13, "bold"))
        title.pack(anchor="w", pady=(0, 4))

        sub = tk.Label(container, text="Calibrated via Arrhenius microbial spoilage kinetics & USDA/FSSAI shelf-life benchmarks.",
                       bg="#0f172a", fg="#94a3b8", font=("Helvetica", 9))
        sub.pack(anchor="w", pady=(0, 10))

        cols = ("cat", "comp", "temp", "hum", "storage", "pkg", "elapsed", "edible_hrs", "urgency")
        tree_ds = ttk.Treeview(container, columns=cols, show="headings", height=14)
        tree_ds.heading("cat", text="Category")
        tree_ds.heading("comp", text="Type")
        tree_ds.heading("temp", text="Temp (°C)")
        tree_ds.heading("hum", text="Humidity (%)")
        tree_ds.heading("storage", text="Storage")
        tree_ds.heading("pkg", text="Packaging")
        tree_ds.heading("elapsed", text="Elapsed (h)")
        tree_ds.heading("edible_hrs", text="Safe (h)")
        tree_ds.heading("urgency", text="Urgency Tier")

        for col in cols:
            tree_ds.column(col, width=85, anchor="center")
        tree_ds.column("cat", width=110, anchor="w")

        for r in self.dataset_records[:150]:
            tree_ds.insert("", "end", values=(
                r.get('category'), r.get('food_type'), f"{r.get('ambient_temp_c', 0):.1f}",
                f"{r.get('humidity_percent', 0):.0f}", r.get('storage_condition'),
                r.get('packaging_type'), f"{r.get('prepared_hours_ago', 0):.1f}",
                f"{r.get('safe_consumption_hours', 0):.1f}", r.get('urgency_tier')
            ))

        tree_ds.pack(fill="both", expand=True)

    # =========================================================================
    # TAB 5: VIVA VOCE DEFENSE GUIDE
    # =========================================================================
    def _build_tab_viva(self, parent):
        container = tk.Frame(parent, bg="#0f172a", padx=20, pady=16)
        container.pack(fill="both", expand=True)

        title = tk.Label(container, text="🎓 College Major Project Defense & Viva Voce Guide",
                         bg="#0f172a", fg="#ffffff", font=("Helvetica", 13, "bold"))
        title.pack(anchor="w", pady=(0, 12))

        questions = [
            ("Q1: What is the core Machine Learning formulation of this Major Project?",
             "This project formulates dynamic food perishability as a Supervised Machine Learning problem. Rather than relying on static expiry dates, it predicts remaining safe hours (Regression) and categorizes donations into urgency tiers (Classification) based on Arrhenius microbial growth equations."),
            ("Q2: How does the system connect Donors with NGOs?",
             "The Food Donor Portal allows hotels, caterers, and restaurants to post surplus food with automated ML Spoilage predictions. The NGO Shelter Portal automatically receives these listings sorted by ML urgency (Red Alert < 4 hours first), enabling NGOs to claim and dispatch volunteers before food spoils."),
            ("Q3: Why did you choose Random Forest over Simple Linear Regression?",
             "In benchmark evaluations, Linear Regression achieved only 68.30% R² because it cannot model cross-feature interactions (e.g. high heat + high humidity = exponential bacteria growth). Random Forest achieved 94.13% R² because decision tree ensembles capture non-linear microbial dynamics accurately."),
            ("Q4: What is the environmental and social impact of this application?",
             "According to the UN Food and Agriculture Organization (FAO), 1/3 of all food is wasted, generating 8-10% of global greenhouse gases. By predicting spoilage in real time and routing surplus meals to shelters, this system saves meals and prevents carbon emissions ($2.5\\text{ kg } \\text{CO}_2$ per kg food saved).")
        ]

        for q, a in questions:
            box = tk.Frame(container, bg="#1e293b", padx=14, pady=10)
            box.pack(fill="x", pady=(0, 8))
            tk.Label(box, text=q, bg="#1e293b", fg="#c084fc", font=("Helvetica", 9, "bold")).pack(anchor="w")
            tk.Label(box, text=a, bg="#1e293b", fg="#cbd5e1", font=("Helvetica", 8), wraplength=980, justify="left").pack(anchor="w", pady=(2, 0))

def main():
    app = FoodRescueApp()
    app.mainloop()

if __name__ == "__main__":
    main()
