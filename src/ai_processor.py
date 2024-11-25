from typing import List
import openai
import os


class AIProcessor:

    # get model from ENV var or default to gpt-4o
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    summary_language = os.getenv("SUMMARY_LANGUAGE", "en")
    num_vocabulary_words = os.getenv("NUM_VOCABULARY_WORDS", 30)
    vocab_translation_language = os.getenv("VOCAB_TRANSLATION_LANGUAGE", "en")

    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def transcribe_chunk(self, chunk_path: str) -> str:
        """Transcribe audio chunk using OpenAI Whisper API"""
        try:
            with open(chunk_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return transcript["text"]

        except Exception as e:
            raise Exception(f"Error transcribing chunk: {str(e)}")

    def summarize_text(self, text: str) -> str:
        """Summarize text using OpenAI GPT"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes podcast content.",
                    },
                    {
                        "role": "user",
                        "content": f"Please provide a concise summary of the following podcast transcript (summary language: {self.summary_language}). ONLY REPLY WITH THE SUMMARY!\n\n{text}",
                    },
                ],
            )
            return response.choices[0].message["content"]

        except Exception as e:
            raise Exception(f"Error summarizing text: {str(e)}")

    def extract_vocabulary(self, text: str) -> List[str]:
        """Extract key vocabulary using OpenAI GPT"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts key vocabulary from text.",
                    },
                    {
                        "role": "user",
                        "content": f"Please extract a list of {self.num_vocabulary_words} key vocabulary words from this text, focusing on important terms and concepts. Reply as a CSV with the following format: `word, example, translation`. The example should be an occurence in the podcast. The translation should be in the following language: '{self.vocab_translation_language}'. ONLY REPLY WITH THE CSV!\n\n{text}",
                    },
                ],
            )
            text = response.choices[0].message["content"].split("\n")
            # remove csv md formatting
            if text[0] == "```csv":
                text = text[1:]
            if text[-1] == "```":
                text = text[:-1]

            return text

        except Exception as e:
            raise Exception(f"Error extracting vocabulary: {str(e)}")
