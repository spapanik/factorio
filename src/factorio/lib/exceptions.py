class RemovedIn08Warning(FutureWarning):  # pragma: no cover
    version = "0.8.0"

    def __init__(self, deprecated_feature: str, alternative: str) -> None:
        super().__init__(
            f"{deprecated_feature} is deprecated and will be removed in "
            f"`v{self.version}`. Use {alternative} instead."
        )
