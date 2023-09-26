class CatalogTemplate:
    def __init__(
        self,
        namespace: str = None,
        inputs: dict = None,
        outputs: dict = None,
        artifacts: dict = None,
        templatized: dict = None,
        params: dict = None,
        unmanaged: dict = None,
    ) -> None:
        self.namespace = namespace

        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.artifacts = artifacts or {}
        self.templatized = templatized or {}
        self.params = params or {}
        self.unmanaged = unmanaged or {}


class AppCatalog:
    def __init__(
        self,
        datasets: dict = None,
        template_params: dict = None,
        catalog_params: dict = None,
    ) -> None:
        self.datasets = datasets or {}
        self.template_params = template_params or {}
        self.catalog_params = catalog_params or {}
