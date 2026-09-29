import os


class Settings:
    APP_NAME: str = "RecallOps"
    APP_VERSION: str = "1.0.0"

    HINDSIGHT_URL: str = os.getenv(
        "HINDSIGHT_URL",
        ""
    )

    HINDSIGHT_API_KEY: str = os.getenv(
        "HINDSIGHT_API_KEY",
        ""
    )

    GROQ_API_KEY: str = os.getenv(
        "GROQ_API_KEY",
        ""
    )


settings = Settings()