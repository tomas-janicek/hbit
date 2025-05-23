from hbit import clients, extractors, services, summaries, types


class ImperativeEvaluator:
    def __init__(self, registry: services.ServiceContainer) -> None:
        self.registry = registry
        self.model = registry.get_service(types.DefaultModel)
        self.summary_service = registry.get_service(summaries.SummaryService)
        self.device_extractor = registry.get_service(extractors.DeviceExtractor)
        self.patch_extractor = registry.get_service(extractors.PatchExtractor)
        self.client = registry.get_service(clients.HBITClient)

    def get_device_security_answer(self, input: str) -> str:
        device_identifier = self.device_extractor.extract_device_identifier(input)
        patch_build = self.patch_extractor.extract_patch_build(input)

        if not patch_build:
            raise ValueError(
                "Could not figure out what patch the user is asking about."
            )

        if not device_identifier:
            evaluation = self.client.get_patch_evaluation(patch_build)
        else:
            evaluation = self.client.get_device_evaluation(
                device_identifier, patch_build
            )

        summary = self.summary_service.generate_summary(evaluation)

        return summary
