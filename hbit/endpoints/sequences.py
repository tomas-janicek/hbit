from hbit import evaluations, extractors, services, summaries, types


class ImperativeEvaluator:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry
        self.model = registry.get_service(types.DefaultModel)
        self.summary_service = registry.get_service(summaries.SummaryService)
        self.device_extractor = registry.get_service(extractors.DeviceExtractor)
        self.patch_extractor = registry.get_service(extractors.PatchExtractor)
        self.evaluation_service = registry.get_service(
            evaluations.DeviceEvaluationService
        )

    def get_device_security_answer(self, question: str) -> str:
        device_identifier = self.device_extractor.extract_device_identifier(question)
        if not device_identifier:
            raise ValueError(
                "Could not figure out what device the user is asking about."
            )

        patch_build = self.patch_extractor.extract_patch_build(question)
        if not patch_build:
            raise ValueError(
                "Could not figure out what patch the user is asking about."
            )

        evaluation = self.evaluation_service.get_trimmed_evaluation(
            device_identifier, patch_build
        )
        summary = self.summary_service.generate_summary(evaluation)

        return summary
