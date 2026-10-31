# Contributing to GLC CONVERTER

Thank you for helping improve GLC CONVERTER! Bug reports, new conversion profiles,
FFmpeg optimisations, UI improvements and translations are all welcome.
You can write issues and pull requests in English, French or Haitian Creole.

## Ways to contribute

- **Report a bug** or **suggest a feature** with the [issue forms](https://github.com/granlakucompany/glc-converter/issues/new/choose).
- **Ask a question** or share an idea in [Discussions](https://github.com/granlakucompany/glc-converter/discussions).
- **Send code** with a pull request (see below).

## Development setup

Requirements: Windows 10/11 64-bit and Python 3.12 (3.10+ works).

```bash
git clone https://github.com/<your-account>/glc-converter.git
cd glc-converter
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Before opening a pull request

1. Create a branch from `main` for your change.
2. Run the tests and the license check:

   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   python tools/check_licenses.py
   ```

   The same checks run automatically on GitHub for every pull request.
3. Open the pull request against `main` and describe what changed and how you tested it.

## Project rules

- **No GPL components.** The project is distributed under the MIT license, so the build must not
  include `libx264`, `libx265`, `libxvid`, `pillow-heif` or any other GPL encoder.
  `tools/check_licenses.py` must pass. Details: [`DOCS/06_LICENCES_ET_DISTRIBUTION.md`](DOCS/06_LICENCES_ET_DISTRIBUTION.md).
- **Translate every user-facing text** in the 9 languages of `src/core/i18n.py`
  (French, Haitian Creole, English, Spanish, Portuguese, German, Italian, Chinese, Russian).
  English is the default language.
- **Keep the UI responsive.** Long work (conversions, rendering) runs outside the UI thread.
- **No secrets or personal data** in the code: no API keys, passwords, tokens or local paths.
- Match the style of the surrounding code and add a test when you fix a bug.

## License

By contributing, you agree that your contributions are released under the [MIT License](LICENSE.txt)
of the project.

---

GLC CONVERTER is developed by GETHO GUERRIER for [GRAN LAKU COMPANY](https://granlaku.com/glcconverter).
