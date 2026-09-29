import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("edugenie.gemini")

class GeminiServiceError(Exception):
    """Custom exception for Gemini service errors with user-friendly messages."""
    def __init__(self, message: str, status_code: int = 500, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        env_model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite").strip()
        # Candidate model chain for high reliability
        self.candidate_models = [
            env_model,
            "gemini-3.1-flash-lite",
            "gemini-3.8-flash",
            "gemini-3.5-flash-lite",
            "gemini-flash-latest"
        ]
        # Deduplicate while preserving order
        self.model_chain = list(dict.fromkeys(self.candidate_models))
        self.default_model = self.model_chain[0]
        self._is_configured = False
        self._init_client()

    def _init_client(self):
        """Initializes the google.generativeai client if API key is provided."""
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.warning("GEMINI_API_KEY is not set or using placeholder value.")
            self._is_configured = False
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._is_configured = True
            logger.info("Gemini API client configured successfully.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini client: {e}")
            self._is_configured = False

    def is_configured(self) -> bool:
        """Returns True if the API key is configured."""
        return self._is_configured and bool(self.api_key) and self.api_key != "your_api_key_here"

    def clean_json_markdown(self, raw_text: str) -> str:
        """Removes markdown code fences (```json ... ```) from model output."""
        text = raw_text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
    ) -> str:
        """Generates text using Gemini with multi-model fallback and error recovery."""
        if not self.is_configured():
            raise GeminiServiceError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file.",
                status_code=503
            )

        import google.generativeai as genai

        last_error = None
        for model_name in self.model_chain:
            try:
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )

                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=generation_config,
                    system_instruction=system_instruction if system_instruction else None,
                )

                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()

            except Exception as e:
                error_str = str(e)
                last_error = error_str
                logger.warning(f"Model '{model_name}' encountered: {error_str[:120]}. Trying fallback if available...")

                if "API_KEY_INVALID" in error_str or "unregistered" in error_str.lower():
                    raise GeminiServiceError(
                        "Invalid Gemini API key. Please check your GEMINI_API_KEY in the .env file.",
                        status_code=401
                    )
                # Continue loop to try next candidate model in model_chain

        logger.error(f"All candidate models exhausted. Last error: {last_error}")
        raise GeminiServiceError(
            "EduGenie couldn't generate a response right now. Please try again in a moment.",
            status_code=500,
            detail=last_error
        )

    def generate_json(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Any:
        """Generates structured JSON response, stripping markdown fences and verifying JSON."""
        full_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT: Output MUST be valid JSON only. "
            "Do NOT include markdown formatting or backticks around the JSON."
        )

        raw_output = self.generate_text(
            prompt=full_prompt,
            system_instruction=system_instruction,
            temperature=temperature,
        )

        cleaned_output = self.clean_json_markdown(raw_output)

        try:
            return json.loads(cleaned_output)
        except json.JSONDecodeError as json_err:
            logger.warning(f"Initial JSON decode failed: {json_err}. Attempting regex extraction.")
            # Try to extract the first {...} or [...] block
            match = re.search(r"(\[.*\]|\{.*\})", cleaned_output, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception as inner_err:
                    logger.error(f"Regex JSON fallback failed: {inner_err}")

            logger.error(f"Failed to parse model JSON: {raw_output}")
            raise GeminiServiceError(
                "EduGenie encountered an issue formatting the educational data. Please try again.",
                status_code=500,
                detail=f"JSON Decode Error: {str(json_err)}"
            )

# Singleton service instance
gemini_service = GeminiService()
