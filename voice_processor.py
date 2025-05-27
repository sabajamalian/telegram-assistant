import os
import tempfile
from pathlib import Path
import openai
from pydub import AudioSegment
import ffmpeg
from tasks.task_manager import TaskManager

class VoiceProcessor:
    def __init__(self):
        """Initialize the voice processor with OpenAI API key."""
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.task_manager = TaskManager(self.client)

    async def process_voice(self, voice_file_path: str) -> tuple[str, dict]:
        """
        Process a voice file: convert to mp3, transcribe using Whisper, and handle the task.
        
        Args:
            voice_file_path (str): Path to the voice file
            
        Returns:
            tuple[str, dict]: Task type and response
        """
        # Convert to mp3 if needed
        mp3_path = self._convert_to_mp3(voice_file_path)
        
        try:
            # First, transcribe the audio using Whisper
            with open(mp3_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            # Then, use ChatGPT to translate and improve the transcription
            translation_prompt = f"""Please translate the following text to English, maintaining the original meaning and context as accurately as possible. If the text is already in English, improve its grammar and clarity while keeping the original meaning:

{transcription}

Please provide only the translated/improved text without any additional explanations."""

            translation_response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional translator and language expert. Your task is to translate text to English or improve English text while maintaining the original meaning and context."},
                    {"role": "user", "content": translation_prompt}
                ],
                temperature=0.3
            )
            
            translated_text = translation_response.choices[0].message.content.strip()
            
            # Process the task
            task_type, task_response = await self.task_manager.process_task(translated_text)
            
            return task_type, task_response
            
        finally:
            # Clean up temporary files
            if os.path.exists(mp3_path):
                os.remove(mp3_path)

    def _convert_to_mp3(self, input_path: str) -> str:
        """
        Convert audio file to mp3 format.
        
        Args:
            input_path (str): Path to the input audio file
            
        Returns:
            str: Path to the converted mp3 file
        """
        # Create a temporary file for the mp3
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f"converted_{Path(input_path).stem}.mp3")
        
        # Convert to mp3 using ffmpeg
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path)
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
        
        return output_path 