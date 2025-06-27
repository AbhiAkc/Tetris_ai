import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import subprocess
import platform
import time
import requests
import json
import threading
import psutil
import sys
import shutil
from pathlib import Path
import math
import random
import sqlite3
import re
import hashlib
from PIL import Image, ImageTk
import cv2
import numpy as np
import openai
from cryptography.fernet import Fernet
import pickle

class TETRISInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_database()
        self.setup_window()
        self.setup_ai_engine()
        self.setup_ui()
        self.setup_custom_commands()
        self.is_listening = False
        self.conversation_history = []
        self.user_preferences = self.load_user_preferences()
        self.learning_mode = True
        self.security_level = "STANDARD"
        self.active_protocols = []
        
    def setup_database(self):
        """Initialize SQLite database for custom commands and learning"""
        self.db_path = "tetris_memory.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_commands (
                id INTEGER PRIMARY KEY,
                trigger TEXT UNIQUE,
                response TEXT,
                action_type TEXT,
                parameters TEXT,
                usage_count INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_memory (
                id INTEGER PRIMARY KEY,
                user_input TEXT,
                tetris_response TEXT,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importance_score INTEGER DEFAULT 1
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY,
                pattern TEXT,
                response_template TEXT,
                confidence_score REAL,
                success_rate REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def setup_window(self):
        """Setup the main T.E.T.R.I.S window with modern design"""
        self.root.title("T.E.T.R.I.S - Tactically Enhanced Technology Response Intelligence System")
        self.root.geometry("1400x900")
        self.root.configure(bg="#000000")
        self.root.attributes('-alpha', 0.95)  # Semi-transparent
        
        # Modern styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Modern.TFrame', background='#0a0a0a')
        style.configure('Modern.TLabel', background='#0a0a0a', foreground='#00ff41')
        style.configure('Modern.TButton', background='#1a1a1a', foreground='#00ff41')
        
        # Set window icon
        try:
            self.root.iconbitmap("tetris.ico")
        except:
            pass
    
    def setup_ai_engine(self):
        """Initialize advanced AI components"""
        # Text-to-Speech with advanced settings
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            
            # Find the best voice (prefer female for Friday/EDITH style)
            selected_voice = None
            for voice in voices:
                if any(name in voice.name.lower() for name in ['zira', 'hazel', 'female']):
                    selected_voice = voice.id
                    break
            
            if selected_voice:
                self.engine.setProperty('voice', selected_voice)
            
            self.engine.setProperty('rate', 165)
            self.engine.setProperty('volume', 0.9)
            self.tts_available = True
        except Exception as e:
            print(f"TTS Error: {e}")
            self.tts_available = False
        
        # Speech Recognition with advanced settings
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust recognition settings
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
            
            self.sr_available = True
        except Exception as e:
            print(f"Speech Recognition Error: {e}")
            self.sr_available = False
        
        # Initialize OpenAI (optional - for advanced AI responses)
        self.openai_available = False
        try:
            # You can set your OpenAI API key here
            # openai.api_key = "your-api-key-here"
            # self.openai_available = True
            pass
        except:
            pass
    
    def setup_ui(self):
        """Create the modern T.E.T.R.I.S user interface"""
        # Main container with gradient effect
        main_frame = tk.Frame(self.root, bg="#000000")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header with holographic-style branding
        header_frame = tk.Frame(main_frame, bg="#000000", height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # T.E.T.R.I.S Logo with animation effect
        self.title_label = tk.Label(
            header_frame, 
            text="◆ T.E.T.R.I.S ◆", 
            font=("Orbitron", 28, "bold"), 
            fg="#00ff41", 
            bg="#000000"
        )
        self.title_label.pack(side=tk.LEFT, pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Tactically Enhanced Technology Response Intelligence System",
            font=("Consolas", 10),
            fg="#00aa33",
            bg="#000000"
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(15, 0))
        
        # Status panel
        status_frame = tk.Frame(header_frame, bg="#000000")
        status_frame.pack(side=tk.RIGHT, pady=10)
        
        self.status_label = tk.Label(
            status_frame, 
            text="● ACTIVE", 
            font=("Consolas", 12, "bold"), 
            fg="#00ff41", 
            bg="#000000"
        )
        self.status_label.pack()
        
        self.security_label = tk.Label(
            status_frame,
            text=f"Security: {self.security_level}",
            font=("Consolas", 9),
            fg="#ffaa00",
            bg="#000000"
        )
        self.security_label.pack()
        
        # Main content area with tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat tab
        self.setup_chat_tab()
        
        # Command Manager tab
        self.setup_command_tab()
        
        # System Monitor tab
        self.setup_monitor_tab()
        
        # Learning Center tab
        self.setup_learning_tab()
        
        # Control panel
        self.setup_control_panel(main_frame)
        
        # Initialize with welcome message
        welcome_msg = "T.E.T.R.I.S system online. All systems operational. How may I assist you today?"
        self.add_message("T.E.T.R.I.S", welcome_msg)
        self.speak(welcome_msg)
        
        # Start background processes
        self.start_background_processes()
    
    def setup_chat_tab(self):
        """Setup the main chat interface"""
        self.chat_frame = tk.Frame(self.notebook, bg="#000000")
        self.notebook.add(self.chat_frame, text="🎯 MAIN INTERFACE")
        
        # Chat display with modern styling
        chat_container = tk.Frame(self.chat_frame, bg="#000000")
        chat_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            bg="#0a0a0a",
            fg="#00ff41",
            font=("Consolas", 11),
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            insertbackground="#00ff41",
            selectbackground="#003300",
            borderwidth=2,
            relief="solid"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Advanced input area
        input_container = tk.Frame(self.chat_frame, bg="#000000", height=100)
        input_container.pack(fill=tk.X, padx=10, pady=(0, 10))
        input_container.pack_propagate(False)
        
        # Input field with autocomplete
        self.input_entry = tk.Entry(
            input_container,
            bg="#1a1a1a",
            fg="#ffffff",
            font=("Consolas", 12),
            insertbackground="#00ff41",
            borderwidth=2,
            relief="solid"
        )
        self.input_entry.pack(fill=tk.X, pady=(10, 5))
        self.input_entry.bind('<Return>', self.process_text_input)
        self.input_entry.bind('<KeyRelease>', self.on_key_release)
        
        # Suggestion box
        self.suggestion_var = tk.StringVar()
        self.suggestion_label = tk.Label(
            input_container,
            textvariable=self.suggestion_var,
            font=("Consolas", 9),
            fg="#666666",
            bg="#000000"
        )
        self.suggestion_label.pack(anchor=tk.W)
        
        # Control buttons with modern styling
        button_frame = tk.Frame(input_container, bg="#000000")
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.voice_button = tk.Button(
            button_frame,
            text="🎤 VOICE COMMAND",
            bg="#00ff41",
            fg="#000000",
            font=("Consolas", 10, "bold"),
            command=self.toggle_voice_listening,
            relief="flat",
            pady=5
        )
        self.voice_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.send_button = tk.Button(
            button_frame,
            text="⚡ EXECUTE",
            bg="#ff4444",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            command=self.process_text_input,
            relief="flat",
            pady=5
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.learn_button = tk.Button(
            button_frame,
            text="🧠 TEACH MODE",
            bg="#4444ff",
            fg="#ffffff",
            font=("Consolas", 10, "bold"),
            command=self.enter_teach_mode,
            relief="flat",
            pady=5
        )
        self.learn_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quick actions
        quick_frame = tk.Frame(button_frame, bg="#000000")
        quick_frame.pack(side=tk.RIGHT)
        
        quick_buttons = [
            ("🔒 SECURITY", self.toggle_security),
            ("📊 SCAN", self.system_scan),
            ("🌐 WEB", self.quick_web),
            ("💾 MEMORY", self.memory_mode)
        ]
        
        for text, command in quick_buttons:
            btn = tk.Button(
                quick_frame,
                text=text,
                bg="#333333",
                fg="#ffffff",
                font=("Consolas", 8),
                command=command,
                relief="flat",
                padx=8,
                pady=2
            )
            btn.pack(side=tk.LEFT, padx=1)
    
    def setup_command_tab(self):
        """Setup custom command management"""
        self.command_frame = tk.Frame(self.notebook, bg="#000000")
        self.notebook.add(self.command_frame, text="⚙️ COMMANDS")
        
        # Command list
        list_frame = tk.Frame(self.command_frame, bg="#000000")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            list_frame,
            text="Custom Commands Database",
            font=("Consolas", 14, "bold"),
            fg="#00ff41",
            bg="#000000"
        ).pack(pady=(0, 10))
        
        # Command treeview
        columns = ("Trigger", "Action", "Usage", "Last Used")
        self.command_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.command_tree.heading(col, text=col)
            self.command_tree.column(col, width=200)
        
        self.command_tree.pack(fill=tk.BOTH, expand=True)
        
        # Command management buttons
        cmd_button_frame = tk.Frame(self.command_frame, bg="#000000")
        cmd_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        cmd_buttons = [
            ("➕ Add Command", self.add_custom_command),
            ("✏️ Edit Command", self.edit_custom_command),
            ("🗑️ Delete Command", self.delete_custom_command),
            ("🔄 Refresh List", self.refresh_command_list),
            ("📤 Export Commands", self.export_commands),
            ("📥 Import Commands", self.import_commands)
        ]
        
        for text, command in cmd_buttons:
            btn = tk.Button(
                cmd_button_frame,
                text=text,
                bg="#333333",
                fg="#ffffff",
                font=("Consolas", 9),
                command=command,
                relief="flat",
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        self.refresh_command_list()
    
    def setup_monitor_tab(self):
        """Setup system monitoring interface"""
        self.monitor_frame = tk.Frame(self.notebook, bg="#000000")
        self.notebook.add(self.monitor_frame, text="📊 MONITOR")
        
        # System stats display
        stats_frame = tk.Frame(self.monitor_frame, bg="#000000")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.stats_display = scrolledtext.ScrolledText(
            stats_frame,
            bg="#0a0a0a",
            fg="#00ff41",
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20
        )
        self.stats_display.pack(fill=tk.BOTH, expand=True)
        
        # Monitor controls
        monitor_controls = tk.Frame(self.monitor_frame, bg="#000000")
        monitor_controls.pack(fill=tk.X, padx=10, pady=10)
        
        monitor_buttons = [
            ("🔄 Refresh", self.refresh_system_stats),
            ("📈 Performance", self.detailed_performance),
            ("🌡️ Temperature", self.system_temperature),
            ("🔌 Processes", self.running_processes),
            ("💾 Storage", self.storage_analysis),
            ("🌐 Network", self.network_status)
        ]
        
        for text, command in monitor_buttons:
            btn = tk.Button(
                monitor_controls,
                text=text,
                bg="#333333",
                fg="#ffffff",
                font=("Consolas", 9),
                command=command,
                relief="flat",
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Auto-refresh system stats
        self.refresh_system_stats()
    
    def setup_learning_tab(self):
        """Setup AI learning interface"""
        self.learning_frame = tk.Frame(self.notebook, bg="#000000")
        self.notebook.add(self.learning_frame, text="🧠 LEARNING")
        
        # Learning status
        status_frame = tk.Frame(self.learning_frame, bg="#000000")
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.learning_status = tk.Label(
            status_frame,
            text=f"Learning Mode: {'ACTIVE' if self.learning_mode else 'INACTIVE'}",
            font=("Consolas", 12, "bold"),
            fg="#00ff41" if self.learning_mode else "#ff4444",
            bg="#000000"
        )
        self.learning_status.pack()
        
        # Pattern analysis
        pattern_frame = tk.Frame(self.learning_frame, bg="#000000")
        pattern_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            pattern_frame,
            text="Learned Patterns & Behaviors",
            font=("Consolas", 14, "bold"),
            fg="#00ff41",
            bg="#000000"
        ).pack(pady=(0, 10))
        
        self.pattern_display = scrolledtext.ScrolledText(
            pattern_frame,
            bg="#0a0a0a",
            fg="#00ff41",
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=15
        )
        self.pattern_display.pack(fill=tk.BOTH, expand=True)
        
        # Learning controls
        learning_controls = tk.Frame(self.learning_frame, bg="#000000")
        learning_controls.pack(fill=tk.X, padx=10, pady=10)
        
        learning_buttons = [
            ("🔄 Toggle Learning", self.toggle_learning),
            ("📊 Analyze Patterns", self.analyze_patterns),
            ("🧹 Clear Memory", self.clear_learning_memory),
            ("💾 Export Learning", self.export_learning_data),
            ("🎯 Train Response", self.train_response)
        ]
        
        for text, command in learning_buttons:
            btn = tk.Button(
                learning_controls,
                text=text,
                bg="#333333",
                fg="#ffffff",
                font=("Consolas", 9),
                command=command,
                relief="flat",
                padx=10,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        self.analyze_patterns()
    
    def setup_control_panel(self, parent):
        """Setup the main control panel"""
        control_frame = tk.Frame(parent, bg="#000000", height=60)
        control_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        control_frame.pack_propagate(False)
        
        # System control buttons
        system_buttons = [
            ("🔥 EMERGENCY SHUTDOWN", self.emergency_shutdown, "#ff0000"),
            ("🛡️ DEFENSE MODE", self.defense_mode, "#ff8800"),
            ("🎯 PRECISION MODE", self.precision_mode, "#0088ff"),
            ("🌟 FRIDAY MODE", self.friday_mode, "#00ff88"),
            ("🔧 MAINTENANCE", self.maintenance_mode, "#888888"),
            ("📱 MINIMIZE", self.minimize_window, "#444444")
        ]
        
        for text, command, color in system_buttons:
            btn = tk.Button(
                control_frame,
                text=text,
                bg=color,
                fg="#ffffff",
                font=("Consolas", 9, "bold"),
                command=command,
                relief="flat",
                padx=8,
                pady=8
            )
            btn.pack(side=tk.LEFT, padx=2, pady=5)
    
    def setup_custom_commands(self):
        """Load custom commands from database"""
        self.custom_commands = {}
        try:
            self.cursor.execute("SELECT trigger, response, action_type, parameters FROM custom_commands")
            for row in self.cursor.fetchall():
                trigger, response, action_type, parameters = row
                self.custom_commands[trigger.lower()] = {
                    'response': response,
                    'action_type': action_type,
                    'parameters': parameters
                }
        except Exception as e:
            print(f"Error loading custom commands: {e}")
    
    def add_message(self, sender, message, message_type="normal"):
        """Add message to chat display with advanced formatting"""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if sender == "T.E.T.R.I.S":
            self.chat_display.insert(tk.END, f"[{timestamp}] ◆ T.E.T.R.I.S: ", "tetris_header")
            self.chat_display.insert(tk.END, f"{message}\n\n", "tetris_msg")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] USER: ", "user_header")
            self.chat_display.insert(tk.END, f"{message}\n\n", "user_msg")
        
        # Configure advanced styling
        self.chat_display.tag_config("tetris_header", foreground="#00ff41", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("tetris_msg", foreground="#ffffff")
        self.chat_display.tag_config("user_header", foreground="#ffaa00", font=("Consolas", 11, "bold"))
        self.chat_display.tag_config("user_msg", foreground="#cccccc")
        
        # Special formatting for different message types
        if message_type == "warning":
            self.chat_display.tag_config("tetris_msg", foreground="#ff8800")
        elif message_type == "error":
            self.chat_display.tag_config("tetris_msg", foreground="#ff4444")
        elif message_type == "success":
            self.chat_display.tag_config("tetris_msg", foreground="#44ff44")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
        # Store in conversation memory
        self.store_conversation(message if sender == "USER" else "", message if sender == "T.E.T.R.I.S" else "")
    
    def speak(self, text, priority="normal"):
        """Advanced text-to-speech with priority system"""
        if self.tts_available:
            def speak_thread():
                try:
                    # Adjust speech parameters based on priority
                    if priority == "urgent":
                        self.engine.setProperty('rate', 180)
                        self.engine.setProperty('volume', 1.0)
                    elif priority == "whisper":
                        self.engine.setProperty('rate', 150)
                        self.engine.setProperty('volume', 0.6)
                    else:
                        self.engine.setProperty('rate', 165)
                        self.engine.setProperty('volume', 0.9)
                    
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Speech error: {e}")
            
            threading.Thread(target=speak_thread, daemon=True).start()
    
    def toggle_voice_listening(self):
        """Advanced voice listening with continuous mode"""
        if not self.is_listening:
            self.start_voice_listening()
        else:
            self.stop_voice_listening()
    
    def start_voice_listening(self):
        """Start advanced voice recognition"""
        if not self.sr_available:
            self.add_message("T.E.T.R.I.S", "Voice recognition systems offline. Please check microphone connection.", "error")
            return
        
        self.is_listening = True
        self.voice_button.config(text="🛑 STOP LISTENING", bg="#ff4444")
        self.status_label.config(text="● LISTENING", fg="#ffaa00")
        
        def continuous_listen():
            while self.is_listening:
                try:
                    with self.microphone as source:
                        # Adjust for ambient noise
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        
                        # Listen for audio
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=8)
                    
                    # Recognize speech
                    command = self.recognizer.recognize_google(audio)
                    
                    # Process command on main thread
                    self.root.after(0, lambda: self.process_voice_command(command))
                    
                    # Brief pause before next listen
                    time.sleep(0.5)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    self.root.after(0, lambda: self.add_message("T.E.T.R.I.S", f"Voice recognition error: {str(e)}", "error"))
                    break
        
        threading.Thread(target=continuous_listen, daemon=True).start()
    
    def stop_voice_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        self.voice_button.config(text="🎤 VOICE COMMAND", bg="#00ff41")
        self.status_label.config(text="● ACTIVE", fg="#00ff41")
    
    def process_voice_command(self, command):
        """Process voice command with learning capability"""
        self.add_message("USER", command)
        response = self.process_command(command)
        self.add_message("T.E.T.R.I.S", response)
        self.speak(response)
    
    def process_text_input(self, event=None):
        """Process text input with advanced parsing"""
        command = self.input_entry.get().strip()
        if command:
            self.add_message("USER", command)
            response = self.process_command(command)
            self.add_message("T.E.T.R.I.S", response)
            self.speak(response)
            self.input_entry.delete(0, tk.END)
            self.suggestion_var.set("")
    
    def process_command(self, command):
        """Advanced command processing with AI learning"""
        original_command = command
        command = command.lower().strip()
        
        # Check for wake words
        if any(wake in command for wake in ['tetris', 'friday', 'edith', 'ai']):
            command = self.remove_wake_words(command)
        
        # Check custom commands first
        custom_response = self.check_custom_commands(command)
        if custom_response:
            return custom_response
        
        # AI-powered response generation
        if self.learning_mode:
            learned_response = self.generate_learned_response(command)
            if learned_response:
                return learned_response
        
        # Core command processing
        response = self.process_core_commands(command, original_command)
        
        # Learn from this interaction
        if self.learning_mode:
            self.learn_from_interaction(command, response)
        
        return response
    
    def process_core_commands(self, command, original_command):
        """Process core system commands"""
        
        # Advanced greetings with personality
        if any(word in command for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            greetings = [
                "Good to see you again. T.E.T.R.I.S systems are fully operational.",
                "Hello. All systems green and ready for your commands.",
                "Greetings. I've been monitoring system status while you were away.",
                "Welcome back. How may I assist you today?"
            ]
            return random.choice(greetings)
        
        # Personality queries
        elif any(phrase in command for phrase in ['who are you', 'what are you', 'introduce yourself']):
            return ("I am T.E.T.R.I.S - Tactically Enhanced Technology Response Intelligence System. "
                   "I'm an advanced AI assistant designed to learn, adapt, and assist with complex tasks. "
                   "Think of me as your personal Friday or EDITH system.")
        
        # Time and date with advanced formatting
        elif 'time' in command:
            now = datetime.datetime.now()
            return f"Current time: {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}"
        
        elif 'date' in command:
            return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}"
        
        # Advanced system controls
        elif any(phrase in command for phrase in ['shutdown', 'turn off', 'power down']):
            return self.advanced_shutdown(command)
        
        elif any(phrase in command for phrase in ['restart', 'reboot', 'reset']):
            return self.advanced_restart(command)
        
        elif 'sleep' in command or 'hibernate' in command:
            return self.advanced_sleep(command)
        
        elif 'lock' in command:
            return self.advanced_lock()
        
        # Application management
        elif 'open' in command or 'launch' in command:
            app = self.extract_app_name(command, ['open', 'launch'])
            return self.advanced_open_application(app)
        
        elif 'close' in command or 'terminate' in command:
            app = self.extract_app_name(command, ['close', 'terminate'])
            return self.advanced_close_application(app)
        
        # Web and search with AI enhancement
        elif any(phrase in command for phrase in ['search', 'google', 'find', 'look up']):
            query = self.extract_search_query(command)
            return self.advanced_web_search(query)
        
        elif 'youtube' in command:
            query = self.extract_search_query(command, 'youtube')
            return self.advanced_youtube_search(query)
        
        # Study and learning assistance
        elif any(phrase in command for phrase in ['study', 'homework', 'learn', 'explain', 'teach me']):
            return self.advanced_study_assistant(command)
        
        elif any(phrase in command for phrase in ['calculate', 'math', 'compute', 'solve']):
            return self.advanced_calculator(command)
        
        elif any(phrase in command for phrase in ['define', 'meaning', 'what is', 'explain']):
            return self.advanced_dictionary(command)
        
        # File operations with AI
        elif any(phrase in command for phrase in ['file', 'folder', 'directory', 'create', 'delete', 'move', 'copy']):
            return self.advanced_file_operations(command)
        
        # System information
        elif any(phrase in command for phrase in ['system status', 'performance', 'resources', 'stats']):
            return self.get_advanced_system_status()
        
        elif 'weather' in command:
            location = self.extract_location(command)
            return self.get_advanced_weather(location)
        
        # Entertainment
        elif 'joke' in command:
            return self.tell_advanced_joke()
        
        elif 'music' in command or 'song' in command:
            return self.advanced_music_control(command)
        
        # AI and learning commands
        elif any(phrase in command for phrase in ['remember', 'save', 'note', 'remind me']):
            return self.create_memory(command)
        
        elif any(phrase in command for phrase in ['forget', 'delete memory', 'clear']):
            return self.delete_memory(command)
        
        elif 'what do you remember' in command or 'recall' in command:
            return self.recall_memory(command)
        
        # Security and privacy
        elif any(phrase in command for phrase in ['security scan', 'check security', 'scan system']):
            return self.security_scan()
        
        elif 'privacy mode' in command:
            return self.toggle_privacy_mode()
        
        # Advanced features
        elif 'analyze' in command:
            return self.perform_analysis(command)
        
        elif 'predict' in command or 'forecast' in command:
            return self.make_prediction(command)
        
        elif 'optimize' in command:
            return self.optimize_system(command)
        
        # Help system
        elif 'help' in command or 'commands' in command:
            return self.show_advanced_help()
        
        # Fallback with AI learning
        else:
            return self.generate_intelligent_response(command)
    
    def extract_app_name(self, command, remove_words):
        """Extract application name from command"""
        for word in remove_words:
            command = command.replace(word, '')
        return command.strip()
    
    def extract_search_query(self, command, platform=None):
        """Extract search query from command"""
        remove_words = ['search', 'google', 'find', 'look up', 'for', platform] if platform else ['search', 'google', 'find', 'look up', 'for']
        query = command
        for word in remove_words:
            if word:
                query = query.replace(word, '')
        return query.strip()
    
    def extract_location(self, command):
        """Extract location from weather command"""
        location = command.replace('weather', '').replace('in', '').replace('for', '').strip()
        return location if location else "current location"
    
    def advanced_open_application(self, app_name):
        """Advanced application launcher with learning"""
        # Enhanced application dictionary
        apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'explorer': 'explorer.exe',
            'file explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'task manager': 'taskmgr.exe',
            'control panel': 'control.exe',
            'settings': 'ms-settings:',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'outlook': 'outlook.exe',
            'teams': 'teams.exe',
            'discord': 'discord.exe',
            'spotify': 'spotify.exe',
            'steam': 'steam.exe',
            'vscode': 'code.exe',
            'visual studio code': 'code.exe',
            'photoshop': 'photoshop.exe',
            'premiere': 'premiere.exe',
            'after effects': 'afterfx.exe'
        }
        
        app_lower = app_name.lower()
        
        if app_lower in apps:
            try:
                subprocess.Popen(apps[app_lower], shell=True)
                return f"Launching {app_name}. Application should be starting now."
            except Exception as e:
                return f"Failed to launch {app_name}. Error: {str(e)}"
        else:
            # Try to find similar applications
            similar_apps = [app for app in apps.keys() if app_lower in app or app in app_lower]
            if similar_apps:
                return f"Did you mean: {', '.join(similar_apps)}? Please specify which application you'd like to open."
            
            # Try to launch directly
            try:
                subprocess.Popen(app_name, shell=True)
                return f"Attempting to launch {app_name}. If this fails, please check the application name."
            except:
                return f"Application '{app_name}' not found. Try saying 'help' for available applications."
    
    def advanced_close_application(self, app_name):
        """Advanced application termination"""
        try:
            # Common process names
            process_map = {
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'explorer': 'explorer.exe'
            }
            
            process_name = process_map.get(app_name.lower(), f"{app_name}.exe")
            
            # Terminate process
            subprocess.run(['taskkill', '/f', '/im', process_name], 
                         capture_output=True, text=True, check=True)
            return f"Successfully terminated {app_name}."
        except subprocess.CalledProcessError:
            return f"Could not terminate {app_name}. Process may not be running."
        except Exception as e:
            return f"Error terminating {app_name}: {str(e)}"
    
    def advanced_web_search(self, query):
        """Advanced web search with multiple engines"""
        if not query:
            return "What would you like me to search for?"
        
        search_engines = {
            'google': f"https://www.google.com/search?q={query.replace(' ', '+')}",
            'bing': f"https://www.bing.com/search?q={query.replace(' ', '+')}",
            'duckduckgo': f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
        }
        
        # Default to Google
        webbrowser.open(search_engines['google'])
        return f"Searching for '{query}' on Google. Results should appear in your browser."
    
    def advanced_youtube_search(self, query):
        """Advanced YouTube search"""
        if not query:
            return "What would you like me to search for on YouTube?"
        
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching YouTube for '{query}'. Results should appear in your browser."
    
    def advanced_study_assistant(self, command):
        """Advanced study assistance with subject detection"""
        subjects = {
            'math': "I can help with mathematics. Try asking me to calculate equations, explain formulas, or solve problems.",
            'science': "I can assist with science topics including physics, chemistry, and biology. What specific area interests you?",
            'history': "I can help with historical facts, dates, and events. What time period or topic are you studying?",
            'english': "I can help with grammar, writing, literature analysis, and vocabulary. What do you need help with?",
            'computer': "I can help with programming, computer science concepts, and technology. What programming language or topic?",
            'physics': "I can help with physics concepts, formulas, and problem-solving. What physics topic are you working on?",
            'chemistry': "I can assist with chemical equations, periodic table, and reactions. What chemistry topic do you need help with?",
            'biology': "I can help with biological processes, anatomy, and life sciences. What biology topic interests you?"
        }
        
        for subject, response in subjects.items():
            if subject in command.lower():
                return response
        
        return ("Study mode activated. I can help with various subjects including mathematics, science, history, English, and computer science. "
                "What subject would you like to focus on?")
    
    def advanced_calculator(self, command):
        """Advanced calculator with complex operations"""
        # Extract mathematical expression
        expression = command
        for word in ['calculate', 'compute', 'solve', 'what is', 'math']:
            expression = expression.replace(word, '')
        expression = expression.strip()
        
        if not expression:
            return "Please provide a mathematical expression to calculate."
        
        try:
            # Enhanced expression processing
            expression = expression.replace('x', '*')
            expression = expression.replace('÷', '/')
            expression = expression.replace('^', '**')
            
            # Handle advanced functions
            replacements = {
                'sin': 'math.sin',
                'cos': 'math.cos',
                'tan': 'math.tan',
                'sqrt': 'math.sqrt',
                'log': 'math.log',
                'ln': 'math.log',
                'exp': 'math.exp',
                'pi': 'math.pi',
                'e': 'math.e',
                'factorial': 'math.factorial'
            }
            
            for old, new in replacements.items():
                expression = expression.replace(old, new)
            
            # Safe evaluation
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            # Format result appropriately
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)
            
            return f"The result of '{expression}' is: {result}"
            
        except Exception as e:
            return f"I couldn't calculate that expression. Please check the syntax. Error: {str(e)}"
    
    def advanced_dictionary(self, command):
        """Advanced dictionary with AI-powered definitions"""
        word = command
        for phrase in ['define', 'meaning', 'what is', 'explain']:
            word = word.replace(phrase, '')
        word = word.strip()
        
        if not word:
            return "What word would you like me to define?"
        
        # Try to get definition from online API (you can integrate with dictionary APIs)
        try:
            # Placeholder for dictionary API integration
            return f"Looking up definition for '{word}'. For detailed definitions, I recommend checking online dictionaries or saying 'search define {word}'."
        except:
            return f"I'll search for the definition of '{word}' online."
    
    def advanced_file_operations(self, command):
        """Advanced file operations with AI assistance"""
        if 'create' in command and 'folder' in command:
            return self.create_folder_dialog()
        elif 'delete' in command:
            return "What file or folder would you like to delete? Please be specific for safety."
        elif 'copy' in command:
            return "What file would you like to copy and where?"
        elif 'move' in command:
            return "What file would you like to move and where?"
        elif 'find' in command or 'search' in command:
            return "What file are you looking for? I can help you search."
        else:
            return "I can help with file operations like create, delete, copy, move, or find files. What would you like to do?"
    
    def create_folder_dialog(self):
        """Create folder with dialog"""
        folder_name = simpledialog.askstring("Create Folder", "Enter folder name:")
        if folder_name:
            try:
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                folder_path = os.path.join(desktop, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                return f"Created folder '{folder_name}' on desktop."
            except Exception as e:
                return f"Failed to create folder: {str(e)}"
        return "Folder creation cancelled."
    
    def get_advanced_system_status(self):
        """Get comprehensive system status"""
        try:
            # CPU Information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk Information
            disk = psutil.disk_usage('/')
            
            # Network Information
            network = psutil.net_io_counters()
            
            # System Information
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            status = f"""T.E.T.R.I.S System Status Report:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖥️  SYSTEM OVERVIEW:
   Platform: {platform.system()} {platform.release()}
   Architecture: {platform.architecture()[0]}
   Processor: {platform.processor()}
   Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
   Uptime: {str(uptime).split('.')[0]}

⚡ CPU STATUS:
   Usage: {cpu_percent}%
   Cores: {cpu_count} ({psutil.cpu_count(logical=False)} physical)
   Frequency: {cpu_freq.current:.2f} MHz
   Max Frequency: {cpu_freq.max:.2f} MHz

💾 MEMORY STATUS:
   Total RAM: {memory.total // (1024**3)} GB
   Available: {memory.available // (1024**3)} GB
   Used: {memory.used // (1024**3)} GB
   Usage: {memory.percent}%
   
   Swap Total: {swap.total // (1024**3)} GB
   Swap Used: {swap.used // (1024**3)} GB

💿 STORAGE STATUS:
   Total Space: {disk.total // (1024**3)} GB
   Free Space: {disk.free // (1024**3)} GB
   Used Space: {disk.used // (1024**3)} GB
   Usage: {disk.percent}%

🌐 NETWORK STATUS:
   Bytes Sent: {network.bytes_sent // (1024**2)} MB
   Bytes Received: {network.bytes_recv // (1024**2)} MB
   Packets Sent: {network.packets_sent}
   Packets Received: {network.packets_recv}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
System Status: {'🟢 OPTIMAL' if cpu_percent < 80 and memory.percent < 80 else '🟡 MONITORING' if cpu_percent < 90 and memory.percent < 90 else '🔴 CRITICAL'}"""
            
            return status
            
        except Exception as e:
            return f"Error retrieving system status: {str(e)}"
    
    def get_advanced_weather(self, location):
        """Get advanced weather information"""
        try:
            # Using a free weather API
            if location == "current location":
                url = "http://wttr.in/?format=3"
            else:
                url = f"http://wttr.in/{location}?format=3"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return f"Weather for {location}: {response.text.strip()}"
            else:
                return f"Unable to retrieve weather for {location}."
        except Exception as e:
            return f"Weather service unavailable: {str(e)}"
    
    def tell_advanced_joke(self):
        """Tell advanced jokes with categories"""
        joke_categories = {
            'tech': [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
                "Why did the AI break up with the database? It couldn't handle the relationship!",
                "What's a computer's favorite snack? Microchips!"
            ],
            'science': [
                "Why don't scientists trust atoms? Because they make up everything!",
                "What do you call a sleeping bull at the particle accelerator? A bulldozer!",
                "Why did the photon refuse to check a bag? Because it was traveling light!",
                "What's the best thing about Switzerland? I don't know, but the flag is a big plus!"
            ],
            'ai': [
                "Why did the neural network go to therapy? It had too many layers of issues!",
                "What did the machine learning algorithm say to the data? You complete me!",
                "Why don't AIs ever get lost? They always know their way around the neural pathways!",
                "What's an AI's favorite type of music? Deep learning beats!"
            ]
        }
        
        category = random.choice(list(joke_categories.keys()))
        joke = random.choice(joke_categories[category])
        return f"Here's a {category} joke for you: {joke}"
    
    def advanced_music_control(self, command):
        """Advanced music control system"""
        if 'play' in command:
            # Extract song/artist if mentioned
            music_query = command.replace('play', '').replace('music', '').strip()
            
            # Try to open music applications
            music_apps = ['spotify.exe', 'winamp.exe', 'vlc.exe', 'wmplayer.exe', 'itunes.exe']
            
            for app in music_apps:
                try:
                    subprocess.Popen(app, shell=True)
                    if music_query:
                        return f"Opening music player and searching for '{music_query}'."
                    else:
                        return "Opening music player."
                except:
                    continue
            
            # If no music app found, open music folder
            music_folder = os.path.join(os.path.expanduser('~'), 'Music')
            if os.path.exists(music_folder):
                os.startfile(music_folder)
                return "Opening music folder."
            
            return "No music player found. You can install Spotify, VLC, or other music applications."
        
        elif 'stop' in command or 'pause' in command:
            return "You can control playback using your music player's controls or media keys."
        
        else:
            return "I can help you play music, open music players, or manage your music library. What would you like to do?"
    
    def check_custom_commands(self, command):
        """Check for custom user-defined commands"""
        for trigger, cmd_data in self.custom_commands.items():
            if trigger in command:
                # Update usage statistics
                self.cursor.execute(
                    "UPDATE custom_commands SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP WHERE trigger = ?",
                    (trigger,)
                )
                self.conn.commit()
                
                # Execute custom action
                if cmd_data['action_type'] == 'response':
                    return cmd_data['response']
                elif cmd_data['action_type'] == 'command':
                    try:
                        subprocess.run(cmd_data['parameters'], shell=True)
                        return cmd_data['response']
                    except:
                        return f"Failed to execute custom command: {trigger}"
                elif cmd_data['action_type'] == 'web':
                    webbrowser.open(cmd_data['parameters'])
                    return cmd_data['response']
        
        return None
    
    def generate_learned_response(self, command):
        """Generate response based on learned patterns"""
        try:
            self.cursor.execute(
                "SELECT response_template, confidence_score FROM learned_patterns WHERE ? LIKE '%' || pattern || '%' ORDER BY confidence_score DESC LIMIT 1",
                (command,)
            )
            result = self.cursor.fetchone()
            
            if result and result[1] > 0.7:  # Confidence threshold
                return result[0]
        except:
            pass
        
        return None
    
    def generate_intelligent_response(self, command):
        """Generate intelligent response for unknown commands"""
        # Analyze command for keywords
        keywords = command.split()
        
        # Check for similar commands in database
        similar_commands = []
        for word in keywords:
            if len(word) > 3:  # Ignore short words
                similar_commands.extend(self.find_similar_commands(word))
        
        if similar_commands:
            return f"I'm not sure about that command. Did you mean: {', '.join(similar_commands[:3])}?"
        
        # Generic helpful response
        responses = [
            "I'm still learning that command. Can you teach me by saying 'teach mode' and showing me what you want?",
            "That's a new one for me. You can add custom commands or try rephrasing your request.",
            "I don't recognize that command yet. Try saying 'help' to see what I can do, or use 'teach mode' to show me.",
            "Interesting request! I'm always learning. You can teach me new commands using the teach mode feature."
        ]
        
        return random.choice(responses)
    
    def find_similar_commands(self, word):
        """Find similar commands in the database"""
        try:
            self.cursor.execute(
                "SELECT trigger FROM custom_commands WHERE trigger LIKE ?",
                (f"%{word}%",)
            )
            return [row[0] for row in self.cursor.fetchall()]
        except:
            return []
    
    def learn_from_interaction(self, command, response):
        """Learn from user interactions"""
        try:
            # Store the interaction
            self.cursor.execute(
                "INSERT INTO conversation_memory (user_input, tetris_response, context, importance_score) VALUES (?, ?, ?, ?)",
                (command, response, "normal", 1)
            )
            
            # Extract patterns
            words = command.split()
            if len(words) > 2:
                pattern = ' '.join(words[:2])  # First two words as pattern
                
                # Check if pattern exists
                self.cursor.execute(
                    "SELECT id, success_rate, usage_count FROM learned_patterns WHERE pattern = ?",
                    (pattern,)
                )
                existing = self.cursor.fetchone()
                
                if existing:
                    # Update existing pattern
                    new_usage = existing[2] + 1
                    new_success_rate = (existing[1] * existing[2] + 1) / new_usage
                    
                    self.cursor.execute(
                        "UPDATE learned_patterns SET success_rate = ?, usage_count = ? WHERE id = ?",
                        (new_success_rate, new_usage, existing[0])
                    )
                else:
                    # Create new pattern
                    self.cursor.execute(
                        "INSERT INTO learned_patterns (pattern, response_template, confidence_score, success_rate, usage_count) VALUES (?, ?, ?, ?, ?)",
                        (pattern, response, 0.5, 1.0, 1)
                    )
            
            self.conn.commit()
        except Exception as e:
            print(f"Learning error: {e}")
    
    def store_conversation(self, user_input, tetris_response):
        """Store conversation in memory"""
        try:
            if user_input or tetris_response:
                self.cursor.execute(
                    "INSERT INTO conversation_memory (user_input, tetris_response, context) VALUES (?, ?, ?)",
                    (user_input, tetris_response, "chat")
                )
                self.conn.commit()
        except Exception as e:
            print(f"Memory storage error: {e}")
    
    def load_user_preferences(self):
        """Load user preferences from database"""
        try:
            self.cursor.execute("SELECT key, value FROM user_preferences")
            return dict(self.cursor.fetchall())
        except:
            return {}
    
    def save_user_preference(self, key, value):
        """Save user preference to database"""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.conn.commit()
            self.user_preferences[key] = value
        except Exception as e:
            print(f"Preference save error: {e}")
    
    def on_key_release(self, event):
        """Handle key release for autocomplete suggestions"""
        current_text = self.input_entry.get().lower()
        if len(current_text) > 2:
            suggestions = self.get_command_suggestions(current_text)
            if suggestions:
                self.suggestion_var.set(f"Suggestions: {', '.join(suggestions[:3])}")
            else:
                self.suggestion_var.set("")
        else:
            self.suggestion_var.set("")
    
    def get_command_suggestions(self, partial_command):
        """Get command suggestions based on partial input"""
        suggestions = []
        
        # Common commands
        common_commands = [
            "open calculator", "open notepad", "system status", "what time is it",
            "search for", "play music", "tell a joke", "weather forecast",
            "shutdown computer", "lock screen", "create folder", "help"
        ]
        
        # Find matching commands
        for cmd in common_commands:
            if cmd.startswith(partial_command):
                suggestions.append(cmd)
        
        # Add custom commands
        for trigger in self.custom_commands.keys():
            if trigger.startswith(partial_command):
                suggestions.append(trigger)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def remove_wake_words(self, command):
        """Remove wake words from command"""
        wake_words = ['tetris', 'friday', 'edith', 'ai', 'hey', 'ok']
        words = command.split()
        filtered_words = [word for word in words if word.lower() not in wake_words]
        return ' '.join(filtered_words)
    
    # Advanced Features
    def enter_teach_mode(self):
        """Enter teaching mode for custom commands"""
        teach_dialog = TeachModeDialog(self.root, self)
        self.root.wait_window(teach_dialog.dialog)
    
    def add_custom_command(self):
        """Add new custom command"""
        dialog = CustomCommandDialog(self.root, self)
        self.root.wait_window(dialog.dialog)
        self.refresh_command_list()
    
    def edit_custom_command(self):
        """Edit existing custom command"""
        selection = self.command_tree.selection()
        if selection:
            item = self.command_tree.item(selection[0])
            trigger = item['values'][0]
            
            # Get command details
            self.cursor.execute(
                "SELECT response, action_type, parameters FROM custom_commands WHERE trigger = ?",
                (trigger,)
            )
            result = self.cursor.fetchone()
            
            if result:
                dialog = CustomCommandDialog(self.root, self, trigger, result[0], result[1], result[2])
                self.root.wait_window(dialog.dialog)
                self.refresh_command_list()
        else:
            messagebox.showwarning("Selection Required", "Please select a command to edit.")
    
    def delete_custom_command(self):
        """Delete custom command"""
        selection = self.command_tree.selection()
        if selection:
            item = self.command_tree.item(selection[0])
            trigger = item['values'][0]
            
            if messagebox.askyesno("Confirm Delete", f"Delete command '{trigger}'?"):
                try:
                    self.cursor.execute("DELETE FROM custom_commands WHERE trigger = ?", (trigger,))
                    self.conn.commit()
                    
                    # Remove from memory
                    if trigger.lower() in self.custom_commands:
                        del self.custom_commands[trigger.lower()]
                    
                    self.refresh_command_list()
                    self.add_message("T.E.T.R.I.S", f"Custom command '{trigger}' deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete command: {str(e)}")
        else:
            messagebox.showwarning("Selection Required", "Please select a command to delete.")
    
    def refresh_command_list(self):
        """Refresh the command list display"""
        # Clear existing items
        for item in self.command_tree.get_children():
            self.command_tree.delete(item)
        
        # Load commands from database
        try:
            self.cursor.execute(
                "SELECT trigger, action_type, usage_count, last_used FROM custom_commands ORDER BY usage_count DESC"
            )
            
            for row in self.cursor.fetchall():
                trigger, action_type, usage_count, last_used = row
                last_used_str = last_used if last_used else "Never"
                
                self.command_tree.insert("", "end", values=(
                    trigger, action_type, usage_count, last_used_str
                ))
        except Exception as e:
            print(f"Error refreshing command list: {e}")
    
    def export_commands(self):
        """