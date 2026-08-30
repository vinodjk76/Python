"""
Live Microphone Speech-to-Text (fully offline)
------------------------------------------------
Captures audio from your microphone in real time and transcribes it
using a local Whisper model via faster-whisper. No internet connection
is required once the model has been downloaded the first time.

Usage:
    python speech_to_text.py
    python speech_to_text.py --model small --chunk 4 --language en

Press Ctrl+C to stop.
"""

import argparse
import queue
import sys
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000  # Whisper expects 16kHz mono audio
CHANNELS = 1


def parse_args():
    parser = argparse.ArgumentParser(description="Offline live speech-to-text using Whisper")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size. Smaller = faster but less accurate. Default: base",
    )
    parser.add_argument(
        "--chunk",
        type=float,
        default=4.0,
        help="Seconds of audio to capture before transcribing each chunk. Default: 4.0",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Force a language code (e.g. 'en'). Default: auto-detect.",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Input device index. Run with --list-devices to see options.",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices and exit.",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Precision for inference: int8 (fastest/CPU-friendly), float16, float32. Default: int8",
    )
    parser.add_argument(
        "--samplerate",
        type=int,
        default=None,
        help="Force the input samplerate (Hz) to record at, e.g. 44100 or 48000. "
        "Default: auto-detect the device's native rate.",
    )
    return parser.parse_args()


def list_devices():
    print(sd.query_devices())


def resample_to_16k(segment: np.ndarray, orig_rate: int) -> np.ndarray:
    """Simple linear-interpolation resample from orig_rate to 16kHz."""
    if orig_rate == SAMPLE_RATE:
        return segment
    duration = len(segment) / orig_rate
    target_len = int(duration * SAMPLE_RATE)
    orig_positions = np.linspace(0, len(segment) - 1, num=len(segment))
    target_positions = np.linspace(0, len(segment) - 1, num=target_len)
    return np.interp(target_positions, orig_positions, segment).astype(np.float32)


def main():
    args = parse_args()

    if args.list_devices:
        list_devices()
        return

    print(f"Loading Whisper model '{args.model}' (this may take a moment the first time)...")
    model = WhisperModel(args.model, device="cpu", compute_type=args.compute_type)
    print("Model loaded. Listening... (Ctrl+C to stop)\n")

    audio_queue: "queue.Queue[np.ndarray]" = queue.Queue()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"[audio warning] {status}", file=sys.stderr)
        audio_queue.put(indata.copy())

    # Determine the samplerate to actually record at.
    if args.samplerate:
        record_rate = args.samplerate
    else:
        try:
            device_info = sd.query_devices(args.device, "input")
            record_rate = int(device_info["default_samplerate"])
        except Exception:
            record_rate = SAMPLE_RATE

    if record_rate != SAMPLE_RATE:
        print(f"Recording at device native rate {record_rate}Hz, will resample to {SAMPLE_RATE}Hz for Whisper.")

    chunk_samples = int(args.chunk * record_rate)

    try:
        with sd.InputStream(
            samplerate=record_rate,
            channels=CHANNELS,
            dtype="float32",
            device=args.device,
            callback=audio_callback,
        ):
            buffer = np.empty((0,), dtype=np.float32)

            while True:
                data = audio_queue.get()
                buffer = np.concatenate([buffer, data[:, 0]])

                while len(buffer) >= chunk_samples:
                    raw_segment = buffer[:chunk_samples]
                    buffer = buffer[chunk_samples:]
                    segment = resample_to_16k(raw_segment, record_rate)

                    # Skip near-silent chunks to save time and avoid junk output
                    if np.abs(segment).mean() < 0.003:
                        continue

                    segments, info = model.transcribe(
                        segment,
                        language=args.language,
                        beam_size=1,
                        vad_filter=True,
                    )
                    text = "".join(seg.text for seg in segments).strip()
                    if text:
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"[{timestamp}] {text}")

    except KeyboardInterrupt:
        print("\nStopped listening.")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()