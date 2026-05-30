import json
import os
import hashlib
import hmac
import math
import sqlite3
import uuid
from copy import deepcopy

os.environ.setdefault("KIVY_NO_FILELOG", "1")

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color, InstructionGroup, Rectangle
from kivy.graphics.texture import Texture
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, DictProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.resources import resource_find
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.utils import platform

if platform not in ("android", "ios"):
    Config.set("input", "mouse", "mouse,multitouch_on_demand")
else:
    Config.set("kivy", "keyboard_mode", "system")

from kivy.core.window import Window

Window.clearcolor = (0.961, 0.937, 0.878, 1)
Window.softinput_mode = "pan"


KV = """
#:import dp kivy.metrics.dp

<RoundedCard@BoxLayout>:
    orientation: "vertical"
    padding: dp(18)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: app.colors["shadow_strong"]
        RoundedRectangle:
            pos: self.x, self.y - dp(10)
            size: self.size
            radius: [28, 28, 28, 28]
        Color:
            rgba: app.colors["card"]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [28, 28, 28, 28]
        Color:
            rgba: app.colors["pink_gloss"]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [28, 28, 28, 28]
            texture: app.metallic_pink_texture
        Color:
            rgba: 1, 1, 1, 0.2
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [28, 28, 28, 28]
            texture: app.surface_glow_texture
        Color:
            rgba: app.colors["outline"]
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 28]
            width: 1.35
        Color:
            rgba: app.colors["cream"][0], app.colors["cream"][1], app.colors["cream"][2], 0.55
        Line:
            rounded_rectangle: [self.x + dp(1.6), self.y + dp(1.6), self.width - dp(3.2), self.height - dp(3.2), 26.4]
            width: 1.15

<PageTitle@Label>:
    color: app.colors["text"]
    font_name: app.title_font
    font_size: "28sp"
    size_hint_y: None
    height: self.texture_size[1] + dp(2)
    halign: "left"
    valign: "middle"
    text_size: self.width, None

<SectionTitle@Label>:
    color: app.colors["text"]
    font_name: app.title_font
    font_size: "20sp"
    size_hint_y: None
    height: self.texture_size[1] + dp(2)
    halign: "left"
    valign: "middle"
    text_size: self.width, None

<BodyLabel@ShadowLabel>:
    color: app.colors["text_muted"]
    font_name: app.body_font
    font_size: "15sp"
    halign: "left"
    valign: "middle"
    text_size: self.width, None
    size_hint_y: None
    height: self.texture_size[1] + dp(2)

<PrimaryButton>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: 1, 1, 1, 1
    font_name: app.body_font
    font_size: "16sp"
    size_hint_y: None
    height: dp(54)
    base_color: app.colors["green_button"]
    rest_lift: dp(0)
    text_lift: self.rest_lift
    corner_radius: dp(27)
    canvas.before:
        PushMatrix
        Translate:
            x: 0
            y: self.text_lift
        Scale:
            origin: self.center_x, self.center_y
            x: self.press_scale
            y: self.press_scale
            z: 1
        Color:
            rgba: self.base_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
        Color:
            rgba: 1, 1, 1, 0.12
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
            texture: app.button_gloss_texture
        Color:
            rgba: 1, 1, 1, 0.1
        Line:
            rounded_rectangle: [self.x + dp(2), self.y + dp(2), self.width - dp(4), self.height - dp(4), self.corner_radius - dp(2)]
            width: 1.05
        Color:
            rgba: 0.08, 0.2, 0.1, 0.08
        Line:
            rounded_rectangle: [self.x + dp(1.5), self.y + dp(1.5), self.width - dp(3), self.height - dp(3), self.corner_radius - dp(1.5)]
            width: 0.8
        Color:
            rgba: self.overlay_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
    canvas.after:
        PopMatrix

<SecondaryButton>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: app.colors["text"]
    font_name: app.body_font
    font_size: "15sp"
    size_hint_y: None
    height: dp(50)
    base_color: app.colors["pink_soft"]
    rest_lift: dp(0)
    text_lift: self.rest_lift
    corner_radius: dp(25)
    canvas.before:
        PushMatrix
        Translate:
            x: 0
            y: self.text_lift
        Scale:
            origin: self.center_x, self.center_y
            x: self.press_scale
            y: self.press_scale
            z: 1
        Color:
            rgba: self.base_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
        Color:
            rgba: 1, 1, 1, 0.18
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
            texture: app.button_gloss_texture
        Color:
            rgba: app.colors["pink_main"][0], app.colors["pink_main"][1], app.colors["pink_main"][2], 0.38
        Line:
            rounded_rectangle: [self.x + dp(2), self.y + dp(2), self.width - dp(4), self.height - dp(4), self.corner_radius - dp(2)]
            width: 1.0
        Color:
            rgba: 1, 1, 1, 0.34
        Line:
            rounded_rectangle: [self.x + dp(1.5), self.y + dp(1.5), self.width - dp(3), self.height - dp(3), self.corner_radius - dp(1.5)]
            width: 0.7
        Color:
            rgba: self.overlay_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
    canvas.after:
        PopMatrix

<AccentButton>:
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: 0.420, 0.353, 0.306, 1
    font_name: app.body_font
    font_size: "15sp"
    size_hint_y: None
    height: dp(48)
    base_color: 0.859, 0.667, 0.733, 1
    rest_lift: dp(0)
    text_lift: self.rest_lift
    corner_radius: dp(24)
    canvas.before:
        PushMatrix
        Translate:
            x: 0
            y: self.text_lift
        Scale:
            origin: self.center_x, self.center_y
            x: self.press_scale
            y: self.press_scale
            z: 1
        Color:
            rgba: self.base_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
        Color:
            rgba: 0.420, 0.353, 0.306, 0.25
        Line:
            rounded_rectangle: [self.x + dp(2), self.y + dp(2), self.width - dp(4), self.height - dp(4), self.corner_radius - dp(2)]
            width: 1.0
        Color:
            rgba: self.overlay_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.corner_radius] * 4
    canvas.after:
        PopMatrix

<ChoiceChip>:
    selected_color: app.colors["green_main"]
    background_color: 0, 0, 0, 0
    background_normal: ""
    background_down: ""
    color: app.colors["text"]
    font_name: app.body_font
    size_hint_y: None
    height: dp(44)
    canvas.before:
        PushMatrix
        Translate:
            x: 0
            y: self.text_lift
        Scale:
            origin: self.center_x, self.center_y
            x: self.press_scale
            y: self.press_scale
            z: 1
        Color:
            rgba: self.selected_color if self.state == "down" else app.colors["card"]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20, 20, 20, 20]
        Color:
            rgba: self.selected_outline if self.state == "down" else app.colors["outline"]
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 20]
            width: 1.1
        Color:
            rgba: self.overlay_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20, 20, 20, 20]
    canvas.after:
        PopMatrix

<GenderChip@ChoiceChip>:
    selected_color: app.colors["green_main"]

<SoftInput>:
    multiline: False
    background_normal: ""
    background_active: ""
    background_color: 0, 0, 0, 0
    foreground_color: 0.0, 0.0, 0.0, 1
    disabled_foreground_color: 0.0, 0.0, 0.0, 1
    cursor_color: 0.0, 0.0, 0.0, 1
    cursor_width: dp(2)
    hint_text_color: app.colors["text_muted"]
    selection_color: 0.76, 0.88, 0.78, 0.45
    padding: [dp(16), dp(14), dp(16), dp(14)]
    font_name: app.body_font
    font_size: "15sp"
    size_hint_y: None
    height: dp(52)
    canvas.before:
        Color:
            rgba: app.colors["card"]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20, 20, 20, 20]
        Color:
            rgba: 1, 1, 1, 0.2
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20, 20, 20, 20]
            texture: app.surface_glow_texture
        Color:
            rgba: app.colors["outline"]
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 20]
            width: 1.35

<ProgressTrack@Widget>:
    progress: 0
    fill_color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: app.colors["outline"]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2] * 4
        Color:
            rgba: self.fill_color
        RoundedRectangle:
            pos: self.pos
            size: self.width * min(1, max(0, self.progress)), self.height
            radius: [self.height / 2] * 4

<ShoppingItemCard>:
    size_hint_y: None
    height: self.minimum_height
    orientation: "vertical"
    padding: dp(12)
    spacing: dp(6)
    canvas.before:
        Color:
            rgba: root.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [24, 24, 24, 24]
    BoxLayout:
        size_hint_y: None
        height: max(item_name_label.texture_size[1] + dp(2), dp(24))
        spacing: dp(8)
        AnchorLayout:
            size_hint: None, None
            size: dp(28), dp(28)
            anchor_x: "center"
            anchor_y: "center"
            canvas.before:
                Color:
                    rgba: 0.961, 0.937, 0.878, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [8, 8, 8, 8]
                Color:
                    rgba: 0.859, 0.667, 0.733, 1
                Line:
                    rounded_rectangle: [self.x, self.y, self.width, self.height, 8]
                    width: 1.2
            CheckBox:
                size_hint: None, None
                size: dp(24), dp(24)
                active: root.checked
                on_active: root.toggle_checked(self.active)
                color: 0.541, 0.549, 0.353, 1
        Label:
            id: item_name_label
            text: root.item_name
            color: app.colors["text"]
            font_name: app.title_font
            font_size: "18sp"
            halign: "left"
            valign: "middle"
            text_size: self.width, None
    Label:
        text: root.category_label
        size_hint: None, None
        size: dp(108), dp(36)
        color: 0.961, 0.937, 0.878, 1
        font_name: app.body_font
        halign: "center"
        valign: "middle"
        text_size: self.size
        canvas.before:
            Color:
                rgba: root.badge_color
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [18, 18, 18, 18]
    Label:
        text: root.helper_text
        color: app.colors["text_muted"]
        font_name: app.body_font
        font_size: "13sp"
        halign: "left"
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1] + dp(2)
    SoftInput:
        id: price_input
        hint_text: "Item price"
        text: root.price_text
        input_filter: "float"
        on_text_validate: root.save_price(self.text)
    PrimaryButton:
        text: "Save Price"
        size_hint_y: None
        height: dp(42)
        on_release: root.save_price(price_input.text)

<PastelInfoCard@BoxLayout>:
    card_color: 1, 1, 1, 1
    orientation: "vertical"
    padding: dp(16)
    spacing: dp(8)
    size_hint_y: None
    height: self.minimum_height + dp(6)
    canvas.before:
        Color:
            rgba: self.card_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [24, 24, 24, 24]
        Color:
            rgba: 1, 1, 1, 0.22
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [24, 24, 24, 24]
            texture: app.surface_glow_texture

<BrandTitle@Label>:
    color: app.colors["text"]
    font_name: app.title_font
    halign: "left"
    valign: "middle"
    text_size: self.width, None
    size_hint_y: None
    height: self.texture_size[1] + dp(6)

<SplashScreen>:
    name: "splash"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.bg_texture
            Color:
                rgba: 1, 1, 1, 0.12
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        canvas.after:
            Color:
                rgba: 1, 1, 1, 0.18
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        BoxLayout:
            orientation: "vertical"
            spacing: dp(8)
            padding: [dp(24), dp(22), dp(24), dp(22)]
            size_hint: 0.88, None
            height: dp(438)
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            canvas.before:
                Color:
                    rgba: app.colors["shadow"]
                RoundedRectangle:
                    pos: self.x, self.y - dp(8)
                    size: self.size
                    radius: [36, 36, 36, 36]
                Color:
                    rgba: app.colors["card"]
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [36, 36, 36, 36]
                Color:
                    rgba: app.colors["outline"]
                Line:
                    rounded_rectangle: [self.x, self.y, self.width, self.height, 36]
                    width: 1
            Widget:
                size_hint_y: None
                height: dp(60)
            Image:
                source: app.splash_logo
                size_hint: None, None
                size: dp(248), dp(248)
                pos_hint: {"center_x": 0.5}
                allow_stretch: True
                keep_ratio: True
            Widget:
                size_hint_y: None
                height: dp(-22)
            BrandTitle:
                text: "Essentia"
                font_size: "38sp"
                halign: "center"
                text_size: self.width - dp(12), None
                height: self.texture_size[1]
            Label:
                text: "Grocery buddy"
                color: app.colors["text_muted"]
                font_name: app.body_font
                font_size: "17sp"
                size_hint_y: None
                height: dp(24)
            Widget:
                size_hint_y: None
                height: dp(48)
            Label:
                text: "Buy the must-haves first."
                color: app.colors["text"]
                font_name: app.body_font
                font_size: "15sp"
                size_hint_y: None
                height: dp(22)
            ProgressTrack:
                size_hint_y: None
                height: dp(10)
                progress: 0.72
                fill_color: app.colors["green_main"]
            BodyLabel:
                text: "Loading your shopping flow..."
                halign: "center"
                text_size: self.width, None

<LoginScreen>:
    name: "login"
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            texture: app.bg_texture
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: max(self.minimum_height, self.parent.height if self.parent else 0)
            padding: [dp(32), dp(0), dp(32), dp(40)]
            spacing: dp(0)
            Widget:
                size_hint_y: 1
            Label:
                text: "Sign in"
                color: app.colors["text"]
                font_name: app.title_font
                font_size: "34sp"
                size_hint_y: None
                height: self.texture_size[1]
                halign: "left"
                text_size: self.width, None
            Widget:
                size_hint_y: None
                height: dp(6)
            Label:
                text: "Good to see you again."
                color: app.colors["text_muted"]
                font_name: app.body_font
                font_size: "15sp"
                size_hint_y: None
                height: self.texture_size[1]
                halign: "left"
                text_size: self.width, None
            Widget:
                size_hint_y: None
                height: dp(32)
            SoftInput:
                id: login_username
                hint_text: "Username"
            Widget:
                size_hint_y: None
                height: dp(12)
            SoftInput:
                id: login_password
                hint_text: "Password"
                password: True
            Label:
                id: login_message
                text: ""
                color: app.colors["danger"]
                font_name: app.body_font
                font_size: "13sp"
                text_size: self.width, None
                halign: "left"
                size_hint_y: None
                height: self.texture_size[1] + dp(4)
            Widget:
                size_hint_y: None
                height: dp(20)
            PrimaryButton:
                text: "Log In"
                on_release: root.login(login_username.text, login_password.text)
            Widget:
                size_hint_y: None
                height: dp(16)
            BoxLayout:
                size_hint_y: None
                height: dp(36)
                Label:
                    text: "New User?  "
                    color: app.colors["text_muted"]
                    font_name: app.body_font
                    font_size: "14sp"
                    halign: "right"
                    valign: "middle"
                    text_size: self.size
                Label:
                    text: "[ref=s][u]Create Account[/u][/ref]"
                    markup: True
                    color: app.colors["pink_main"]
                    font_name: app.title_font
                    font_size: "14sp"
                    halign: "left"
                    valign: "middle"
                    text_size: self.size
                    on_ref_press: app.go_to("signup")

<SignupScreen>:
    name: "signup"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.bg_texture
            Color:
                rgba: 1, 1, 1, 0.12
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        canvas.after:
            Color:
                rgba: 1, 1, 1, 0.16
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        ScrollView:
            do_scroll_x: False
            size_hint: 1, 1
            BoxLayout:
                orientation: "vertical"
                spacing: dp(18)
                size_hint_y: None
                height: max(self.minimum_height, self.parent.height if self.parent else 0)
                padding: [dp(22), dp(26), dp(22), dp(28)]
                canvas.before:
                RoundedCard:
                    size_hint_y: None
                    height: dp(720)
                    canvas.before:
                        Color:
                            rgba: app.colors["card"]
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [34, 34, 34, 34]
                    BoxLayout:
                        orientation: "vertical" if self.width < dp(520) else "horizontal"
                        spacing: dp(14)
                        size_hint_y: None
                        height: self.minimum_height
                        BoxLayout:
                            orientation: "vertical"
                            spacing: dp(8)
                            size_hint_y: None
                            height: self.minimum_height
                            BrandTitle:
                                text: "Essentia"
                                font_size: "40sp"
                                halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                            BodyLabel:
                                text: "Create your account and keep your list saved."
                                halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                            Widget:
                        Image:
                            source: app.signup_image
                            allow_stretch: True
                            keep_ratio: True
                            size_hint: None, None
                            size: (dp(146), dp(146)) if self.parent.orientation == "horizontal" else (dp(172), dp(172))
                            pos_hint: {"center_x": 0.5}
                    SoftInput:
                        id: signup_name
                        hint_text: "Name"
                    SoftInput:
                        id: signup_birthday
                        hint_text: "Birthday"
                    Label:
                        text: "Gender"
                        color: app.colors["text"]
                        font_name: app.title_font
                        font_size: "18sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                        halign: "left"
                        text_size: self.width, None
                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)
                        BoxLayout:
                            size_hint_y: None
                            height: dp(44)
                            spacing: dp(8)
                            GenderChip:
                                id: signup_gender_female
                                text: "Female"
                                group: "signup_gender"
                                state: "down"
                                selected_color: 0.878, 0.502, 0.565, 0.50
                            GenderChip:
                                id: signup_gender_male
                                text: "Male"
                                group: "signup_gender"
                                selected_color: 0.541, 0.549, 0.353, 0.50
                        GenderChip:
                            id: signup_gender_skip
                            text: "Prefer not to say"
                            group: "signup_gender"
                            size_hint_y: None
                            height: dp(44)
                            selected_color: app.colors["green_soft"]
                    SoftInput:
                        id: signup_username
                        hint_text: "Username"
                    SoftInput:
                        id: signup_password
                        hint_text: "Password"
                        password: True
                    Label:
                        id: signup_message
                        text: ""
                        color: app.colors["danger"]
                        font_name: app.body_font
                        text_size: self.width, None
                        halign: "left"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                    PrimaryButton:
                        text: "Create Account"
                        on_release:
                            root.signup(
                            signup_name.text,
                            signup_birthday.text,
                            "Female" if signup_gender_female.state == "down" else "Male" if signup_gender_male.state == "down" else "Prefer not to say",
                            signup_username.text,
                            signup_password.text
                            )
                    SecondaryButton:
                        text: "Back to Login"
                        on_release: app.go_to("login")

<HomeScreen>:
    name: "home"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.bg_texture
            Color:
                rgba: 1, 1, 1, 0.12
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        canvas.after:
            Color:
                rgba: 1, 1, 1, 0.16
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        ScrollView:
            do_scroll_x: False
            size_hint: 1, 1
            BoxLayout:
                orientation: "vertical"
                spacing: dp(18)
                size_hint_y: None
                height: max(self.minimum_height, self.parent.height if self.parent else 0)
                padding: [dp(22), dp(10), dp(22), dp(30)]
                BoxLayout:
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(10)
                    AccentButton:
                        text: "Settings"
                        size_hint_x: None
                        width: dp(118)
                        on_release: app.open_settings_menu()
                    Widget:
                RoundedCard:
                    size_hint_y: None
                    height: self.minimum_height + dp(20)
                    canvas.before:
                        Color:
                            rgba: app.colors["green_main"]
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [30, 30, 30, 30]
                    BoxLayout:
                        orientation: "vertical" if self.width < dp(520) else "horizontal"
                        spacing: dp(14)
                        size_hint_y: None
                        height: self.minimum_height
                        BoxLayout:
                            orientation: "vertical"
                            spacing: dp(8)
                            size_hint_y: None
                            height: self.minimum_height
                            BrandTitle:
                                text: "Essentia"
                                font_size: "40sp"
                                halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                                color: 0.961, 0.937, 0.878, 1
                            Label:
                                id: home_greeting
                                text: "Hi, " + app.profile.get("display_name", "Shopper") + "!"
                                color: 0.961, 0.937, 0.878, 1
                                font_name: app.title_font
                                font_size: "22sp"
                                size_hint_y: None
                                height: self.texture_size[1] + dp(2)
                                halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                                text_size: self.width, None
                            BodyLabel:
                                text: "Keep your must-buys on top."
                                halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                                color: 0.961, 0.937, 0.878, 0.80
                            Widget:
                        Image:
                            source: app.hero_image
                            allow_stretch: True
                            keep_ratio: True
                            size_hint: None, None
                            size: (dp(196), dp(196)) if self.parent.orientation == "horizontal" else (dp(210), dp(210))
                            pos_hint: {"center_x": 0.5}
                RoundedCard:
                    size_hint_y: None
                    height: self.minimum_height + dp(24)
                    SectionTitle:
                        text: "Home"
                    BodyLabel:
                        text: "Make a list or start shopping."
                    PrimaryButton:
                        text: "Create List"
                        on_release: app.go_to("create_list")
                    SecondaryButton:
                        text: "Start Shopping"
                        on_release: app.go_to("current_list")

<ProfileScreen>:
    name: "profile"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.bg_texture
            Color:
                rgba: 1, 1, 1, 0.12
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        canvas.after:
            Color:
                rgba: 1, 1, 1, 0.16
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        ScrollView:
            do_scroll_x: False
            size_hint: 1, 1
            BoxLayout:
                orientation: "vertical"
                spacing: dp(18)
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(22), dp(24), dp(22), dp(28)]
                canvas.before:
                BoxLayout:
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(10)
                    AccentButton:
                        text: "Back"
                        size_hint_x: None
                        width: dp(96)
                        on_release: app.go_to("home")
                    Widget:
                RoundedCard:
                    size_hint_y: None
                    height: self.minimum_height + dp(6)
                    PageTitle:
                        text: "Profile"
                    SoftInput:
                        id: profile_name
                        hint_text: "Name"
                        text: ""
                    SoftInput:
                        id: profile_birthday
                        hint_text: "Birthday"
                        text: ""
                    Label:
                        text: "Gender"
                        color: app.colors["text"]
                        font_name: app.title_font
                        font_size: "18sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                        halign: "left"
                        text_size: self.width, None
                    BoxLayout:
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)
                        BoxLayout:
                            size_hint_y: None
                            height: dp(44)
                            spacing: dp(8)
                            GenderChip:
                                id: profile_gender_female
                                text: "Female"
                                group: "profile_gender"
                                selected_color: 0.878, 0.502, 0.565, 0.50
                            GenderChip:
                                id: profile_gender_male
                                text: "Male"
                                group: "profile_gender"
                                selected_color: 0.541, 0.549, 0.353, 0.50
                        GenderChip:
                            id: profile_gender_skip
                            text: "Prefer not to say"
                            group: "profile_gender"
                            size_hint_y: None
                            height: dp(44)
                            selected_color: app.colors["green_soft"]
                    SoftInput:
                        id: profile_username
                        hint_text: "Username"
                        text: ""
                    SoftInput:
                        id: profile_password
                        hint_text: "New password (optional)"
                        text: ""
                        password: True
                        text: ""
                    Label:
                        id: profile_message
                        text: ""
                        color: app.colors["danger"]
                        font_name: app.body_font
                        text_size: self.width, None
                        halign: "left"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                    PrimaryButton:
                        text: "Save"
                        on_release:
                            root.save_profile(
                            profile_name.text,
                            profile_birthday.text,
                            "Female" if profile_gender_female.state == "down" else "Male" if profile_gender_male.state == "down" else "Prefer not to say",
                            profile_username.text,
                            profile_password.text
                            )

<AboutScreen>:
    name: "about"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.bg_texture
            Color:
                rgba: 1, 1, 1, 0.12
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        canvas.after:
            Color:
                rgba: 1, 1, 1, 0.16
            Rectangle:
                pos: self.pos
                size: self.size
                texture: app.surface_glow_texture
        ScrollView:
            do_scroll_x: False
            size_hint: 1, 1
            BoxLayout:
                orientation: "vertical"
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height
                padding: [dp(22), dp(42), dp(22), dp(30)]
                BoxLayout:
                    size_hint_y: None
                    height: dp(48)
                    spacing: dp(10)
                    AccentButton:
                        text: "Back"
                        size_hint_x: None
                        width: dp(96)
                        on_release: app.go_to("home")
                    Widget:
                PastelInfoCard:
                    card_color: 0.878, 0.502, 0.565, 1
                    size_hint_y: None
                    height: self.minimum_height + dp(14)
                    Label:
                        text: "About Essentia"
                        color: 0.961, 0.937, 0.878, 1
                        font_name: app.title_font
                        font_size: "28sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                        halign: "left"
                        text_size: self.width, None
                    BodyLabel:
                        text: "Keeping track of groceries can feel messy, especially when some items matter more than others. This app helps organize your shopping list by separating important items from less urgent ones."
                        color: 0.961, 0.937, 0.878, 1
                PastelInfoCard:
                    card_color: 0.541, 0.549, 0.353, 1
                    Label:
                        text: "How the System Works"
                        color: 0.961, 0.937, 0.878, 1
                        font_name: app.title_font
                        font_size: "18sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                        halign: "left"
                        text_size: self.width, None
                    BodyLabel:
                        text: "The app sorts every grocery item into two groups: Essential and Optional. Essential items are the things you truly need, such as daily food or household basics, while optional items are extra things you may want but can live without. This gives your shopping list a clearer structure instead of one long confusing list."
                        color: 0.961, 0.937, 0.878, 1
                PastelInfoCard:
                    card_color: 0.859, 0.667, 0.733, 1
                    Label:
                        text: "Managing Essential Items"
                        color: 0.420, 0.353, 0.306, 1
                        font_name: app.title_font
                        font_size: "18sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                        halign: "left"
                        text_size: self.width, None
                    BodyLabel:
                        text: "Items in the Essential section are handled using a queue system. This means the first item you add will also be the first item removed. It works well because your most important groceries stay in the order you originally planned, helping you keep track of the items that should be handled first."
                        color: 0.420, 0.353, 0.306, 1
                PastelInfoCard:
                    card_color: 0.420, 0.353, 0.306, 1
                    Label:
                        text: "Handling Optional Items"
                        color: 0.961, 0.937, 0.878, 1
                        font_name: app.title_font
                        font_size: "18sp"
                        size_hint_y: None
                        height: self.texture_size[1] + dp(2)
                        halign: "left"
                        text_size: self.width, None
                    BodyLabel:
                        text: "Optional items are managed using a stack system, which means the last item you add becomes the first one removed. This makes optional groceries easier to change because extra items often change quickly. If you decide you no longer need something, the newest optional item can be removed first without affecting the rest of your list."
                        color: 0.961, 0.937, 0.878, 1
<CreateListScreen>:
    name: "create_list"
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: "vertical"
            spacing: dp(18)
            size_hint_y: None
            height: max(self.minimum_height, self.parent.height if self.parent else 0)
            padding: [dp(22), dp(24), dp(22), dp(30)]
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
                    texture: app.bg_texture
                Color:
                    rgba: 1, 1, 1, 0.12
                Rectangle:
                    pos: self.pos
                    size: self.size
                    texture: app.surface_glow_texture
            canvas.after:
                Color:
                    rgba: 1, 1, 1, 0.16
                Rectangle:
                    pos: self.pos
                    size: self.size
                    texture: app.surface_glow_texture
            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(10)
                AccentButton:
                    text: "Back"
                    size_hint_x: None
                    width: dp(96)
                    on_release: app.go_to("home")
                Widget:
            RoundedCard:
                size_hint_y: None
                height: self.minimum_height + dp(20)
                BoxLayout:
                    orientation: "vertical" if self.width < dp(520) else "horizontal"
                    spacing: dp(14)
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: "vertical"
                        spacing: dp(8)
                        size_hint_y: None
                        height: self.minimum_height
                        PageTitle:
                            text: "Create List"
                            halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                        BodyLabel:
                            text: "Add items, then sort them as essential or optional."
                            halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                        Widget:
                    Image:
                        source: app.draft_image
                        allow_stretch: True
                        keep_ratio: True
                        size_hint: None, None
                        size: (dp(182), dp(136)) if self.parent.orientation == "horizontal" else (dp(210), dp(158))
                        pos_hint: {"center_x": 0.5}
                SoftInput:
                    id: item_input
                    hint_text: "Add grocery item"
                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(10)
                    ChoiceChip:
                        id: essential_choice
                        text: "Essential"
                        group: "list_category"
                        state: "down"
                        selected_color: app.colors["green_main"]
                    ChoiceChip:
                        id: optional_choice
                        text: "Optional"
                        group: "list_category"
                        selected_color: 0.541, 0.549, 0.353, 0.50
                BoxLayout:
                    size_hint_y: None
                    height: dp(52)
                    spacing: dp(10)
                    PrimaryButton:
                        text: "Add to List"
                        on_release:
                            root.add_item(
                            item_input.text,
                            "essential" if essential_choice.state == "down" else "optional"
                            )
                    SecondaryButton:
                        text: "Remove"
                        on_release:
                            root.remove_item("essential" if essential_choice.state == "down" else "optional")
                Label:
                    id: create_message
                    text: ""
                    color: app.colors["text_muted"]
                    font_name: app.body_font
                    text_size: self.width, None
                    halign: "left"
                    size_hint_y: None
                    height: self.texture_size[1] + dp(2)
            RoundedCard:
                size_hint_y: None
                height: self.minimum_height + dp(8)
                canvas.before:
                    Color:
                        rgba: app.colors["cream"]
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [28, 28, 28, 28]
                SectionTitle:
                    text: "Current Draft"
                BoxLayout:
                    size_hint_y: None
                    height: max(essential_card.height, optional_card.height)
                    spacing: dp(12)
                    RoundedCard:
                        id: essential_card
                        size_hint_y: None
                        height: self.minimum_height + dp(8)
                        canvas.before:
                            Color:
                                rgba: app.colors["green_soft"]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [24, 24, 24, 24]
                        Label:
                            text: "Essential"
                            color: app.colors["text"]
                            font_name: app.title_font
                            size_hint_y: None
                            height: self.texture_size[1] + dp(2)
                        Label:
                            text: app.essential_draft_text
                            color: app.colors["text"]
                            font_name: app.body_font
                            halign: "left"
                            valign: "top"
                            text_size: self.width, None
                            size_hint_y: None
                            height: self.texture_size[1] + dp(2)
                    RoundedCard:
                        id: optional_card
                        size_hint_y: None
                        height: self.minimum_height + dp(8)
                        canvas.before:
                            Color:
                                rgba: app.colors["green_alt_soft"]
                            RoundedRectangle:
                                pos: self.pos
                                size: self.size
                                radius: [24, 24, 24, 24]
                        Label:
                            text: "Optional"
                            color: app.colors["text"]
                            font_name: app.title_font
                            size_hint_y: None
                            height: self.texture_size[1] + dp(2)
                        Label:
                            text: app.optional_draft_text
                            color: app.colors["text"]
                            font_name: app.body_font
                            halign: "left"
                            valign: "top"
                            text_size: self.width, None
                            size_hint_y: None
                            height: self.texture_size[1] + dp(2)

<CurrentListScreen>:
    name: "current_list"
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: "vertical"
            spacing: dp(18)
            size_hint_y: None
            height: max(self.minimum_height, self.parent.height if self.parent else 0)
            padding: [dp(22), dp(24), dp(22), dp(30)]
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
                    texture: app.bg_texture
                Color:
                    rgba: 1, 1, 1, 0.12
                Rectangle:
                    pos: self.pos
                    size: self.size
                    texture: app.surface_glow_texture
            canvas.after:
                Color:
                    rgba: 1, 1, 1, 0.16
                Rectangle:
                    pos: self.pos
                    size: self.size
                    texture: app.surface_glow_texture
            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(10)
                AccentButton:
                    text: "Back"
                    size_hint_x: None
                    width: dp(96)
                    on_release: app.go_to("home")
                Widget:
            RoundedCard:
                size_hint_y: None
                height: self.minimum_height + dp(20)
                BoxLayout:
                    orientation: "vertical" if self.width < dp(520) else "horizontal"
                    spacing: dp(14)
                    size_hint_y: None
                    height: self.minimum_height
                    BoxLayout:
                        orientation: "vertical"
                        spacing: dp(8)
                        size_hint_y: None
                        height: self.minimum_height
                        PageTitle:
                            text: "Start Shopping"
                            halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                        BodyLabel:
                            text: "Check items, save prices, and watch your budget."
                            halign: "center" if self.parent.parent.orientation == "vertical" else "left"
                        Widget:
                    Image:
                        source: app.summary_image
                        allow_stretch: True
                        keep_ratio: True
                        size_hint: None, None
                        size: (dp(198), dp(134)) if self.parent.orientation == "horizontal" else (dp(226), dp(154))
                        pos_hint: {"center_x": 0.5}
                BoxLayout:
                    size_hint_y: None
                    height: dp(42)
                    spacing: dp(8)
                    SoftInput:
                        id: budget_input
                        hint_text: "Budget"
                        text: app.shopping_data.get("budget_text", "")
                        input_filter: "float"
                    PrimaryButton:
                        text: "Save"
                        size_hint_x: None
                        width: dp(118)
                        on_release: root.save_budget(budget_input.text)
                Label:
                    text: app.budget_summary
                    color: app.colors["text"]
                    font_name: app.body_font
                    halign: "left"
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1] + dp(4)
                ProgressTrack:
                    size_hint_y: None
                    height: dp(16)
                    progress: app.progress_ratio
                    fill_color: app.progress_color
                Label:
                    text: app.progress_caption
                    color: app.colors["text_muted"]
                    font_name: app.body_font
                    halign: "left"
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1] + dp(4)
            RoundedCard:
                size_hint_y: None
                height: self.minimum_height + dp(22)
                SectionTitle:
                    text: "Shopping Checklist"
                BoxLayout:
                    id: item_holder
                    orientation: "vertical"
                    spacing: dp(12)
                    size_hint_y: None
                    height: self.minimum_height
"""


