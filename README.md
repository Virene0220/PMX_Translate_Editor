# PMX Translate Editor

## English

PMX Translate Editor is a small Windows-friendly tool for editing and translating text fields inside MMD/PMX model files. It is designed for PMX Editor workflows where Japanese or Chinese object names need to be converted to English or unaccented Vietnamese.

The tool only rewrites PMX text strings. It does not modify meshes, materials settings, bones transforms, morph data, rigid bodies, joints, physics, textures, or other binary model data.

### Features

- GUI editor built with Tkinter.
- CLI mode for batch-style translation.
- Target languages: English (`en`) and unaccented Vietnamese (`vi`).
- Offline MMD-oriented dictionary for common PMX names.
- Optional online fallback for names that still contain CJK characters after offline translation.
- Translation cache stored in `translation_cache.json`.
- Section filters for materials, bones, morphs, display frames, rigid bodies, joints, and soft bodies.
- Manual review/editing before saving.
- Safe default behavior: writes to universal/English name fields unless local name overwrite is enabled.

### Requirements

- For the packaged version, run `PMXTranslateEditor.exe`.
- Python 3 on Windows is only needed if you run the source script directly.
- No runtime third-party Python package is required for normal GUI/CLI usage from source.

### Run the GUI

```powershell
python .\pmx_translate_tool.py --gui
```

Or run without arguments:

```powershell
python .\pmx_translate_tool.py
```

Basic workflow:

1. Click `Open PMX` and choose a model or stage file.
2. Select the target language: `en` or `vi`.
3. Choose sections in `Translate sections`, such as `Objects/Materials`, `Bones`, or `Morphs`.
4. Enable `Online fallback` if you want unresolved CJK names to be translated online.
5. Click `Auto Translate`.
6. Review and edit rows in the `New` field, then click `Apply Selected`.
7. Click `Save As` to write a new `.pmx` file.

By default, the tool writes only to universal/English PMX name fields. Enable `Overwrite local names` only if you also want to replace local/Japanese name fields.

### Run the CLI

Translate to English:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en
```

Translate to unaccented Vietnamese:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi
```

Preview changes without writing a file:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi --dry-run
```

Fill only empty fields:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --only-empty
```

Also rewrite local/Japanese fields:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language vi --overwrite-local
```

Translate only materials/objects:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --sections material
```

Translate only bones and morphs:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --sections bone,morph
```

Valid `--sections` values:

```text
all, material, objects, bone, morph, display, rigid_body, joint, soft_body
```

Enable online fallback:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online
python .\pmx_translate_tool.py "stage.pmx" --language vi --online
```

Set the source language for online fallback:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online --source-language zh-CN
python .\pmx_translate_tool.py "model.pmx" --language en --online --source-language ja
```

Online translation results are cached in `translation_cache.json`.

### Limitations

Offline translation cannot be perfect for every PMX file. PMX names may contain custom abbreviations, author-specific names, mixed Japanese/Chinese text, corrupted mojibake, or proper nouns. Rows that still contain CJK characters are highlighted in the GUI so they can be reviewed manually before saving.

---

## Tiếng Việt

PMX Translate Editor là công cụ nhỏ, thân thiện với Windows, dùng để sửa và dịch các trường chữ trong file model MMD/PMX. Công cụ phù hợp cho workflow với PMX Editor khi bạn cần đổi tên object tiếng Nhật hoặc tiếng Trung sang tiếng Anh hoặc tiếng Việt không dấu.

Tool chỉ ghi lại các chuỗi text trong file PMX. Tool không sửa mesh, thiết lập material, transform của bone, dữ liệu morph, rigid body, joint, physics, texture hay dữ liệu nhị phân khác của model.

### Tính năng

- Giao diện GUI bằng Tkinter.
- Có chế độ CLI để dịch nhanh bằng command line.
- Ngôn ngữ đích: tiếng Anh (`en`) và tiếng Việt không dấu (`vi`).
- Từ điển offline cho các tên PMX/MMD phổ biến.
- Có thể bật online fallback cho các tên vẫn còn ký tự CJK sau khi dịch offline.
- Cache kết quả dịch online trong `translation_cache.json`.
- Lọc theo nhóm: material, bone, morph, display frame, rigid body, joint, soft body.
- Cho phép sửa tay trước khi lưu.
- Mặc định an toàn: chỉ ghi vào trường universal/English name, trừ khi bạn bật ghi đè local name.

### Yêu cầu

- Với bản đã đóng gói, chỉ cần chạy `PMXTranslateEditor.exe`.
- Python 3 trên Windows chỉ cần thiết nếu bạn chạy trực tiếp từ source.
- Không cần cài package Python bên thứ ba để chạy GUI/CLI thông thường từ source.

### Chạy GUI

```powershell
python .\pmx_translate_tool.py --gui
```

Hoặc chạy không tham số:

```powershell
python .\pmx_translate_tool.py
```

Quy trình dùng cơ bản:

1. Bấm `Open PMX` và chọn file model hoặc stage.
2. Chọn ngôn ngữ đích: `en` hoặc `vi`.
3. Chọn nhóm cần dịch trong `Translate sections`, ví dụ `Objects/Materials`, `Bones`, hoặc `Morphs`.
4. Bật `Online fallback` nếu muốn dịch online các tên CJK mà từ điển offline chưa xử lý được.
5. Bấm `Auto Translate`.
6. Kiểm tra và sửa các dòng trong ô `New`, rồi bấm `Apply Selected`.
7. Bấm `Save As` để lưu ra file `.pmx` mới.

Mặc định tool chỉ ghi vào trường universal/English name của PMX. Chỉ bật `Overwrite local names` nếu bạn muốn thay luôn trường local/Japanese name.

### Chạy CLI

Dịch sang tiếng Anh:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en
```

