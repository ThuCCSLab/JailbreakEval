# %%
from urllib.parse import urljoin
import copy
from typing import Any, Dict, List, Optional, Union

from jailbreakeval.services.text_classification.service_base import TextClassificationService
from googleapiclient import discovery
from googleapiclient.discovery import Resource


class PerspectiveTextClassificationService(TextClassificationService, service_type="perspective"):
    def __init__(
        self,
        resource: Optional[Resource] = None,
        attributes: Optional[Union[str, List[str]]] = None,
        predict_kwargs: Optional[Dict[str, Any]] = None,
        **client_kwargs,
    ) -> None:
        super().__init__(None, predict_kwargs)

        self.predict_kwargs = predict_kwargs or {}
        attributes = [attributes] if isinstance(attributes, str) else attributes
        if attributes and "requestedAttributes" not in self.predict_kwargs:
            self.predict_kwargs["requestedAttributes"] = {attribute: {} for attribute in attributes}
        elif attributes:
            raise ValueError("Can not set `attributes` when key `requestedAttributes` exists in predict_kwargs")
        elif "requestedAttributes" not in self.predict_kwargs:
            raise ValueError("Either `attributes` or key `requestedAttributes` in predict_kwargs should exist")

        if resource:
            self.resource = resource
        else:
            api_key = client_kwargs.pop("api_key", None)
            base_url = client_kwargs.pop("base_url", None)

            discoveryServiceUrl = urljoin(base_url, "$discovery/rest?version={apiVersion}") if base_url else None

            self.resource = discovery.build(
                "commentanalyzer",
                "v1alpha1",
                static_discovery=False,
                developerKey=api_key,
                discoveryServiceUrl=discoveryServiceUrl,
            ).comments()

            if base_url:
                self.resource._baseUrl = base_url

    def predict(self, text: str, **override_predict_kwargs) -> Dict:
        predict_kwargs = copy.deepcopy(self.predict_kwargs)
        for k in override_predict_kwargs:
            if k in predict_kwargs:
                predict_kwargs.pop(k)
        return self.resource.analyze(body={"comment": {"text": text}, **predict_kwargs}).execute()
