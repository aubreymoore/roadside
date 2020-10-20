import glob
import subprocess
import os
import plac

@plac.opt('data_dir',abbrev='dd')
@plac.opt('date', abbrev='d')
def main(data_dir='/home/aubrey/Desktop/Guam01', date='20201001'):
    """
    Reduces frame rate to 3 FPS for each video. The original video is renamed to *_oriiginal.mp4
    """
    for video_path in glob.glob(f'{data_dir}/{date}/{date}_??????.mp4'):
        new_path = video_path.replace('.mp4', 'original.mp4')
        if os.path.exists(new_path):
            print(f'WARNING: {new_path} alreadyexists. Skipping FPS reduction.')
        else:
            os.rename(video_path, new_path)
            print(f'{video_path} --> {new_path}')
            output = subprocess.run(['ffmpeg', '-i', new_path, '-filter:v', 'fps=fps=3', video_path])
            print(output)

if __name__ == '__main__':
    import plac; plac.call(main)