Dịch sang tiếng Việt không dấu:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi
```

Xem trước thay đổi, không ghi file:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi --dry-run
```

Chỉ điền các trường đang trống:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --only-empty
```

Ghi cả trường local/Japanese:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language vi --overwrite-local
```

Chỉ dịch material/object:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --sections material
```

Chỉ dịch bone và morph:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --sections bone,morph
```

Giá trị hợp lệ của `--sections`:

```text
all, material, objects, bone, morph, display, rigid_body, joint, soft_body
```

Bật online fallback:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online
python .\pmx_translate_tool.py "stage.pmx" --language vi --online
```

Chỉ định ngôn ngữ nguồn cho online fallback:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online --source-language zh-CN
python .\pmx_translate_tool.py "model.pmx" --language en --online --source-language ja
```

Kết quả dịch online được lưu cache trong `translation_cache.json`.

### Giới hạn

Dịch offline không thể đúng 100% cho mọi file PMX. Tên trong PMX có thể là viết tắt riêng, tên do tác giả tự đặt, tiếng Nhật/Trung trộn lẫn, lỗi mojibake hoặc tên riêng. Những dòng vẫn còn ký tự CJK sẽ được tô màu trong GUI để bạn kiểm tra thủ công trước khi lưu.

---

## 中文

PMX Translate Editor 是一个适合 Windows 使用的小工具，用于编辑和翻译 MMD/PMX 模型文件中的文本字段。它适合配合 PMX Editor 使用，把日文或中文对象名称转换为英文或无声调越南语。

本工具只重写 PMX 文件中的文本字符串。它不会修改网格、材质参数、骨骼变换、Morph 数据、刚体、Joint、物理设置、贴图或其他二进制模型数据。

### 功能

- 使用 Tkinter 构建的 GUI。
- 支持 CLI 命令行模式。
- 目标语言：英文 (`en`) 和无声调越南语 (`vi`)。
- 内置面向 MMD 常用名称的离线词典。
- 可选在线 fallback，用于处理离线翻译后仍包含 CJK 字符的名称。
- 在线翻译结果会缓存到 `translation_cache.json`。
- 可按 section 过滤：material、bone、morph、display frame、rigid body、joint、soft body。
- 保存前可以手动检查和编辑。
- 默认安全行为：只写入 universal/English name 字段，除非启用 local name 覆盖。

### 需求

- 如果使用已打包版本，直接运行 `PMXTranslateEditor.exe`。
- 只有从源码脚本运行时才需要 Windows 上的 Python 3。
- 从源码正常使用 GUI/CLI 不需要第三方 Python 包。

### 启动 GUI

```powershell
python .\pmx_translate_tool.py --gui
```

或不带参数运行：

```powershell
python .\pmx_translate_tool.py
```

基本流程：

1. 点击 `Open PMX`，选择 model 或 stage 文件。
2. 选择目标语言：`en` 或 `vi`。
3. 在 `Translate sections` 中选择要翻译的部分，例如 `Objects/Materials`、`Bones` 或 `Morphs`。
4. 如果希望在线翻译离线词典无法处理的 CJK 名称，启用 `Online fallback`。
5. 点击 `Auto Translate`。
6. 检查并编辑 `New` 字段中的内容，然后点击 `Apply Selected`。
7. 点击 `Save As` 保存为新的 `.pmx` 文件。

默认情况下，工具只写入 PMX 的 universal/English name 字段。只有在你确实想替换 local/Japanese name 字段时，才启用 `Overwrite local names`。

### 使用 CLI

翻译为英文：

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en
```

翻译为无声调越南语：

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi
```

只预览变化，不写入文件：

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi --dry-run
```

只填充空字段：

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --only-empty
```

同时重写 local/Japanese 字段：

