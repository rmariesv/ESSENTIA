# ❀ Essentia

Welcome to **Essentia**! 

ִ˚❀.🐇✿˚✦˚ 

Essentia is a grocery prioritization mobile application developed using **Python**, **Kivy**, and **Buildozer**. This repository contains all the source code, assets, and files needed to run or build the application.

---

## 📥 Downloading the Project

### ⭐⭐⭐ Download ZIP 

1. Click the green **Code** button.
2. Select **Download ZIP**.
3. Extract the ZIP file anywhere on your computer.
4. Open the extracted **Essentia** folder.

---

## 📂 Project Structure

Your folder should look something like this:

```text
Essentia/
├── buildozer.spec
├── main.py
├── ui_assets/
├── font/
├── essentia_data.db
├── essentia_data.json
└── README.md
```

⚠️ PLEASE do NOT move, rename, or delete files as the application depends on these files being in their correct locations !!!

---

## ▶️ Running the Application

### Requirements

* Python 3.x 🐍
* Kivy 🎨

Install Kivy:

```bash
pip install kivy
```

Run the application:

```bash
python main.py
```

---

## 📱 Building the Android APK

### Requirements

* Linux or WSL (Ubuntu) 🐧
* Python 3
* Buildozer ⚙️

Install Buildozer:

```bash
pip install buildozer
```

Build the APK:

```bash
buildozer android debug
```

⋆˚꩜｡ The first build may take a while because Buildozer downloads Android SDKs and other tools automatically.

---

## 📦 APK Location

After a successful build, the APK will be located inside:

```text
bin/
```

Example:

```text
bin/essentia-debug.apk
```

# ⭐⭐⭐ Installing the APK on Android 

1. Transfer the APK to your Android device.
2. Open the APK file.
3. Allow installation from unknown sources if prompted.
4. Tap **Install**.
5. Launch Essentia from your app drawer.

---

## 🛠️ Troubleshooting

### App uses old code

```bash
buildozer android clean
buildozer android debug
```

### Missing images or assets

Make sure:

* 📁 `ui_assets/` exists
* 🔤 `font/` exists
* 📄 `essentia_data.json` exists
* 🗄️ `essentia_data.db` exists

### Buildozer not found

```bash
pip install buildozer
```

---

## Thank You! ୨୧

Thank you for checking out **Essentia**! 𖥸₊ ࣪˖⚘゛

If you're reviewing this project, downloading the ZIP file is the easiest way to access all source files. Feel free to explore the code, assets, and project structure.

Happy exploring! 

𐔌՞. .՞𐦯
