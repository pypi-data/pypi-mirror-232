import os
import argparse
import logging
import tempfile
import toml
import subprocess

__author__ = "makes"
__version__ = "0.0.1"
__license__ = "MIT"

DEFAULT_X = 1920
DEFAULT_Y = 1080
DEFAULT_FPS = 29.97
DEFAULT_VIDEO_CODEC = "libx264"
DEFAULT_CRF = 23
DEFAULT_AUDIO_CODEC = "aac"
DEFAULT_AUDIO_BITRATE = "256k"
DEFAULT_OUTPUT_FILE = 'out.mp4'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

logger.addHandler(ch)

def timeindex_to_s(t):
    if type(t) == str:
        t = t.split(':')
    elif type(t) != list:
        t = [t]
    if len(t) == 3:
        return float(t[0]) * 3600 + timeindex_to_s(t[1:])
    elif len(t) == 2:
        return float(t[0]) * 60 + timeindex_to_s(t[1:])
    elif len(t) == 1:
        return float(t[0])
    else:
        raise ValueError("Invalid time index")

class Clip:
    def __init__(self, seq, infile, start, stop):
        self.seq = seq
        self.infile = infile
        try:
            self.start = timeindex_to_s(start)
            self.stop = timeindex_to_s(stop)
        except ValueError:
            logger.error("Invalid time index in video specification file. Exiting.")
            exit(1)

class OutputVideo:
    def __init__(self,
                 outfile,
                 clips,
                 x=1920,
                 y=1080,
                 fps=29.97,
                 video_codec="libx264",
                 crf=23,
                 audio_codec="aac",
                 audio_bitrate="256k"):
        self.output_file = outfile
        self.x = x
        self.y = y
        self.fps = fps
        self.video_codec = video_codec
        self.crf = crf
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate
        self.clips = []
        for seq, c in enumerate(clips):
            start, stop = c['interval']
            self.clips.append(Clip(seq, c['file'], start, stop))
        self.files = self._input_streams(list({c.infile for c in self.clips}))

    @classmethod
    def from_file(cls, f, output_file = None, overwrite=False):
        vidspec = toml.load(f)
        try:
            output = vidspec['output']
            clips = vidspec['clip']
        except KeyError:
            logger.error("Invalid video specification file. Exiting.")
            exit(1)
        if output_file is None:
            if 'path' in output:
                output_file = output['path']
            else:
                output_file = DEFAULT_OUTPUT_FILE
        x = DEFAULT_X if 'x' not in output else output['x']
        y = DEFAULT_Y if 'y' not in output else output['y']
        fps = DEFAULT_FPS if 'fps' not in output else output['fps']
        video_codec = DEFAULT_VIDEO_CODEC if 'video_codec' not in output else output['video_codec']
        crf = DEFAULT_CRF if 'crf' not in output else output['crf']
        audio_codec = DEFAULT_AUDIO_CODEC if 'audio_codec' not in output else output['audio_codec']
        audio_bitrate = DEFAULT_AUDIO_BITRATE if 'audio_bitrate' not in output else output['audio_bitrate']

        return cls(output_file, clips, x, y, fps, video_codec, crf, audio_codec, audio_bitrate)

    def _input_streams(self, filelist):
        ret = {}
        for i, f in enumerate(filelist):
            ret[f] = {'fileid': i, 'clips': [] }
            for c in self.clips:
                if c.infile == f:
                    ret[f]['clips'].append(c)
        return ret

    def input_list(self):
        inputs = []
        for f in self.files:
            inputs.append('-i')
            inputs.append(f'{f}')
        return inputs

    def filter_script(self):
        filter = ''
        for s in self.files.values():
            fid = s['fileid']

            # video
            filter += f'[{fid}:v]setpts=PTS-STARTPTS[bv{fid}];\n'
            n_split = len(s['clips'])
            sp = f'split={n_split}' if n_split >= 2 else 'null'
            filter += f'[bv{fid}]{sp}'
            splits = [f'[v{c.seq}]' for c in s["clips"]]
            filter += ''.join(splits) + ';\n'

            x = self.x
            y = self.y
            fps = self.fps

            for c in s["clips"]:
                filter += f'[v{c.seq}]select=\'between(t\,{c.start}\,{c.stop})\','
                filter += f'scale={x}:{y}:force_original_aspect_ratio=decrease,'
                filter += f'pad={x}:{y}:-1:-1:color=black,'
                filter += f'setpts=N/FRAME_RATE/TB,fps={fps},fifo[{c.seq}v];\n'

            # audio
            sp = f'asplit={n_split}' if n_split >= 2 else 'anull'
            filter += f'[{fid}:a]{sp}'
            splits = [f'[a{c.seq}]' for c in s["clips"]]
            filter += ''.join(splits) + ';\n'
        
            for c in s["clips"]:
                filter += f'[a{c.seq}]aselect=\'between(t\,{c.start}\,{c.stop})\','
                filter += f'asetpts=N/SR/TB,afifo[{c.seq}a];\n'

        n_clip = len(self.clips)
        for c in self.clips:
            filter += f'[{c.seq}v][{c.seq}a]'
        filter += f'concat=n={n_clip}:v=1:a=1[outv][outa]'

        return filter

    def ffmpeg_cmd(self, filter_script):
        cmd = ['ffmpeg', '-nostdin'] + self.input_list()
        cmd += ['-filter_complex_script', filter_script]
        cmd += ['-map', '[outv]', '-map', '[outa]']
        cmd += ['-vcodec', self.video_codec, '-crf', str(self.crf)]
        cmd += ['-acodec', self.audio_codec, '-b:a', str(self.audio_bitrate)]
        cmd += [self.output_file]
        return cmd

    def run(self, overwrite=False, test=False):
        with tempfile.TemporaryDirectory() as tmpdir:
            scriptfile = os.path.join(tmpdir, 'cutter.flt')
            script = self.filter_script()
            logger.debug("\nFFmpeg Filter script:\n\n" + script)
            with open(scriptfile, 'w', encoding='utf8') as f:
                f.write(script)
            cmd = self.ffmpeg_cmd(scriptfile)
            logger.debug("\nFFmpeg command:\n\n" + str(cmd))
            if not test:
                if os.path.exists(self.output_file):
                    if not overwrite:
                        logger.error(f'Output file {self.output_file} already exists. Exiting.')
                        exit(1)
                    else:
                        os.unlink(self.output_file)
                subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))
    parser.add_argument("vidspec", help="Video specification TOML file")
    parser.add_argument("-o", "--output", action="store", dest="output")
    parser.add_argument("--overwrite", action="store_true", dest="overwrite", default=False)
    parser.add_argument("--test", action="store_true", dest="test", default=False)
    args = parser.parse_args()
    if args.test:
        logger.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    v = OutputVideo.from_file(args.vidspec, output_file=args.output)
    v.run(args.overwrite, args.test)

if __name__ == "__main__":
    main()
