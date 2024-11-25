import os
import json
import shutil
from src.downloader import PodcastDownloader
from src.audio_processor import AudioProcessor
from src.ai_processor import AIProcessor


class PodcastProcessor:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.downloader = PodcastDownloader()
        self.audio_processor = AudioProcessor()
        self.ai_processor = AIProcessor(api_key)

    def process_podcast(self, url: str) -> dict:
        """Process entire podcast and return results"""
        temp_dir = "temp_chunks"
        audio_path = None

        try:
            # Download
            print("Downloading podcast...")
            audio_path = self.downloader.download_podcast(url)

            # Split
            print("Splitting audio into chunks...")
            chunks = self.audio_processor.split_audio(audio_path)

            # Transcribe
            print("Transcribing chunks...")
            full_transcript = ""
            for chunk in chunks:
                transcript = self.ai_processor.transcribe_chunk(chunk)
                full_transcript += transcript + " "

            # Summarize
            print("Generating summary...")
            summary = self.ai_processor.summarize_text(full_transcript)

            # Extract vocabulary
            print("Extracting vocabulary...")
            vocabulary = self.ai_processor.extract_vocabulary(full_transcript)

            results = {
                "transcript": full_transcript.strip(),
                "summary": summary.strip(),
                "vocabulary": [v.strip() for v in vocabulary if v.strip()],
            }

            return results

        except Exception as e:
            raise Exception(f"Error processing podcast: {str(e)}")

        finally:
            # Clean up
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def main():
    try:
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = input("Please enter your OpenAI API key: ").strip()
            if not api_key:
                raise ValueError("OpenAI API key is required")

        # Get podcast URL
        url = input("Please enter the YouTube URL: ").strip()
        if not url:
            raise ValueError("Podcast URL is required")

        default_out_file = "out.json"
        out_file = input(
            f"Please enter the output file name (default: {default_out_file}): "
        ).strip()
        if not out_file:
            out_file = default_out_file

        # Process podcast
        processor = PodcastProcessor(api_key)
        results = processor.process_podcast(url)

        # Save results
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\nProcessing complete! Results saved to " + out_file)
        print("\nSummary:")
        print(results["summary"])
        print("\nKey Vocabulary:")
        for row in results["vocabulary"]:
            print(f"{row}")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
