import os
import wave
import argparse

def calculate_audio_duration(filename):
    with wave.open(filename, 'rb') as wf:
        # Extract Audio Parameters
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth() * 8  # Convert bytes to bits
        frame_rate = wf.getframerate()
        n_frames = wf.getnframes()

        # Calculate Bit Rate
        bit_rate = frame_rate * sample_width * n_channels

        # Calculate Duration
        duration_seconds = (n_frames * sample_width * n_channels) / bit_rate
        return duration_seconds

def get_audio_duration_in_folder(folder_path):
    total_duration = 0
    for filename in os.listdir(folder_path):
        if filename.endswith('.wav'):
            file_path = os.path.join(folder_path, filename)
            duration = calculate_audio_duration(file_path)
            total_duration += duration

    hours = int(total_duration // 3600)
    minutes = int((total_duration % 3600) // 60)
    seconds = int(total_duration % 60)
    return hours, minutes, seconds

def main():
    parser = argparse.ArgumentParser(description="Calculate the total duration of all WAV files in the specified folder.")
    parser.add_argument('-p', '--path', type=str, required=True, help="The path to the folder containing the WAV files")

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: The path {args.path} does not exist or is not a directory.")
        return

    hours, minutes, seconds = get_audio_duration_in_folder(args.path)
    print(f"Total audio duration in {args.path} is {hours} hours, {minutes} minutes, and {seconds} seconds.")

if __name__ == "__main__":
    main()