DEFAULT_STATE = {
    "registered": False,
    "profile": {
        "display_name": "",
        "birthday": "",
        "gender": "",
        "username": "",
        "account_detail": "",
    },
    "shopping_data": {
        "budget": 0.0,
        "budget_text": "",
        "items": [],
    },
}


class ShoppingItemCard(BoxLayout):
    item_id = StringProperty("")
    item_name = StringProperty("")
    category = StringProperty("essential")
    checked = BooleanProperty(False)
    price_text = StringProperty("")
    screen_ref = ObjectProperty(None)
    card_color = ListProperty([1, 1, 1, 1])
    badge_color = ListProperty([1, 1, 1, 1])

    @property
    def category_label(self):
        return self.category.capitalize()

    @property
    def helper_text(self):
        if not self.checked:
            return "Check this when it's in your cart."
        if self.price_text:
            return f"Saved price: {self.price_text}"
        return "Add the price to count it."

    def on_kv_post(self, _base_widget):
        app = App.get_running_app()
        if self.category == "essential":
            self.card_color = [0.859, 0.667, 0.733, 0.35]   # dusty pink wash
            self.badge_color = [0.878, 0.502, 0.565, 1]      # coral pink
        else:
            self.card_color = [0.961, 0.937, 0.878, 1]       # cream
            self.badge_color = [0.541, 0.549, 0.353, 1]      # sage green

    def toggle_checked(self, value):
        if self.screen_ref:
            self.screen_ref.toggle_item(self.item_id, value)

    def save_price(self, value):
        if self.screen_ref:
            self.screen_ref.save_item_price(self.item_id, value)


