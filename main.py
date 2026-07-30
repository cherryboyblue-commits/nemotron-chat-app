import os
import threading
from typing import List, Dict, Any

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.metrics import dp, sp
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import OneLineAvatarIconListItem, ILeftBodyTouch, IRightBodyTouch
from kivymd.uix.avatar import ImageLeftWidget
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.recycleview import MDRecycleView
from kivymd.uix.card import MDCard

# Set window size for desktop testing (optional)
Window.size = (400, 700)

KV = '''
<MessageBubble@MDCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(12), dp(8)
    radius: [dp(16), dp(16), dp(16), dp(16)]
    elevation: 1
    md_bg_color: root.bg_color
    
    MDLabel:
        id: msg_label
        text: root.message_text
        adaptive_height: True
        font_size: sp(16)
        color: root.text_color
        markup: True
        text_size: self.width, None

<UserMessageBubble@MessageBubble>:
    bg_color: 0.2, 0.6, 1, 1  # Blue for user
    text_color: 1, 1, 1, 1
    pos_hint: {"right": 1}
    size_hint_x: 0.85

<BotMessageBubble@MessageBubble>:
    bg_color: 0.9, 0.9, 0.9, 1  # Gray for bot
    text_color: 0, 0, 0, 1
    pos_hint: {"x": 0}
    size_hint_x: 0.85

<LoadingBubble@MDCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(40)
    size_hint_x: 0.6
    pos_hint: {"x": 0}
    padding: dp(12), dp(8)
    radius: [dp(16), dp(16), dp(16), dp(16)]
    elevation: 1
    md_bg_color: 0.9, 0.9, 0.9, 1
    
    MDSpinner:
        size_hint: None, None
        size: dp(24), dp(24)
        active: True
        color: 0.2, 0.6, 1, 1

<ChatScreen>:
    orientation: 'vertical'
    md_bg_color: 0.95, 0.95, 0.95, 1
    
    MDTopAppBar:
        id: toolbar
        title: "Nemotron 3 Ultra"
        elevation: 2
        md_bg_color: 0.2, 0.6, 1, 1
        specific_text_color: 1, 1, 1, 1
        right_action_items: [["dots-vertical", lambda x: app.show_menu()]]
    
    MDScrollView:
        id: scroll_view
        do_scroll_x: False
        effect_cls: "ScrollEffect"
        
        MDBoxLayout:
            id: message_container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(16), dp(16)
            spacing: dp(12)
    
    MDBoxLayout:
        size_hint_y: None
        height: dp(70)
        padding: dp(12), dp(8)
        spacing: dp(8)
        md_bg_color: 1, 1, 1, 1
        elevation: 4
        
        MDTextField:
            id: input_field
            hint_text: "Type a message..."
            mode: "fill"
            fill_color: 0.95, 0.95, 0.95, 1
            font_size: sp(16)
            size_hint_x: 0.8
            on_text_validate: app.send_message()
            multiline: False
            max_height: dp(100)
        
        MDRaisedButton:
            id: send_button
            text: "SEND"
            md_bg_color: 0.2, 0.6, 1, 1
            text_color: 1, 1, 1, 1
            font_size: sp(14)
            size_hint_x: 0.2
            on_release: app.send_message()
            disabled: True
'''

class NemotronChatBot:
    def __init__(self, api_key: str = None, model: str = "nemotron-3-ultra"):
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required.")
        
        self.model = model
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.conversation_history: List[Dict[str, str]] = []
    
    def add_system_prompt(self, system_prompt: str):
        self.conversation_history.insert(0, {"role": "system", "content": system_prompt})
    
    def chat(self, user_message: str, temperature: float = 0.7, max_tokens: int = 1024, top_p: float = 0.9) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})
        
        payload = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": False
        }
        
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            bot_response = result["choices"][0]["message"]["content"]
            
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            return bot_response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text}"
            raise Exception(error_msg)
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected response format: {str(e)}")
    
    def clear_history(self, keep_system_prompt: bool = True):
        if keep_system_prompt and self.conversation_history and self.conversation_history[0]["role"] == "system":
            system_prompt = self.conversation_history[0]
            self.conversation_history = [system_prompt]
        else:
            self.conversation_history = []


class ChatScreen(MDBoxLayout):
    pass


class NemotronApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bot = None
        self.loading_bubble = None
        self.message_widgets = []
    
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        Builder.load_string(KV)
        
        # Initialize bot with API key
        API_KEY = "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"
        try:
            self.bot = NemotronChatBot(api_key=API_KEY)
            self.bot.add_system_prompt("You are a helpful, harmless, and honest AI assistant named Nemotron 3 Ultra.")
        except Exception as e:
            print(f"Failed to initialize bot: {e}")
        
        return ChatScreen()
    
    def on_start(self):
        # Focus the input field
        Clock.schedule_once(lambda dt: setattr(self.root.ids.input_field, 'focus', True), 0.5)
        # Bind text change to enable/disable send button
        self.root.ids.input_field.bind(text=self.on_text_change)
    
    def on_text_change(self, instance, value):
        self.root.ids.send_button.disabled = not value.strip()
    
    def send_message(self):
        user_text = self.root.ids.input_field.text.strip()
        if not user_text or not self.bot:
            return
        
        # Clear input
        self.root.ids.input_field.text = ""
        self.root.ids.send_button.disabled = True
        
        # Add user message bubble
        self.add_user_message(user_text)
        
        # Show loading indicator
        self.show_loading()
        
        # Start API call in background thread
        threading.Thread(target=self.get_bot_response, args=(user_text,), daemon=True).start()
    
    def add_user_message(self, text):
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        
        bubble = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),
            padding=(dp(12), dp(8)),
            radius=[dp(16), dp(16), dp(16), dp(16)],
            elevation=1,
            md_bg_color=(0.2, 0.6, 1, 1),
            pos_hint={"right": 1},
            size_hint_x=0.85
        )
        
        label = MDLabel(
            text=text,
            adaptive_height=True,
            font_size=sp(16),
            color=(1, 1, 1, 1),
            markup=True,
            text_size=(None, None)
        )
        bubble.add_widget(label)
        
        # Bind width to update text_size
        def update_text_size(instance, width):
            label.text_size = (width * 0.9, None)
            instance.height = label.height + dp(16)
        
        bubble.bind(width=update_text_size)
        
        self.root.ids.message_container.add_widget(bubble)
        self.scroll_to_bottom()
    
    def add_bot_message(self, text):
        from kivymd.uix.card import MDCard
        from kivymd.uix.label import MDLabel
        
        bubble = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),
            padding=(dp(12), dp(8)),
            radius=[dp(16), dp(16), dp(16), dp(16)],
            elevation=1,
            md_bg_color=(0.9, 0.9, 0.9, 1),
            pos_hint={"x": 0},
            size_hint_x=0.85
        )
        
        label = MDLabel(
            text=text,
            adaptive_height=True,
            font_size=sp(16),
            color=(0, 0, 0, 1),
            markup=True,
            text_size=(None, None)
        )
        bubble.add_widget(label)
        
        def update_text_size(instance, width):
            label.text_size = (width * 0.9, None)
            instance.height = label.height + dp(16)
        
        bubble.bind(width=update_text_size)
        
        self.root.ids.message_container.add_widget(bubble)
        self.scroll_to_bottom()
    
    def show_loading(self):
        from kivymd.uix.card import MDCard
        from kivymd.uix.spinner import MDSpinner
        
        self.loading_bubble = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            size_hint_x=0.6,
            pos_hint={"x": 0},
            padding=(dp(12), dp(8)),
            radius=[dp(16), dp(16), dp(16), dp(16)],
            elevation=1,
            md_bg_color=(0.9, 0.9, 0.9, 1)
        )
        
        spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            active=True,
            color=(0.2, 0.6, 1, 1)
        )
        self.loading_bubble.add_widget(spinner)
        
        self.root.ids.message_container.add_widget(self.loading_bubble)
        self.scroll_to_bottom()
    
    def hide_loading(self):
        if self.loading_bubble and self.loading_bubble.parent:
            self.root.ids.message_container.remove_widget(self.loading_bubble)
            self.loading_bubble = None
    
    def get_bot_response(self, user_message):
        try:
            response = self.bot.chat(user_message)
            # Schedule UI update on main thread
            Clock.schedule_once(lambda dt: self.on_bot_response(response), 0)
        except Exception as e:
            # Capture exception in default argument to avoid closure issue
            Clock.schedule_once(lambda dt, err=e: self.on_bot_error(str(err)), 0)
    
    def on_bot_response(self, response):
        self.hide_loading()
        self.add_bot_message(response)
    
    def on_bot_error(self, error_msg):
        self.hide_loading()
        self.add_bot_message(f"[color=#FF0000]Error: {error_msg}[/color]")
    
    def scroll_to_bottom(self):
        def _scroll(dt):
            scroll_view = self.root.ids.scroll_view
            if scroll_view:
                scroll_view.scroll_y = 0
        Clock.schedule_once(_scroll, 0.1)
    
    def show_menu(self):
        # Simple menu implementation
        from kivymd.uix.menu import MDDropdownMenu
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.dialog import MDDialog
        
        menu_items = [
            {
                "text": "Clear History",
                "on_release": lambda: self.clear_history(),
            },
            {
                "text": "About",
                "on_release": lambda: self.show_about(),
            }
        ]
        
        self.menu = MDDropdownMenu(
            caller=self.root.ids.toolbar,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()
    
    def clear_history(self):
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        if self.bot:
            self.bot.clear_history()
        # Clear message container except keep system prompt if any
        container = self.root.ids.message_container
        container.clear_widgets()
        self.add_bot_message("Conversation history cleared. How can I help you?")
    
    def show_about(self):
        if hasattr(self, 'menu'):
            self.menu.dismiss()
        
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        dialog = MDDialog(
            title="About Nemotron 3 Ultra",
            text="Powered by NVIDIA Nemotron 3 Ultra API\n\nA mobile chat interface for Nemotron 3 Ultra 550B model.",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()


if __name__ == "__main__":
    NemotronApp().run()
