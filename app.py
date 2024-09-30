import gradio as gr
import PyPDF2
import openai
import requests
import re
import time
import os


def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page_num in range(len(reader.pages)):
        text += reader.pages[page_num].extract_text()
    return text

def process_extracted_text(text):
    # 1. 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 2. 合并被错误分割的单词
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # 3. 处理句子分割
    text = re.sub(r'([.!?])\s*\n\s*', r'\1 ', text)
    
    # 4. 保留段落分隔
    text = re.sub(r'\n{2,}', '\n\n', text)
    
    return text.strip()

def convert_pdf_to_text(pdf_file, out_txt_path_input):
    try:
        # 如果文件不存在，则创建
        if not os.path.exists(out_txt_path_input):
            open(out_txt_path_input, 'w', encoding='utf-8').close()
        
        raw_text = extract_text_from_pdf(pdf_file)
        processed_text = process_extracted_text(raw_text)
        save_to_txt(processed_text, out_txt_path_input)
        return processed_text, "转换完成"
    except Exception as e:
        return None, f"转换失败: {str(e)}"

# Function to save text to txt file
def save_to_txt(text, output_filename='output.txt'):
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(text)

# Text splitting based on punctuation
def split_text_by_punctuation(text, max_length=2048):
    sentences = re.split(r'([。！？\.\?\!])', text)
    chunks = []
    current_chunk = ""
    for sentence, punct in zip(sentences[::2], sentences[1::2]):
        if len(current_chunk) + len(sentence) + len(punct) > max_length:
            chunks.append(current_chunk)
            current_chunk = sentence + punct
        else:
            current_chunk += sentence + punct
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

# Function to correct or summarize text using OpenAI with text splitting
def correct_or_summarize_text(prompt, result_text, api_key, model, api_base=None):
    text_chunks = split_text_by_punctuation(result_text)
    result = ""

    for chunk in text_chunks:
        client = openai.OpenAI(base_url=api_base, api_key=api_key)
        # Call the OpenAI chat API
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": f"{prompt}: {chunk}"},
            ],
            timeout=30,
            temperature=0.2,
            max_tokens=4096
        )

        result += resp.choices[0].message.content.strip() + "\n"

    return result, "执行完毕"

# Function to send text chunks to third-party API for playback
def send_to_third_party_api(text, third_party_api_url, output_filename):
    print("开始准备发送工作")
    text_chunks = split_text_by_punctuation(text, max_length=300)
    log_output = ""
    chunk_count = 0

    for chunk in text_chunks:
        data_json = {
            "type": "reread",
            "data": {
                "content": chunk,
                "username": "1"
            }
        }

        response = requests.post(third_party_api_url, json=data_json)
        time.sleep(1)

        if response.status_code == 200:
            print(f"发送成功: {chunk}")
            log_output += f"发送成功: {chunk}\n"
            chunk_count += 1

            if chunk_count % 60 == 0:
                remove_first_60_chunks_from_file(output_filename)
                updated_text = load_local_txt(output_filename)
                print(f"已成功发送 60 条，删除了文件中的前 60 条数据。")
                log_output += f"已成功发送 60 条，删除了文件中的前 60 条数据。\n"
                yield updated_text, log_output
                log_output = ""  # 重置日志
        else:
            log_output += f"发送失败: {chunk}, 状态码: {response.status_code}\n"

    # 处理完所有数据后的最终更新
    final_text = load_local_txt(output_filename)
    yield final_text, log_output

def remove_first_60_chunks_from_file(output_filename):
    with open(output_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 移除前60行（或者根据您的分块逻辑调整）
    if len(lines) > 60:
        lines = lines[60:]
    else:
        lines = []  # 如果文件少于60行，清空文件
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# Function to process the PDF, perform actions, and return results
def process_txt(custom_prompt, model, api_key, api_base, result_text):
        # Use OpenAI API for text correction or summarization
    result, msg = correct_or_summarize_text(custom_prompt, result_text, api_key, model, api_base)
    return result, msg  # Return None for audio output


def load_local_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read(), "加载文件成功"
    except Exception as e:
        return "", f"加载文件失败: {str(e)}"


# Gradio Interface
def gradio_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# PDF 听书软件")

        with gr.Blocks():
            with gr.Row():
                # Inputs for API configuration
                api_key_input = gr.Textbox(label="OpenAI API 密钥", placeholder="请输入 OpenAI API 密钥", value="sk-xxxx")
                api_base_input = gr.Textbox(label="OpenAI API 地址 (可选)", placeholder="http://127.0.0.1:11434/v1", value="http://127.0.0.1:11434/v1")
                model_input = gr.Textbox(label="OpenAI 模型", placeholder="如 gpt-3.5-turbo", value="qwen:1.8b-chat")
                third_party_api_input = gr.Textbox(label="AI Vtuber API 地址", placeholder="请输入AI Vtuber API 地址", value="http://127.0.0.1:8082/send")

        with gr.Blocks():
            with gr.Row():
                # File uploader for PDF
                pdf_file = gr.File(label="上传 PDF 文件", file_types=["pdf"])
                # Button for direct PDF to text conversion
                out_txt_path_input = gr.Textbox(label="输出文本文件路径", placeholder="请输入 输出文本文件路径", value="output.txt")

                convert_btn = gr.Button("PDF 转为文本")
                load_local_txt_btn = gr.Button("加载本地文本")

        with gr.Blocks():
            with gr.Row():
                # Custom prompt input
                custom_prompt = gr.Textbox(label="自定义提示词（用于纠正/总结）", placeholder="请输入自定义指令", value="请修正以下文本中的语病，并统一用中文，请不要修改太多原文内容：")
                
                llm_handle_btn = gr.Button("LLM处理文本")
                
                # Button to start processing
                send_to_ai_vtb_btn = gr.Button("AI Vtuber播放")

        with gr.Blocks():
            with gr.Row():
                # Outputs
                result_text = gr.Textbox(label="处理后的文本", interactive=True)
                run_output = gr.Textbox(label="执行结果")

        # Handle direct PDF to text conversion
        convert_btn.click(convert_pdf_to_text, inputs=[pdf_file, out_txt_path_input], outputs=[result_text, run_output])

        load_local_txt_btn.click(load_local_txt, inputs=[out_txt_path_input], outputs=[result_text, run_output])

        llm_handle_btn.click(
            process_txt,
            inputs=[custom_prompt, model_input, api_key_input, api_base_input, result_text],
            outputs=[result_text, run_output]
        )

        # Handle LLM and TTS actions with updated result_text
        send_to_ai_vtb_btn.click(
            send_to_third_party_api,
            inputs=[result_text, third_party_api_input, out_txt_path_input],
            outputs=[result_text, run_output],  # 实时更新 result_text 和 log_output
            every=60
        )

    return interface

# Launch Gradio interface
if __name__ == "__main__":
    interface = gradio_interface()
    interface.launch(inbrowser=True, share=False, server_name='127.0.0.1', show_api=True)