class TextShadowMixin:
    shadow_enabled = BooleanProperty(True)
    shadow_color = ListProperty([0, 0, 0, 0.28])
    shadow_radius = NumericProperty(2.2)

    def __init__(self, **kwargs):
        self._shadow_trigger = Clock.create_trigger(self._refresh_shadow, -1)
        self._shadow_group = InstructionGroup()
        self._shadow_attached = False
        super().__init__(**kwargs)
        for prop_name in (
            "pos",
            "size",
            "text",
            "texture",
            "texture_size",
            "opacity",
            "disabled",
            "shadow_enabled",
            "shadow_color",
            "shadow_radius",
            "font_size",
            "font_name",
            "halign",
            "valign",
            "text_size",
            "padding",
        ):
            if prop_name in self.properties():
                self.bind(**{prop_name: self._queue_shadow_refresh})
        Clock.schedule_once(lambda *_: self._queue_shadow_refresh(), 0)

    def on_kv_post(self, base_widget):
        parent = getattr(super(), "on_kv_post", None)
        if callable(parent):
            parent(base_widget)
        self._queue_shadow_refresh()

    def _queue_shadow_refresh(self, *_args):
        trigger = getattr(self, "_shadow_trigger", None)
        if trigger is not None:
            trigger()

    def _ensure_shadow_group(self):
        if self._shadow_attached:
            return
        self.canvas.before.add(self._shadow_group)
        self._shadow_attached = True

    def _get_padding_values(self):
        padding = getattr(self, "padding", [0, 0, 0, 0])
        if isinstance(padding, (int, float)):
            return float(padding), float(padding), float(padding), float(padding)
        if len(padding) == 2:
            return float(padding[0]), float(padding[1]), float(padding[0]), float(padding[1])
        if len(padding) == 4:
            return tuple(float(value) for value in padding)
        return 0.0, 0.0, 0.0, 0.0

    def _get_texture_rect(self):
        texture = getattr(self, "texture", None)
        if not texture:
            return None
        tex_w, tex_h = self.texture_size
        if tex_w <= 1 or tex_h <= 1:
            return None

        pad_left, pad_top, pad_right, pad_bottom = self._get_padding_values()
        avail_w = max(0.0, self.width - pad_left - pad_right)
        avail_h = max(0.0, self.height - pad_top - pad_bottom)

        halign = getattr(self, "halign", "left")
        valign = getattr(self, "valign", "middle")

        if halign == "right":
            x = self.right - pad_right - tex_w
        elif halign == "center":
            x = self.x + pad_left + (avail_w - tex_w) / 2.0
        else:
            x = self.x + pad_left

        if valign == "top":
            y = self.top - pad_top - tex_h
        elif valign == "bottom":
            y = self.y + pad_bottom
        else:
            y = self.y + pad_bottom + (avail_h - tex_h) / 2.0

        return x, y, tex_w, tex_h

    def _refresh_shadow(self, *_args):
        self._ensure_shadow_group()
        self._shadow_group.clear()

        if not self.shadow_enabled or self.opacity <= 0 or not getattr(self, "text", ""):
            return

        texture = getattr(self, "texture", None)
        texture_rect = self._get_texture_rect()
        if texture is None or not texture_rect:
            return

        x, y, tex_w, tex_h = texture_rect
        alpha = max(0.0, min(1.0, self.shadow_color[3]))
        radius = max(1.0, float(self.shadow_radius))
        passes = (
            (0.65, 0.5, 0.32),
            (1.15, 0.82, 0.18),
            (1.7, 1.08, 0.1),
        )

        for offset_x, offset_y, alpha_scale in passes:
            self._shadow_group.add(
                Color(
                    self.shadow_color[0],
                    self.shadow_color[1],
                    self.shadow_color[2],
                    alpha * alpha_scale,
                )
            )
            self._shadow_group.add(
                Rectangle(
                    texture=texture,
                    pos=(x + radius * offset_x, y - radius * offset_y),
                    size=(tex_w, tex_h),
                )
            )


