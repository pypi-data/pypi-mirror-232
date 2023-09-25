import os.path

import ffmpy
from kit.file_utils import Files
import os
from pydub import AudioSegment
from pydub.utils import make_chunks
from pathlib import Path
from moviepy.editor import VideoFileClip, concatenate_videoclips
import subprocess


class VideoHandler:
    @classmethod
    def video_format_converter(cls, source_video, target_video):
        video = ffmpy.FFmpeg(
            inputs={source_video: None},
            outputs={target_video: None})
        video.run()

    @classmethod
    def merge_videos(cls, videos, target_file):
        all = []
        for i in videos:
            all.append(VideoFileClip(i))
        final_video = concatenate_videoclips(all)
        final_video.write_videofile(target_file)

    @classmethod
    def audio_format_converter(cls, source_file, target_file):
        cmd = 'ffmpeg -y -i ' + source_file + ' -acodec pcm_s16le -f s16le -ac 1 -ar 16000 ' + target_file
        os.system(cmd)

    @classmethod
    def cut_video_by_second(cls, source_file, target_file, start_s, end_s):
        clipOri = VideoFileClip(source_file).subclip(start_s, end_s)
        clipOri.write_videofile(target_file)

    @classmethod
    def extract_gif_from_video(cls, source_file, target_file, start_s, end_s, size):
        clipOri = VideoFileClip(source_file).subclip(start_s, end_s)
        clipOri.write_gif(target_file, size)

    @classmethod
    def extract_audio_from_video(cls, source_video, target_audio):
        audio = AudioSegment.from_file(source_video)
        audio.export(target_audio, format=Files.get_file_format(target_audio))

    @classmethod
    def alter_video_size(cls, video, dest=None, aspect='16:9', scale='1280:720'):
        print('altering: ' + video)
        if dest is None:
            dest = os.path.join(Files.get_file_dir_path(video),
                                'altered_' + Files.get_file_name(video) + '.' + Files.get_file_format(video))
        resize = 'ffmpeg -i {} -aspect {} -vf scale={} {}'.format(video, aspect, scale, dest)
        subprocess.call(resize, shell=True)

    @classmethod
    def embed_subtitle_to_video(cls, video, subtitle, dest_file=None):
        print('embedding: ' + video)
        sub = '\'' + subtitle.replace('\\', '\\\\').replace(':', '\:') + '\''
        if dest_file is None:
            dest_file = os.path.join(Files.get_file_dir_path(video),
                                     'embed_' + Files.get_file_name(video) + '.' + Files.get_file_format(video))
        cmd_line = '''ffmpeg -i {} -vf subtitles="{}" {}'''.format(video, sub, dest_file)
        subprocess.call(cmd_line, shell=True)


class AudioHandler:

    @classmethod
    def split_audio_by_ms(cls, source_file, destination, duration_ms):
        f = Files.get_file_format(source_file)
        d = Files.get_file_name(source_file).replace(' ', '')
        audio = AudioSegment.from_file(source_file, format=f)

        chunks = make_chunks(audio, duration_ms)
        for i, chunk in enumerate(chunks):
            path = os.path.join(destination, d)
            Path(path).mkdir(parents=True, exist_ok=True)
            chunk_name = os.path.join(destination, d, '{}.{}'.format(i, f))
            chunk.export(chunk_name, format=f)

    @classmethod
    def split_audio_by_second(cls, source_file, destination, duration_s):
        AudioHandler.split_audio_by_ms(source_file, destination, duration_s * 1000)

    @classmethod
    def cut_audio_by_ms(cls, source_file, destination_file, start_ms, end_ms):
        f = Files.get_file_format(source_file)
        n = Files.get_file_name(source_file)
        audio = AudioSegment.from_file(source_file, format=f)
        slice = audio[start_ms:end_ms]
        slice.export(destination_file, format=f)

    @classmethod
    def cut_audio_by_second(cls, source_file, destination, start_s, end_s):
        AudioHandler.cut_audio_by_ms(source_file, destination, start_s * 1000, end_s * 1000)

    @classmethod
    def merge_audios(cls, audios, target_file):
        all_files = []
        for file in audios:
            all_files.append(AudioSegment.from_file(file))

        audio_merged = all_files[0]
        del all_files[0]
        for i in all_files:
            audio_merged += i
        audio_merged.export(target_file, format=Files.get_file_format(target_file))

