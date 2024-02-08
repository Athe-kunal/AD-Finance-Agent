from get_transcripts import generate_transcripts
from download_utils import download_and_convert_to_mp3
from fire import Fire
from functools import partial
import concurrent.futures


def run_main(
    yt_links_filename,
    output_path,
    max_workers: int = 30,
    only_transcripts: bool = False,
):
    if not only_transcripts:
        print(
            f"Started generting the audio files: Please check the folder {output_path}"
        )
        with open(yt_links_filename, "r") as f:
            yt_links = f.readlines()
        download_func = partial(download_and_convert_to_mp3, output_path=output_path)
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers
        ) as executor:
            results = executor.map(download_func, yt_links)
        print(f"Started transcribing the audio files in the folder {output_path}")
        generate_transcripts(output_path)
    else:
        print(f"Started transcribing the audio files in the folder {output_path}")
        generate_transcripts(output_path)


if __name__ == "__main__":
    Fire(run_main)