class ShadowLabel(TextShadowMixin, Label):
    pass


class GlowLabel(Label):
    pass


class GlowButton(TextShadowMixin, Button):
    pass


class GlowToggleButton(TextShadowMixin, ToggleButton):
    pass


class PressableMixin:
    press_scale = NumericProperty(1.0)
    rest_lift = NumericProperty(0.0)
    text_lift = NumericProperty(0.0)
    corner_radius = NumericProperty(dp(24))
    overlay_color = ListProperty([1, 1, 1, 0])
    shadow_color = ListProperty([0, 0, 0, 0])
    selected_outline = ListProperty([0, 0, 0, 0])
    _pressed = BooleanProperty(False)
    _hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform not in ("android", "ios"):
            Window.bind(mouse_pos=self._handle_mouse_pos)

    def on_touch_down(self, touch):
        handled = super().on_touch_down(touch)
        if self.collide_point(*touch.pos) and not self.disabled:
            self._pressed = True
            Animation.cancel_all(self, "press_scale", "text_lift", "overlay_color")
            Animation(
                press_scale=0.972,
                text_lift=dp(0.5),
                overlay_color=[1, 1, 1, 0.06],
                duration=0.075,
                t="out_quad",
            ).start(self)
        return handled

    def on_touch_up(self, touch):
        handled = super().on_touch_up(touch)
        if self._pressed:
            self._pressed = False
            Animation.cancel_all(self, "press_scale", "text_lift", "overlay_color")
            Animation(
                press_scale=1.012 if self._hovered else 1.0,
                text_lift=self.rest_lift + (dp(1.2) if self._hovered else 0),
                overlay_color=[1, 1, 1, 0],
                duration=0.12,
                t="out_back",
            ).start(self)
        return handled

    def _handle_mouse_pos(self, _window, pos):
        if not self.get_root_window() or self.disabled:
            if self._hovered:
                self._set_hovered(False)
            return
        local_x, local_y = self.to_widget(*pos)
        self._set_hovered(self.collide_point(local_x, local_y))

    def _set_hovered(self, hovered):
        if hovered == self._hovered:
            return
        self._hovered = hovered
        if self._pressed:
            return
        Animation.cancel_all(self, "press_scale", "text_lift", "overlay_color")
        Animation(
            press_scale=1.012 if hovered else 1.0,
            text_lift=self.rest_lift + (dp(1.2) if hovered else 0),
            overlay_color=[1, 1, 1, 0.028 if hovered else 0],
            duration=0.14 if hovered else 0.18,
            t="out_quad",
        ).start(self)


