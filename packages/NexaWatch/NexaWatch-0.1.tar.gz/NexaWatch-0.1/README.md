# PyWatcher: Your Dynamic Script Supervisor 🚀

Welcome to PyWatcher! Whether you're a seasoned developer or just getting started, PyWatcher is here to simplify your development process. It's designed to automatically restart scripts or applications when any change is detected, so you can keep coding without the constant back-and-forth of manual restarts.

![PyWatcher Demo](demo.gif)
<!-- Optional: Consider adding a gif of PyWatcher in action. -->

## 🌟 Features

- **Instant Auto-restart**: Say goodbye to manual restarts! PyWatcher does it instantly whenever it detects changes.
- **Supports Many Languages**: Whether you're coding in Python, JavaScript, or many others, PyWatcher has got you covered.
- **Highly Customizable**: Decide what you want to watch, how, and when. Tailored to fit your unique needs.
- **Beautiful Console Output**: With the Rich library, get feedback that's more than just text. It's an experience.
- **Interactive Mode**: More than just a watcher. Pause, resume, or restart your scripts right from your console.
- **Desktop Notifications**: Always stay in the loop, even if you're lost in a sea of tabs!

## 📥 Installation

It's as simple as:

\```bash
pip install pywatcher
\```

## 🚀 Getting Started

### Basic Usage:

Just starting out? Try this:

\```bash
pywatcher your_script.py
\```

### Advanced Configuration:

For the pros out there:

\```bash
pywatcher your_script.py --path /your/path/ --recursive --extensions .py .js --delay 2 --log-file watcher.log --notify
\```

#### Options:
- `--path`: Choose the directory you want to keep an eye on. By default, it's where you stand.
- `--recursive`: For those deep project hierarchies. Dive into all subdirectories.
- `--extensions`: Tell PyWatcher exactly what file types you're working with.
- `--delay`: How long should PyWatcher wait after a change to restart? You decide.
- `--log-file`: Keep a record of all the changes and restarts.
- `--notify`: For those who love notifications!
- `--interpreter`: Got a favorite Python interpreter? Let PyWatcher know.
- `--language`: Maybe you're not coding in Python? That's okay too!

## 🌐 Supported Languages

Out of the box, PyWatcher is fluent in:

- Python (`py`)
- JavaScript (`js`)
<!-- Add other languages you've configured here. -->

Got another language in mind? It's easy to add. Just modify the `config.py` file and include your desired language and its corresponding interpreter.

## 🤔 Need Help?

We've all been there. Check out our [Wiki](#) or join our [Community Forum](#). Our community is super friendly and always eager to help a fellow developer!

## 🤝 Contribution

Every great tool is built by the community. Fork, modify, and make PyWatcher even better! For major changes, please open an issue first. Let's discuss and make magic together!

## 📜 License

PyWatcher is proud to be open-source and is licensed under [MIT](LICENSE). 

Happy Coding! 🎉