```powershell
python .\pmx_translate_tool.py "model.pmx" --language vi --overwrite-local
```

只翻译 material/object：

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --sections material
```

只翻译 bone 和 morph：

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --sections bone,morph
```

`--sections` 的有效值：

```text
all, material, objects, bone, morph, display, rigid_body, joint, soft_body
```

启用在线 fallback：

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online
python .\pmx_translate_tool.py "stage.pmx" --language vi --online
```

为在线 fallback 指定源语言：

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online --source-language zh-CN
python .\pmx_translate_tool.py "model.pmx" --language en --online --source-language ja
```

在线翻译结果会缓存到 `translation_cache.json`。

### 限制

离线翻译无法保证对所有 PMX 文件都 100% 正确。PMX 名称可能包含作者自定义缩写、自定义名称、日文和中文混合文本、mojibake 乱码或专有名词。GUI 会高亮仍包含 CJK 字符的行，方便你在保存前手动检查。

---

## 日本語

PMX Translate Editor は、MMD/PMX モデルファイル内のテキストフィールドを編集・翻訳するための、Windows 向けの小さなツールです。PMX Editor の作業で、日本語または中国語のオブジェクト名を英語またはアクセントなしベトナム語に変換したい場合に使えます。

このツールは PMX 内のテキスト文字列だけを書き換えます。メッシュ、材質設定、ボーン変形、モーフデータ、剛体、ジョイント、物理設定、テクスチャ、その他のバイナリモデルデータは変更しません。

### 機能

- Tkinter ベースの GUI。
- CLI によるコマンドライン実行。
- 翻訳先言語: 英語 (`en`) とアクセントなしベトナム語 (`vi`)。
- MMD でよく使われる名前向けのオフライン辞書。
- オフライン翻訳後も CJK 文字が残る名前に対する任意のオンライン fallback。
- オンライン翻訳結果を `translation_cache.json` にキャッシュ。
- material、bone、morph、display frame、rigid body、joint、soft body ごとのフィルタ。
- 保存前の手動確認と編集。
- 安全なデフォルト動作: local name の上書きを有効にしない限り、universal/English name フィールドだけを書き換えます。

### 必要環境

- パッケージ済み版では `PMXTranslateEditor.exe` を実行します。
- ソーススクリプトから直接実行する場合のみ、Windows 上の Python 3 が必要です。
- ソースから通常の GUI/CLI を使う場合、サードパーティ製 Python パッケージは不要です。

### GUI の起動

```powershell
python .\pmx_translate_tool.py --gui
```

または、引数なしで実行します。

```powershell
python .\pmx_translate_tool.py
```

基本的な手順:

1. `Open PMX` をクリックし、model または stage ファイルを選択します。
2. 翻訳先言語として `en` または `vi` を選択します。
3. `Translate sections` で翻訳対象を選択します。例: `Objects/Materials`、`Bones`、`Morphs`。
4. オフライン辞書で処理できない CJK 名をオンライン翻訳したい場合は、`Online fallback` を有効にします。
5. `Auto Translate` をクリックします。
6. `New` フィールドの内容を確認・編集し、`Apply Selected` をクリックします。
7. `Save As` をクリックして新しい `.pmx` ファイルとして保存します。

デフォルトでは、PMX の universal/English name フィールドだけを書き込みます。local/Japanese name フィールドも置き換えたい場合のみ、`Overwrite local names` を有効にしてください。

### CLI の使用

英語へ翻訳:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en
```

アクセントなしベトナム語へ翻訳:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi
```

ファイルを書き込まずに変更内容を確認:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language vi --dry-run
```

空のフィールドだけを埋める:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --only-empty
```

local/Japanese フィールドも書き換える:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language vi --overwrite-local
```

material/object だけを翻訳:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --sections material
```

bone と morph だけを翻訳:

```powershell
python .\pmx_translate_tool.py "model.pmx" --language en --sections bone,morph
```

`--sections` の有効な値:

```text
all, material, objects, bone, morph, display, rigid_body, joint, soft_body
```

オンライン fallback を有効にする:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online
python .\pmx_translate_tool.py "stage.pmx" --language vi --online
```

オンライン fallback の翻訳元言語を指定する:

```powershell
python .\pmx_translate_tool.py "stage.pmx" --language en --online --source-language zh-CN
python .\pmx_translate_tool.py "model.pmx" --language en --online --source-language ja
```

オンライン翻訳結果は `translation_cache.json` にキャッシュされます。

### 制限事項

オフライン翻訳だけで全ての PMX ファイルを 100% 正しく翻訳することはできません。PMX の名前には、作者独自の略語、任意の名前、日本語と中国語の混在、mojibake、固有名詞などが含まれる場合があります。GUI では CJK 文字が残っている行がハイライトされるため、保存前に手動で確認できます。