class PrimaryButton(PressableMixin, GlowButton):
    base_color = ListProperty([1, 1, 1, 1])


class SecondaryButton(PressableMixin, GlowButton):
    base_color = ListProperty([1, 1, 1, 1])


class AccentButton(PressableMixin, GlowButton):
    base_color = ListProperty([1, 1, 1, 1])


class ChoiceChip(PressableMixin, GlowToggleButton):
    selected_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_outline = [0.55, 0.72, 0.58, 1]


class GenderChip(ChoiceChip):
    pass


class SoftInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._apply_text_colors()
        self.bind(focus=lambda *_: self._apply_text_colors())
        self.bind(text=lambda *_: self._apply_text_colors())
        self.bind(disabled=lambda *_: self._apply_text_colors())
        Clock.schedule_once(lambda *_: self._apply_text_colors(), 0)
        Clock.schedule_once(lambda *_: self._apply_text_colors(), 0.1)

    def on_kv_post(self, _base_widget):
        self._apply_text_colors()

    def _get_line_options(self):
        options = super()._get_line_options()
        options["foreground_color"] = [0, 0, 0, 1]
        return options

    def _update_graphics(self, *largs):
        self.canvas.clear()

        line_height = self.line_height
        dy = line_height + self.line_spacing
        scroll_x = self.scroll_x
        scroll_y = self.scroll_y

        if not self._lines or (not self._lines[0] and len(self._lines) == 1):
            rects = self._hint_text_rects
            labels = self._hint_text_labels
            lines = self._hint_text_lines
            text_color = self.hint_text_color
        else:
            rects = self._lines_rects
            labels = self._lines_labels
            lines = self._lines
            text_color = self.disabled_foreground_color if self.disabled else [0, 0, 0, 1]

        self.canvas.add(Color(*text_color))

        padding_left, padding_top, padding_right, padding_bottom = self.padding
        x = self.x + padding_left
        y = self.top - padding_top + scroll_y
        miny = self.y + padding_bottom
        maxy = self.top - padding_top
        halign = self.halign
        base_dir = self.base_direction

        auto_halign_r = halign == 'auto' and base_dir and 'rtl' in base_dir
        fst_visible_ln = None
        viewport_pos = scroll_x, 0
        for line_num, value in enumerate(lines):
            if miny < y < maxy + dy:
                if fst_visible_ln is None:
                    fst_visible_ln = line_num

                y = self._draw_line(
                    value,
                    line_num,
                    labels[line_num],
                    viewport_pos,
                    line_height,
                    miny,
                    maxy,
                    x,
                    y,
                    base_dir,
                    halign,
                    rects,
                    auto_halign_r,
                )
            elif y <= miny:
                line_num -= 1
                break

            y -= dy

        if fst_visible_ln is not None:
            self._visible_lines_range = (fst_visible_ln, line_num + 1)
        else:
            self._visible_lines_range = 0, 0

        self._update_graphics_selection()
        self._draw_cursor_visual()

    def _draw_cursor_visual(self):
        should_draw_cursor = (
            self.focus
            and not self.disabled
            and not self.readonly
            and (not self.cursor_blink or not self._cursor_blink)
        )
        if not should_draw_cursor:
            return
        cursor_height = max(0, int(self._cursor_visual_height))
        if cursor_height <= 0:
            return
        cursor_x, cursor_top = self._cursor_visual_pos
        cursor_width = max(float(self.cursor_width), dp(2.5))
        self.canvas.add(Color(0, 0, 0, 1))
        self.canvas.add(
            Rectangle(
                pos=(cursor_x, cursor_top - cursor_height),
                size=(cursor_width, cursor_height),
            )
        )

    def _do_blink_cursor(self, dt):
        super()._do_blink_cursor(dt)
        trigger = getattr(self, "_trigger_update_graphics", None)
        if callable(trigger):
            trigger()

    def _apply_text_colors(self):
        app = App.get_running_app()
        muted = app.colors["text_muted"] if app else [0.28, 0.28, 0.28, 1]
        self.foreground_color = [0, 0, 0, 1]
        self.disabled_foreground_color = [0, 0, 0, 1]
        self.cursor_color = [0, 0, 0, 1]
        self.hint_text_color = muted
        refresh = getattr(self, "_trigger_refresh_text", None)
        if callable(refresh):
            refresh()
        self.canvas.ask_update()


class SplashScreen(Screen):
    pass


class LoginScreen(Screen):
    def login(self, username, password):
        message = App.get_running_app().login_user(username, password)
        self.ids.login_message.text = message or ""


class SignupScreen(Screen):
    def signup(self, name, birthday, gender, username, password):
        if not name.strip():
            self.ids.signup_message.text = "Please enter a display name."
            return
        message = App.get_running_app().register_user(name, birthday, gender, username, password)
        self.ids.signup_message.text = message or ""


class HomeScreen(Screen):
    def on_pre_enter(self, *_args):
        self.refresh_content()

    def refresh_content(self):
        app = App.get_running_app()
        self.ids.home_greeting.text = f"Hi, {app.profile.get('display_name', '') or 'Shopper'}!"


class ProfileScreen(Screen):
    def on_pre_enter(self, *_args):
        self.refresh_content()

    def refresh_content(self):
        app = App.get_running_app()
        self.ids.profile_name.text = app.profile.get("display_name", "")
        self.ids.profile_birthday.text = app.profile.get("birthday", "")
        self.ids.profile_username.text = app.profile.get("username", "")
        self.ids.profile_password.text = ""
        gender = (app.profile.get("gender", "") or "female").strip().lower()
        self.ids.profile_gender_female.state = "down" if gender == "female" else "normal"
        self.ids.profile_gender_male.state = "down" if gender == "male" else "normal"
        self.ids.profile_gender_skip.state = "down" if gender == "prefer not to say" else "normal"
        if gender not in ("female", "male", "prefer not to say"):
            self.ids.profile_gender_female.state = "down"
        self.ids.profile_message.text = ""

    def save_profile(self, name, birthday, gender, username, password):
        if not name.strip():
            self.ids.profile_message.text = "Display name cannot be empty."
            return
        message = App.get_running_app().update_profile(name, birthday, gender, username, password)
        self.ids.profile_message.text = message


class AboutScreen(Screen):
    pass


class CreateListScreen(Screen):
    def add_item(self, item_name, category):
        self.ids.create_message.text = App.get_running_app().add_item_to_list(item_name, category)
        self.ids.item_input.text = ""

    def remove_item(self, category):
        self.ids.create_message.text = App.get_running_app().remove_item_from_list(category)


class CurrentListScreen(Screen):
    def on_pre_enter(self, *_args):
        self.refresh_items()

    def refresh_items(self):
        app = App.get_running_app()
        holder = self.ids.item_holder
        holder.clear_widgets()
        items = sorted(
            app.get_current_items(),
            key=lambda item: (0 if item.get("category") == "essential" else 1)
        )
        if not items:
            holder.add_widget(
                Label(
                    text="Your list will show up here.",
                    color=app.colors["text_muted"],
                    font_name=app.body_font,
                    font_size="15sp",
                    size_hint_y=None,
                    height=dp(42),
                    halign="left",
                    valign="middle",
                    text_size=(Window.width - dp(88), None),
                )
            )
            return
        for item in items:
            holder.add_widget(
                ShoppingItemCard(
                    item_id=item["id"],
                    item_name=item["name"],
                    category=item["category"],
                    checked=item.get("checked", False),
                    price_text=item.get("price_text", ""),
                    screen_ref=self,
                )
            )

    def save_budget(self, value):
        App.get_running_app().save_budget(value)

    def toggle_item(self, item_id, value):
        App.get_running_app().toggle_checked(item_id, value)

    def save_item_price(self, item_id, value):
        App.get_running_app().save_price(item_id, value)


