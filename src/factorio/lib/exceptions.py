class RemovedIn07Warning(FutureWarning):
    def __init__(self, deprecated_feature: str, alternative: str) -> None:
        super().__init__(
            f"{deprecated_feature} is deprecated and will be removed in `v0.7.0`. Use {alternative} instead."
        )
