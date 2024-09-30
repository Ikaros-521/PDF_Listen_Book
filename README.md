# PDF_Listen_Book

PDF_Listen_Book 是一个创新的工具，旨在将 PDF 文档转换为可听的音频内容。这个项目结合了 PDF 文本提取、自然语言处理和文本转语音技术，为用户提供了一种新颖的方式来"阅读"PDF文档。

## 功能特点

- PDF 到文本的转换：精确提取 PDF 文件中的文本内容。
- 文本优化：智能处理提取的文本，修复换行问题，提高可读性。
- 自定义文本处理：支持使用大语言模型（如 GPT）进行文本纠错和优化。
- 文本分块：将长文本智能分割为适合音频播放的小段落。
- AI 朗读：集成 AI Vtuber API，将文本转换为流畅的语音输出。
- 用户友好界面：使用 Gradio 构建的简洁直观的 Web 界面。

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/Ikaros-521/PDF_Listen_Book.git
   cd PDF_Listen_Book
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行主程序：
   ```
   python main.py
   ```

2. 在浏览器中打开显示的本地地址（通常是 http://127.0.0.1:7860）。

3. 在 Web 界面中：
   - 上传 PDF 文件
   - PDF转文本
   - 设置 OpenAI API 密钥和其他必要参数
   - 选择处理选项（如文本纠错、总结等）
   - 发送AI Vtuber托管文本队列和播放

## 配置

- `OpenAI API 密钥`：用于文本处理和优化。
- `AI Vtuber API 地址`：用于文本到语音的转换。
- 其他配置选项可在 Web 界面中设置。

## 许可证

本项目采用 [GPL-V3.0 许可证](LICENSE)。

## 联系方式

如有任何问题或建议，请开启一个 issue 或直接联系项目维护者。

---

希望 PDF_Listen_Book 能够为您的阅读体验带来新的可能！

## 更新日志

- 2024-09-30
   - 初版发布