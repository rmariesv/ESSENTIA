# ESSENTIA
grocery prioritization application that seperates essential and optional items for organization purposes.

Here's a more thorough set of instructions you can place in your README.md for people who want to build and run the app from your GitHub repository:

## Downloading the Project

### Option 1: Download ZIP

1. Open the GitHub repository.
2. Click the green **Code** button.
3. Select **Download ZIP**.
4. Extract the ZIP file to a folder on your computer.

---

# Project Files

After downloading, your folder should look similar to:

```text
Essentia/
├── buildozer.spec
├── main.py
├── ui_assets/
├── gotham_rounded/
├── essentia_data.db
├── essentia_data.json
└── README.md
```

Do not rename or move any files or folders, as the application depends on their current locations.

---

# Running the Application on a Computer

## Requirements

* Python 3.10 or newer
* Kivy

Install Kivy:

```bash
pip install kivy
```

Navigate to the project folder:

```bash
cd Essentia
```

Run the application:

```bash
python main.py
```

---

# Building the Android APK

## Prerequisites

### Linux / WSL (Recommended)

Buildozer only officially supports Linux.

If using Windows:

1. Install WSL (Windows Subsystem for Linux)
2. Install Ubuntu from the Microsoft Store
3. Open Ubuntu

Update Ubuntu:

```bash
sudo apt update
sudo apt upgrade
```

Install required packages:

```bash
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv
```

Install Buildozer:

```bash
pip install buildozer
```

---

# Building the APK

Navigate to the project folder:

```bash
cd Essentia
```

If this is your first build:

```bash
buildozer android debug
```

Buildozer will automatically download:

* Android SDK
* Android NDK
* Required build tools

The first build may take 20–60 minutes depending on your internet speed and computer.

---

# APK Location

Once the build is complete, the APK can be found in:

```text
bin/
```

Example:

```text
bin/essentia-0.1-arm64-v8a-debug.apk
```

---

# Installing the APK on Android

1. Transfer the APK to your Android device. 
2. Open the APK file.
3. Allow installation from unknown sources if prompted.
4. Tap **Install**.
5. Find the app on your home screen and launch Essentia.

---

# Troubleshooting

### Buildozer command not found

Install Buildozer:

```bash
pip install buildozer
```

### Missing assets or images

Verify that:

* `ui_assets/` exists
* `font/` exists
* All files were downloaded from the repository

### Build fails

Clean the build and rebuild:

```bash
buildozer android clean
buildozer android debug
```

### App uses old code

Delete the build cache:

```bash
rm -rf .buildozer
buildozer android debug
```

---

# Included Files

The repository intentionally excludes:

```text
__pycache__/
```

These folders are automatically generated and do not need to be downloaded.

---
