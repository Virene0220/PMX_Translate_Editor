# PMX Translate Editor

PMX Translate Editor is a Windows-friendly tool for translating PMX text fields used by MMD/PMX Editor models and stages.

It can translate object/material names, bones, morphs, and PMX texture paths from Japanese or Chinese to English or Vietnamese without accents. It rewrites PMX text strings only. It does not modify mesh data, material parameters, bones transforms, morph data, physics data, or image pixels.

## Download

For normal use, download and run:

```text
Tool/PMXTranslateEditor.exe
```

No Python installation is required for the packaged `.exe`.

## Main Features

- GUI editor for PMX text fields.
- GUI interface languages: English, Vietnamese, and Russian.
- CLI mode for batch usage.
- Target languages: English (`en`) and Vietnamese without accents (`vi`).
- Offline dictionary for common MMD/PMX terms.
- Optional online fallback for unresolved CJK text.
- Section filters for materials, bones, and morphs. Display frames, rigid bodies, joints, and soft bodies are temporarily disabled.
- Optional mode to write the same translated value to both `local_name` and `universal_name`.
- Optional texture mode to translate texture filenames, update PMX texture paths, and copy texture files.
- Optional cleanup mode to delete old texture files after successful copy when they are no longer referenced.

## Basic GUI Workflow

1. Run `Tool/PMXTranslateEditor.exe`.
2. Select UI language from the `UI` dropdown if needed: English, Tiếng Việt, or Русский.
3. Click `Open PMX` and choose a `.pmx` file.
4. Select target language: `en` or `vi`.
5. Choose sections in `Translate sections`.
6. Enable optional modes if needed.
7. Click `Auto Translate`.
8. Review rows in the `New value` column.
9. Edit selected rows manually if needed, then click `Apply Selected`.
10. Click `Save As` to write a new `.pmx` file.

## Name Modes

Default behavior:

```text
local_name      stays original
universal_name  receives the translated name
```

`Overwrite local names` allows the tool to also rewrite `local_name`.

`Translate local name and write both fields` uses `local_name` as the source and writes the same translated value to both fields:

```text
local_name      translated value
universal_name  translated value
```

Use this when you want to remove Chinese/Japanese names from both PMX name fields.

## Texture Mode

Enable this checkbox:

```text
Copy translated texture files and update PMX paths
```

The tool will:

1. Translate texture filenames in PMX texture paths.
2. Update texture paths in the saved PMX.
3. Copy original texture files to the translated filenames.
4. Keep original texture files by default.

Example:

```text
tex/床.png -> tex/floor.png
```

Optional cleanup:

```text
Delete original texture files after successful copy
```

This only deletes an old texture file when:

- the new copied file exists,
- the old file is inside the model folder,
- the old texture path is no longer referenced by another texture entry in the PMX.

The tool asks for confirmation before deleting old texture files in GUI mode.

## CLI Usage

Open the GUI from source:

```powershell
python .\pmx_translate_tool.py --gui
```

Translate to English:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en
```

Translate to Vietnamese without accents:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language vi
```

Preview changes without writing:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --dry-run
```

Write the same translated local name to both PMX name fields:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --sync-name-fields
```

Translate texture filenames and copy texture files:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --translate-textures
```

Translate texture filenames, copy new files, and delete old files when safe:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --translate-textures --delete-original-textures
```

Translate only selected sections:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --sections material,bone,morph
```

Valid section values:

```text
all, material, objects, bone, morph, display, rigid_body, joint, soft_body
```

`display`, `rigid_body`, `joint`, and `soft_body` are accepted for compatibility but are temporarily disabled in this version.

Use online fallback:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --online --source-language ja
python .\pmx_translate_tool.py "stage.pmx" --language en --online --source-language zh-CN
```

Online translation results are cached in:

```text
translation_cache.json
```

This cache file is local runtime data and should not be committed.

## Build EXE

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Build:

```powershell
python -m PyInstaller --clean PMXTranslateEditor.spec
```

The built file will be:

```text
dist/PMXTranslateEditor.exe
```

For release, copy it to:

```text
Tool/PMXTranslateEditor.exe
```

## Custom Icon

To build the EXE with a custom icon, place an icon file at the repository root:

```text
app_icon.ico
```

Then rebuild with:

```powershell
python -m PyInstaller --clean PMXTranslateEditor.spec
```

Optional:

```text
app_icon.png
```

If present, the source GUI can use it as a window icon. The Windows EXE icon still requires `app_icon.ico`.

## Repository Notes

Recommended files to commit:

```text
pmx_translate_tool.py
pyi_runtime_tk.py
PMXTranslateEditor.spec
README.md
app_icon.ico
app_icon.png
Tool/PMXTranslateEditor.exe
.gitignore
```

Do not commit generated folders or local runtime files:

```text
build/
dist/
__pycache__/
translation_cache.json
*.spec.bak
```

## Limitations

Offline translation cannot be perfect for every PMX file. PMX names may contain custom abbreviations, author-specific names, mixed Japanese/Chinese text, mojibake, or proper nouns. Rows that still contain CJK characters are highlighted for manual review before saving.

The online fallback uses a public Google Translate endpoint and requires Internet access. It may be rate limited or unavailable.
