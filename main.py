import re
import os
import pandas as pd
from docx import Document
from moviepy.editor import VideoFileClip, AudioFileClip
from funasr import AutoModel

# 设置 ffmpeg 的路径
os.environ['FFMPEG_BINARY'] = 'E:/wjh/项目/音频视频分割情感分析/bin/ffmpeg.exe'

# 读取 Word 文件中的文本内容
def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# 提取时间片段 (开始时间和结束时间) 的函数
def extract_time_segments(text):
    time_pattern = r'(\d{2}:\d{2}:\d{1,2}\.\d{3}) --> (\d{2}:\d{2}:\d{1,2}\.\d{3})'
    return re.findall(time_pattern, text)

# 将时间字符串转换为秒数
def time_to_seconds(time_str):
    h, m, s = time_str.split(':')
    s, ms = map(float, s.split('.'))
    return int(h) * 3600 + int(m) * 60 + s + ms / 1000

# 根据时间段剪辑视频并保存
import subprocess

def split_video_ffmpeg(video_file, time_segments, output_dir):
    for idx, (start, end) in enumerate(time_segments):
        output_video_path = f"{output_dir}/video_clip_{idx + 1}.mp4"
        command = [
            'ffmpeg',
            '-i', video_file,
            '-ss', start,
            '-to', end,
            '-c', 'copy',  # 使用原始编码
            output_video_path
        ]
        subprocess.run(command, check=True)
        print(f"视频片段 {idx + 1} 已保存: {output_video_path}")

    return [f"{output_dir}/video_clip_{idx + 1}.mp4" for idx in range(len(time_segments))]


# 根据时间段剪辑音频并保存
def split_audio(audio_file, time_segments, output_dir):
    audio = AudioFileClip(audio_file)

    audio_clips = []
    for idx, (start, end) in enumerate(time_segments):
        start_time = time_to_seconds(start)
        end_time = time_to_seconds(end)

        # 截取音频片段
        audio_clip = audio.subclip(start_time, end_time)
        output_audio_path = f"{output_dir}/audio_clip_{idx + 1}.wav"
        audio_clip.write_audiofile(output_audio_path)
        audio_clips.append(output_audio_path)
        print(f"音频片段 {idx + 1} 已保存: {output_audio_path}")

    return audio_clips

# 进行情感分析并保存结果
def analyze_emotions(audio_clips, output_csv):
    model = AutoModel(model="iic/emotion2vec_base_finetuned")
    results = []

    for idx, audio_clip in enumerate(audio_clips):
        rec_result = model.generate(audio_clip, output_dir="./outputs", granularity="utterance")
        print(f"音频片段 {idx + 1} 的情感分析结果：{rec_result}")

        scores = rec_result[0]["scores"]

        # 获取最大得分
        max_score = max(scores)
        print(scores)
        print(max_score)
        # 获取最大得分的索引
        max_score_index = scores.index(max_score)
        print(max_score_index)

        result=rec_result[0]["labels"][max_score_index]
        print("音频分析后，情感基调为：" + result)

        results.append({
                'clip': audio_clip,
                'feats': result
            })

    # 保存到 CSV
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"情感分析结果已保存到: {output_csv}")

# 主程序
if __name__ == "__main__":
    # Word 文件路径
    docx_file = 'test.docx'
    # 视频文件路径
    video_file = 'test.mp4'
    # 音频文件路径
    audio_file = '1.wav'
    # 输出文件夹
    output_dir = './output_clips'
    os.makedirs(output_dir, exist_ok=True)

    # 从 Word 中读取文本内容
    doc_text = read_docx(docx_file)

    # 提取时间片段
    time_segments = extract_time_segments(doc_text)
    print(time_segments)

    # 分割视频
    video_clips = split_video_ffmpeg(video_file, time_segments, output_dir)

    # 分割音频
    audio_clips = split_audio(audio_file, time_segments, output_dir)

    # 分析情感并保存到 CSV
    output_csv = './emotion_analysis_results.csv'
    analyze_emotions(audio_clips, output_csv)
