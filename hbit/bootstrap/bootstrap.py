from hbit import (
    enums,
    services,
)

from .model_factory import ModelServiceFactory
from .service_factory import ServicesFactory
from .vector_db_factory import VectorDBFactory


def create_services(
    device_extractor_type: enums.DeviceExtractorType,
    patch_extractor_type: enums.PatchExtractorType,
    summary_service_type: enums.SummaryServiceType,
    model_provider: enums.ModelProvider = enums.ModelProvider.OPEN_AI,
) -> services.ServiceContainer:
    registry = services.ServiceContainer()
    service_factory = ServicesFactory(registry)
    model_factory = ModelServiceFactory(registry)
    vector_db_factory = VectorDBFactory(registry)

    model_factory.add_models(model_provider)

    service_factory.add_db()
    service_factory.add_requests()
    service_factory.add_client()
    service_factory.add_saver()
    service_factory.add_device_extractor(device_extractor_type)
    service_factory.add_patch_extractor(patch_extractor_type)
    service_factory.add_summary_service(summary_service_type)

    vector_db_factory.add_vector_db()
    vector_db_factory.add_text_splitter()

    return registry