class EssentiaApp(App):
    colors = DictProperty(
        {
            "bg":                 [0.961, 0.937, 0.878, 1],
            "card":               [0.961, 0.937, 0.878, 0.98],
            "cream":              [0.961, 0.937, 0.878, 1],
            "ink":                [0.420, 0.353, 0.306, 1],
            "text":               [0.420, 0.353, 0.306, 1],
            "text_muted":         [0.541, 0.549, 0.353, 0.80],
            "outline":            [0.859, 0.667, 0.733, 1],
            "dot":                [0.878, 0.502, 0.565, 0.55],
            "green_button":       [0.541, 0.549, 0.353, 1],
            "green_main":         [0.541, 0.549, 0.353, 1],
            "green_soft":         [0.859, 0.667, 0.733, 0.35],
            "green_alt":          [0.541, 0.549, 0.353, 1],
            "green_alt_soft":     [0.961, 0.937, 0.878, 1],
            "pink_main":          [0.878, 0.502, 0.565, 1],
            "pink_soft":          [0.859, 0.667, 0.733, 1],
            "pink_gloss":         [0.859, 0.667, 0.733, 0.18],
            "metallic_pink_base": [0.961, 0.937, 0.878, 1],
            "shadow":             [0.420, 0.353, 0.306, 0.07],
            "shadow_strong":      [0.420, 0.353, 0.306, 0.14],
            "danger":             [0.878, 0.502, 0.565, 1],
        }
    )
    profile = DictProperty({})
    shopping_data = DictProperty({})
    profile_preview = StringProperty("")
    essential_draft_text = StringProperty("No items yet.")
    optional_draft_text = StringProperty("No items yet.")
    budget_summary = StringProperty("")
    progress_caption = StringProperty("")
    progress_ratio = NumericProperty(0.0)
    progress_color = ListProperty([0.541, 0.549, 0.353, 1])
    title_font = StringProperty("")
    body_font = StringProperty("")
    bg_texture = ObjectProperty(None)
    button_gloss_texture = ObjectProperty(None)
    surface_glow_texture = ObjectProperty(None)
    metallic_pink_texture = ObjectProperty(None)
    hero_image = StringProperty("")
    draft_image = StringProperty("")
    summary_image = StringProperty("")
    signup_image = StringProperty("")
    splash_logo = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_path = os.path.join(os.path.dirname(__file__), "essentia_data.json")
        self.database_path = os.path.join(os.path.dirname(__file__), "essentia_data.db")
        self.active_user_id = None
        self.current_password_hash = ""
        self.title_font = self.resolve_font(
            [
                os.path.join("gotham_rounded", "gothamrnd_bold.otf"),
                "gothamrnd_bold.otf",
                "GothamRounded-Bold.otf",
                "Gotham Rounded Bold.otf",
                "GothamRnd-Bold.otf",
                "GothamRoundedBold.otf",
                "GothamRounded-Bold.ttf",
                "Gotham Rounded Bold.ttf",
            ],
            resource_find("data/fonts/Roboto-Bold.ttf") or "",
        )
        self.body_font = self.resolve_font(
            [
                os.path.join("gotham_rounded", "gothamrnd_medium.otf"),
                "gothamrnd_medium.otf",
                "GothamRounded-Medium.otf",
                "Gotham Rounded Medium.otf",
                "GothamRnd-Medium.otf",
                "GothamRoundedMedium.otf",
                "GothamRounded-Medium.ttf",
                "Gotham Rounded Medium.ttf",
            ],
            resource_find("data/fonts/Roboto-Medium.ttf") or self.title_font,
        )
        self.bg_texture = self.make_gradient_texture()
        self.button_gloss_texture = self.make_button_gloss_texture()
        self.surface_glow_texture = self.make_surface_glow_texture()
        self.metallic_pink_texture = self.make_metallic_pink_texture()
        asset_root = os.path.join(os.path.dirname(__file__), "ui_assets")
        self.hero_image = os.path.join(asset_root, "home_custom.png")
        self.draft_image = os.path.join(asset_root, "create_list_custom.png")
        self.summary_image = os.path.join(asset_root, "shopping_custom.png")
        self.signup_image = os.path.join(asset_root, "signup_custom.png")
        self.splash_logo = os.path.join(asset_root, "splash_logo.png")
        self.desktop_icon = os.path.join(asset_root, "icon_desktop.png")
        if os.path.exists(self.desktop_icon):
            Window.set_icon(self.desktop_icon)
        self.screen_order = ["splash", "login", "signup", "home", "profile", "about", "create_list", "current_list"]
        self.init_database()
        self.state = self.load_state()
        self.profile = deepcopy(self.state["profile"])
        self.shopping_data = deepcopy(self.state["shopping_data"])
        self.refresh_derived_state()

    def build(self):
        Builder.load_string(KV)
        self.sm = ScreenManager(transition=SlideTransition(duration=0.28))
        for screen_cls in [
            SplashScreen,
            LoginScreen,
            SignupScreen,
            HomeScreen,
            ProfileScreen,
            AboutScreen,
            CreateListScreen,
            CurrentListScreen,
        ]:
            self.sm.add_widget(screen_cls())
        Clock.schedule_once(self.finish_loading, 2.0)
        return self.sm

    def resolve_font(self, candidates, fallback):
        search_roots = [
            os.path.dirname(__file__),
            os.path.join(os.path.dirname(__file__), "starbim_assets"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"),
        ]
        for candidate in candidates:
            if os.path.isabs(candidate) and os.path.exists(candidate):
                return candidate
            for root in search_roots:
                possible = os.path.join(root, candidate)
                if os.path.exists(possible):
                    return possible
        return fallback

    def make_gradient_texture(self):
        # Gradient: cream base (#F5EFE0) with a dusty-pink bloom top-left
        # and a faint coral-pink warmth bottom-right — more cream than pink.
        # cream      rgb(245, 239, 224)
        # dusty pink rgb(219, 170, 187)
        # coral pink rgb(224, 128, 144)
        size = 32
        texture = Texture.create(size=(size, size), colorfmt="rgba")
        texture.mag_filter = "linear"
        texture.min_filter = "linear"
        pixels = []
        for y in range(size):
            y_norm = y / (size - 1)
            for x in range(size):
                x_norm = x / (size - 1)
                # dusty-pink bloom — top-left corner, soft radial
                dist_tl = ((x_norm ** 2) + (y_norm ** 2)) ** 0.5
                pink_bloom = max(0.0, 1.0 - dist_tl / 0.75) ** 1.6
                # coral whisper — bottom-right corner
                dist_br = (((1 - x_norm) ** 2) + ((1 - y_norm) ** 2)) ** 0.5
                coral_whisper = max(0.0, 1.0 - dist_br / 0.85) ** 2.2
                # cream base; blend pink bloom then coral whisper on top
                r = int(245 + pink_bloom * (219 - 245) * 0.90 + coral_whisper * (224 - 245) * 0.65)
                g = int(239 + pink_bloom * (170 - 239) * 0.90 + coral_whisper * (128 - 239) * 0.50)
                b = int(224 + pink_bloom * (187 - 224) * 0.90 + coral_whisper * (144 - 224) * 0.50)
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                pixels.extend((r, g, b, 255))
        texture.blit_buffer(bytes(pixels), colorfmt="rgba", bufferfmt="ubyte")
        return texture

    def make_button_gloss_texture(self):
        width = 96
        height = 24
        pixels = []
        for y in range(height):
            y_norm = y / (height - 1)
            top_soft_glow = max(0.0, 1.0 - abs((y_norm - 0.28) / 0.36))
            vertical_depth = 1.0 - abs((y_norm - 0.5) / 0.5)
            for x in range(width):
                x_norm = x / (width - 1)
                center_sheen = max(0.0, 1.0 - abs((x_norm - 0.36) / 0.33))
                edge_falloff = 1.0 - abs((x_norm - 0.5) / 0.5)
                brightness = 8 + center_sheen * 58 + top_soft_glow * 10 + vertical_depth * 3 + edge_falloff * 4
                brightness = max(0, min(255, int(brightness)))
                pixels.extend((brightness, brightness, brightness, 255))
        texture = Texture.create(size=(width, height), colorfmt="rgba")
        texture.mag_filter = "linear"
        texture.min_filter = "linear"
        texture.blit_buffer(bytes(pixels), colorfmt="rgba", bufferfmt="ubyte")
        return texture

    def make_surface_glow_texture(self):
        width = 96
        height = 96
        pixels = []
        for y in range(height):
            y_norm = y / (height - 1)
            upper_bloom = max(0.0, 1.0 - abs((y_norm - 0.14) / 0.24))
            lower_soft = max(0.0, 1.0 - abs((y_norm - 0.7) / 0.5))
            for x in range(width):
                x_norm = x / (width - 1)
                left_sheen = max(0.0, 1.0 - abs((x_norm - 0.24) / 0.34))
                right_falloff = max(0.0, 1.0 - abs((x_norm - 0.78) / 0.42))
                diagonal = max(0.0, 1.0 - abs((x_norm - (0.18 + y_norm * 0.48)) / 0.22))
                warm_corner = max(0.0, 1.0 - abs((x_norm - 0.88) / 0.2)) * max(0.0, 1.0 - abs((y_norm - 0.12) / 0.2))
                brightness = 22 + upper_bloom * 82 + left_sheen * 46 + right_falloff * 20 + lower_soft * 14 + diagonal * 58
                alpha = 108 + upper_bloom * 108 + diagonal * 82 + left_sheen * 36
                r = max(0, min(255, int(brightness + warm_corner * 12)))
                g = max(0, min(255, int(brightness + warm_corner * 5)))
                b = max(0, min(255, int(brightness + left_sheen * 4)))
                alpha = max(0, min(255, int(alpha)))
                pixels.extend((r, g, b, alpha))
        texture = Texture.create(size=(width, height), colorfmt="rgba")
        texture.mag_filter = "linear"
        texture.min_filter = "linear"
        texture.wrap = "repeat"
        texture.blit_buffer(bytes(pixels), colorfmt="rgba", bufferfmt="ubyte")
        return texture

    def make_metallic_pink_texture(self):
        width = 96
        height = 48
        pixels = []
        for y in range(height):
            y_norm = y / (height - 1)
            top_sheen = max(0.0, 1.0 - abs((y_norm - 0.18) / 0.24))
            middle_satin = max(0.0, 1.0 - abs((y_norm - 0.5) / 0.36))
            lower_reflect = max(0.0, 1.0 - abs((y_norm - 0.84) / 0.2))
            for x in range(width):
                x_norm = x / (width - 1)
                left_bloom = max(0.0, 1.0 - abs((x_norm - 0.2) / 0.32))
                center_band = max(0.0, 1.0 - abs((x_norm - 0.52) / 0.4))
                diagonal = max(0.0, 1.0 - abs((x_norm - (0.18 + y_norm * 0.52)) / 0.22))
                r = int(min(255, 250 + top_sheen * 4 + left_bloom * 3 + diagonal * 2))
                g = int(min(255, 245 + middle_satin * 5 + center_band * 2 + lower_reflect * 3))
                b = int(min(255, 240 + top_sheen * 5 + lower_reflect * 4 + diagonal * 2))
                a = int(min(255, 88 + top_sheen * 38 + middle_satin * 18 + diagonal * 12))
                pixels.extend((r, g, b, a))
        texture = Texture.create(size=(width, height), colorfmt="rgba")
        texture.mag_filter = "linear"
        texture.min_filter = "linear"
        texture.blit_buffer(bytes(pixels), colorfmt="rgba", bufferfmt="ubyte")
        return texture

    def finish_loading(self, *_args):
        self.go_to("home" if self.state.get("registered") else "login")

    def get_db_connection(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def init_database(self):
        with self.get_db_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    birthday TEXT NOT NULL DEFAULT '',
                    gender TEXT NOT NULL DEFAULT '',
                    username TEXT NOT NULL DEFAULT '',
                    password_hash TEXT NOT NULL DEFAULT '',
                    account_detail TEXT NOT NULL DEFAULT '',
                    shopping_data TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS app_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            user_columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }
            if "username" not in user_columns:
                connection.execute("ALTER TABLE users ADD COLUMN username TEXT NOT NULL DEFAULT ''")
            if "password_hash" not in user_columns:
                connection.execute("ALTER TABLE users ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''")
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower
                ON users(lower(username))
                WHERE username <> ''
                """
            )
        self.migrate_json_state_if_needed()

    def migrate_json_state_if_needed(self):
        if not os.path.exists(self.storage_path):
            return
        with self.get_db_connection() as connection:
            has_users = connection.execute("SELECT 1 FROM users LIMIT 1").fetchone()
            has_session = connection.execute(
                "SELECT value FROM app_state WHERE key = ?",
                ("active_user_id",),
            ).fetchone()
        if has_users or has_session:
            return
        legacy_state = self.load_legacy_json_state()
        if not legacy_state.get("registered"):
            return
        migrated_user_id = uuid.uuid4().hex
        with self.get_db_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (id, display_name, birthday, gender, username, password_hash, account_detail, shopping_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    migrated_user_id,
                    legacy_state["profile"].get("display_name", "").strip() or "Shopper",
                    legacy_state["profile"].get("birthday", "").strip(),
                    legacy_state["profile"].get("gender", "").strip(),
                    legacy_state["profile"].get("username", "").strip(),
                    "",
                    legacy_state["profile"].get("account_detail", "").strip(),
                    json.dumps(self.serialize_shopping_data(legacy_state["shopping_data"])),
                ),
            )
            connection.execute(
                """
                INSERT INTO app_state (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                ("active_user_id", migrated_user_id),
            )

    def load_legacy_json_state(self):
        state = deepcopy(DEFAULT_STATE)
        try:
            with open(self.storage_path, "r", encoding="utf-8") as file:
                loaded = json.load(file)
        except (OSError, json.JSONDecodeError):
            return state

        state["registered"] = bool(loaded.get("registered", False))
        state["profile"].update(loaded.get("profile", {}))
        shopping = loaded.get("shopping_data", {})
        state["shopping_data"]["budget"] = float(shopping.get("budget", 0.0) or 0.0)
        state["shopping_data"]["budget_text"] = shopping.get("budget_text", "")

        if isinstance(shopping.get("items"), list):
            state["shopping_data"]["items"] = [self.normalize_item(item) for item in shopping["items"]]
        else:
            state["shopping_data"]["items"] = self.migrate_legacy_items(shopping)
        return state

    def load_state(self):
        state = deepcopy(DEFAULT_STATE)
        with self.get_db_connection() as connection:
            session_row = connection.execute(
                "SELECT value FROM app_state WHERE key = ?",
                ("active_user_id",),
            ).fetchone()
            self.active_user_id = session_row["value"] if session_row and session_row["value"] else None
            if not self.active_user_id:
                return state
            user_row = connection.execute(
                """
                SELECT id, display_name, birthday, gender, username, password_hash, account_detail, shopping_data
                FROM users
                WHERE id = ?
                """,
                (self.active_user_id,),
            ).fetchone()
        if not user_row:
            self.active_user_id = None
            self.persist_active_user_id()
            return state
        state["registered"] = True
        state["profile"] = {
            "display_name": user_row["display_name"],
            "birthday": user_row["birthday"],
            "gender": user_row["gender"],
            "username": user_row["username"],
            "account_detail": user_row["account_detail"],
        }
        self.current_password_hash = user_row["password_hash"] or ""
        state["shopping_data"] = self.deserialize_shopping_data(user_row["shopping_data"])
        return state

    def migrate_legacy_items(self, shopping):
        legacy_current = shopping.get("current_list", {})
        legacy_prices = shopping.get("prices", {})
        legacy_checked = shopping.get("checked", {})
        migrated = []
        for category in ("essential", "optional"):
            for name in legacy_current.get(category, []):
                item_id = uuid.uuid4().hex
                migrated.append(
                    {
                        "id": item_id,
                        "name": str(name),
                        "category": category,
                        "checked": bool(legacy_checked.get(name, False)),
                        "price_text": str(legacy_prices.get(name, "")),
                    }
                )
        return migrated

    def normalize_item(self, item):
        return {
            "id": str(item.get("id") or uuid.uuid4().hex),
            "name": str(item.get("name", "")).strip(),
            "category": item.get("category", "essential") if item.get("category") in ("essential", "optional") else "essential",
            "checked": bool(item.get("checked", False)),
            "price_text": str(item.get("price_text", "")).strip(),
        }

    def serialize_shopping_data(self, shopping_data):
        return {
            "budget": float(shopping_data.get("budget", 0.0) or 0.0),
            "budget_text": str(shopping_data.get("budget_text", "")),
            "items": [
                self.normalize_item(item)
                for item in shopping_data.get("items", [])
                if item.get("name", "").strip()
            ],
        }

    def deserialize_shopping_data(self, raw_value):
        shopping_data = deepcopy(DEFAULT_STATE["shopping_data"])
        try:
            loaded = json.loads(raw_value) if raw_value else {}
        except json.JSONDecodeError:
            loaded = {}
        shopping_data["budget"] = float(loaded.get("budget", 0.0) or 0.0)
        shopping_data["budget_text"] = str(loaded.get("budget_text", ""))
        shopping_data["items"] = [self.normalize_item(item) for item in loaded.get("items", []) if isinstance(item, dict)]
        return shopping_data

    def persist_active_user_id(self):
        with self.get_db_connection() as connection:
            connection.execute(
                """
                INSERT INTO app_state (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                ("active_user_id", self.active_user_id or ""),
            )

    def hash_password(self, password):
        salt = os.urandom(16).hex()
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 100000).hex()
        return f"{salt}${digest}"

    def verify_password(self, password, stored_hash):
        if not stored_hash or "$" not in stored_hash:
            return False
        salt, expected_digest = stored_hash.split("$", 1)
        actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 100000).hex()
        return hmac.compare_digest(actual_digest, expected_digest)

    def get_user_by_username(self, username):
        clean_username = username.strip()
        if not clean_username:
            return None
        with self.get_db_connection() as connection:
            return connection.execute(
                """
                SELECT id, display_name, birthday, gender, username, password_hash, account_detail, shopping_data
                FROM users
                WHERE lower(username) = lower(?)
                LIMIT 1
                """,
                (clean_username,),
            ).fetchone()

    def username_taken(self, username, exclude_user_id=None):
        existing_user = self.get_user_by_username(username)
        if not existing_user:
            return False
        return existing_user["id"] != exclude_user_id

    def save_state(self):
        self.state["registered"] = bool(self.active_user_id)
        self.state["profile"] = dict(self.profile)
        self.state["shopping_data"] = self.serialize_shopping_data(self.shopping_data)
        self.persist_active_user_id()
        if not self.active_user_id:
            return
        with self.get_db_connection() as connection:
            connection.execute(
                """
                UPDATE users
                SET display_name = ?, birthday = ?, gender = ?, username = ?, password_hash = ?,
                    account_detail = ?, shopping_data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    self.profile.get("display_name", "").strip() or "Shopper",
                    self.profile.get("birthday", "").strip(),
                    self.profile.get("gender", "").strip(),
                    self.profile.get("username", "").strip(),
                    self.current_password_hash,
                    self.profile.get("account_detail", "").strip(),
                    json.dumps(self.state["shopping_data"]),
                    self.active_user_id,
                ),
            )

    def refresh_derived_state(self):
        name = self.profile.get("display_name", "") or "Shopper"
        self.profile_preview = (
            f"Name: {name}\n"
            f"Username: {self.profile.get('username', '') or 'Not set'}\n"
            f"Birthday: {self.profile.get('birthday', '') or 'Not set'}\n"
            f"Gender: {self.profile.get('gender', '') or 'Not set'}\n"
            f"Saved list items: {len(self.shopping_data.get('items', []))}"
        )
        self.essential_draft_text = self.format_items("essential")
        self.optional_draft_text = self.format_items("optional")

        budget = float(self.shopping_data.get("budget", 0.0) or 0.0)
        spent = 0.0
        essential_left = 0
        optional_left = 0

        for item in self.shopping_data.get("items", []):
            if item.get("category") == "essential" and not item.get("checked"):
                essential_left += 1
            if item.get("category") == "optional" and not item.get("checked"):
                optional_left += 1
            if item.get("checked") and item.get("price_text"):
                try:
                    spent += float(item["price_text"])
                except (TypeError, ValueError):
                    pass

        remaining = budget - spent
        self.progress_ratio = (spent / budget) if budget > 0 else 0.0
        self.progress_color = self.colors["green_main"] if remaining >= 0 else self.colors["danger"]
        if budget > 0:
            self.budget_summary = f"Budget: {budget:.2f}   Spent: {spent:.2f}   Remaining: {remaining:.2f}"
        else:
            self.budget_summary = "No budget yet."

        if budget <= 0:
            self.progress_caption = "Set a budget to track your shopping."
        elif remaining < 0:
            self.progress_caption = "You're over budget."
        elif essential_left > 0:
            self.progress_caption = f"{essential_left} essential item(s) left."
        elif optional_left > 0:
            self.progress_caption = f"{optional_left} optional item(s) left."
        else:
            self.progress_caption = "All done. Nice!"

    def refresh_ui(self):
        self.refresh_derived_state()
        if hasattr(self, "sm"):
            if self.sm.has_screen("home"):
                self.sm.get_screen("home").refresh_content()
            if self.sm.has_screen("profile"):
                self.sm.get_screen("profile").refresh_content()
            if self.sm.has_screen("current_list"):
                self.sm.get_screen("current_list").refresh_items()

    def go_to(self, screen_name):
        self.refresh_ui()
        if hasattr(self, "sm") and self.sm.current in self.screen_order and screen_name in self.screen_order:
            current_index = self.screen_order.index(self.sm.current)
            target_index = self.screen_order.index(screen_name)
            self.sm.transition.direction = "left" if target_index >= current_index else "right"
        self.sm.current = screen_name

    def register_user(self, name, birthday, gender, username, password):
        clean_name = name.strip()
        clean_birthday = birthday.strip()
        clean_gender = gender.strip()
        clean_username = username.strip()
        clean_password = password.strip()
        if not clean_username:
            return "Please choose a username."
        if not clean_password:
            return "Please choose a password."
        if len(clean_password) < 4:
            return "Password must be at least 4 characters."
        if self.username_taken(clean_username):
            return "That username is already taken."

        self.active_user_id = uuid.uuid4().hex
        self.current_password_hash = self.hash_password(clean_password)
        self.shopping_data = deepcopy(DEFAULT_STATE["shopping_data"])
        self.profile = {
            "display_name": clean_name,
            "birthday": clean_birthday,
            "gender": clean_gender,
            "username": clean_username,
            "account_detail": "",
        }
        with self.get_db_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (id, display_name, birthday, gender, username, password_hash, account_detail, shopping_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.active_user_id,
                    clean_name or "Shopper",
                    clean_birthday,
                    clean_gender,
                    clean_username,
                    self.current_password_hash,
                    "",
                    json.dumps(self.serialize_shopping_data(self.shopping_data)),
                ),
            )
        self.save_state()
        self.go_to("home")
        return ""

    def login_user(self, username, password):
        clean_username = username.strip()
        clean_password = password.strip()
        if not clean_username or not clean_password:
            return "Enter your username and password."
        user_row = self.get_user_by_username(clean_username)
        if not user_row or not self.verify_password(clean_password, user_row["password_hash"]):
            return "Incorrect username or password."
        self.active_user_id = user_row["id"]
        self.current_password_hash = user_row["password_hash"] or ""
        self.profile = {
            "display_name": user_row["display_name"],
            "birthday": user_row["birthday"],
            "gender": user_row["gender"],
            "username": user_row["username"],
            "account_detail": user_row["account_detail"],
        }
        self.shopping_data = self.deserialize_shopping_data(user_row["shopping_data"])
        self.save_state()
        self.go_to("home")
        return ""

    def update_profile(self, name, birthday, gender, username, password):
        clean_name = name.strip()
        clean_username = username.strip()
        clean_password = password.strip()
        if not clean_username:
            return "Username cannot be empty."
        if self.username_taken(clean_username, exclude_user_id=self.active_user_id):
            return "That username is already taken."
        if not self.current_password_hash and not clean_password:
            return "Please set a password before logging out."
        if clean_password and len(clean_password) < 4:
            return "New password must be at least 4 characters."
        if clean_password:
            self.current_password_hash = self.hash_password(clean_password)
        self.profile = {
            "display_name": clean_name,
            "birthday": birthday.strip(),
            "gender": gender.strip(),
            "username": clean_username,
            "account_detail": "",
        }
        self.save_state()
        self.refresh_ui()
        return "Profile updated."

    def sign_out(self, menu=None):
        if menu:
            menu.dismiss()
        self.active_user_id = None
        self.current_password_hash = ""
        self.state = deepcopy(DEFAULT_STATE)
        self.profile = deepcopy(DEFAULT_STATE["profile"])
        self.shopping_data = deepcopy(DEFAULT_STATE["shopping_data"])
        self.save_state()
        self.go_to("login")

    def open_settings_menu(self):
        from kivy.graphics import Color, RoundedRectangle

        menu = ModalView(size_hint=(0.86, None), height=dp(250), background_color=(0, 0, 0, 0))
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=[dp(18), dp(12), dp(18), dp(18)])
        with content.canvas.before:
            Color(*self.colors["card"])
            bg_rect = RoundedRectangle(pos=content.pos, size=content.size, radius=[26, 26, 26, 26])
        content.bind(pos=lambda *_: setattr(bg_rect, "pos", content.pos))
        content.bind(size=lambda *_: setattr(bg_rect, "size", content.size))

        title = Label(
            text="Settings",
            color=self.colors["text"],
            font_name=self.title_font,
            font_size="22sp",
            size_hint_y=None,
            height=dp(28),
            halign="center",
            valign="middle",
            text_size=(dp(260), dp(28)),
        )
        content.add_widget(title)

        button_styles = [
            ("View Profile",    lambda *_: self._settings_nav(menu, "profile"), (0.859, 0.667, 0.733, 1), (0.420, 0.353, 0.306, 1)),
            ("About Essentia",  lambda *_: self._settings_nav(menu, "about"),   (0.541, 0.549, 0.353, 1), (0.961, 0.937, 0.878, 1)),
            ("Sign Out",        lambda *_: self.sign_out(menu),                 (0.878, 0.502, 0.565, 1), (0.961, 0.937, 0.878, 1)),
        ]
        for label_text, callback, bg, fg in button_styles:
            btn = SecondaryButton(
                text=label_text,
                size_hint_y=None,
                height=dp(48),
            )
            btn.base_color = list(bg)
            btn.color = list(fg)
            btn.bind(on_release=callback)
            content.add_widget(btn)

        menu.add_widget(content)
        menu.open()

    def _settings_nav(self, menu, target):
        menu.dismiss()
        Clock.schedule_once(lambda *_: self.go_to(target), 0.05)

    def get_current_items(self):
        return list(self.shopping_data.get("items", []))

    def add_item_to_list(self, item_name, category):
        clean_name = item_name.strip()
        if not clean_name:
            return "Type an item first."
        items = list(self.shopping_data.get("items", []))
        items.append(
            {
                "id": uuid.uuid4().hex,
                "name": clean_name,
                "category": category,
                "checked": False,
                "price_text": "",
            }
        )
        self.shopping_data["items"] = items
        self.save_state()
        self.refresh_ui()
        return f"Added to {category}."

    def remove_item_from_list(self, category):
        items = list(self.shopping_data.get("items", []))
        indexes = [index for index, item in enumerate(items) if item.get("category") == category]
        if not indexes:
            return f"No {category} items to remove."
        remove_index = indexes[0] if category == "essential" else indexes[-1]
        removed = items.pop(remove_index)
        self.shopping_data["items"] = items
        self.save_state()
        self.refresh_ui()
        return f"{removed.get('name', 'Item')} has been removed."

    def save_budget(self, value):
        clean_value = value.strip()
        try:
            amount = float(clean_value) if clean_value else 0.0
        except ValueError:
            return
        self.shopping_data["budget"] = amount
        self.shopping_data["budget_text"] = clean_value
        self.save_state()
        self.refresh_ui()

    def toggle_checked(self, item_id, value):
        items = list(self.shopping_data.get("items", []))
        for item in items:
            if item.get("id") == item_id:
                item["checked"] = bool(value)
                if not value:
                    item["price_text"] = ""
                break
        self.shopping_data["items"] = items
        self.save_state()
        self.refresh_ui()

    def save_price(self, item_id, value):
        clean_value = value.strip()
        items = list(self.shopping_data.get("items", []))
        for item in items:
            if item.get("id") == item_id:
                if not clean_value:
                    item["price_text"] = ""
                else:
                    try:
                        item["price_text"] = f"{float(clean_value):.2f}"
                    except ValueError:
                        return
                break
        self.shopping_data["items"] = items
        self.save_state()
        self.refresh_ui()

    def get_list_summary(self):
        essential_count = sum(1 for item in self.shopping_data.get("items", []) if item.get("category") == "essential")
        optional_count = sum(1 for item in self.shopping_data.get("items", []) if item.get("category") == "optional")
        return (
            f"{essential_count} essential item(s) and {optional_count} optional item(s) are in your latest list."
            if essential_count or optional_count
            else "No list yet."
        )

    def format_items(self, category):
        items = [item["name"] for item in self.shopping_data.get("items", []) if item.get("category") == category]
        if not items:
            return "No items yet."
        return "\n".join(f"- {item}" for item in items)

if __name__ == "__main__":
    EssentiaApp().run()