def _get_oci_client(self) -> GenerativeAiInferenceClient:
    """Get the OCI GenerativeAiInferenceClient following your working example."""
    if not hasattr(self, '_client'):
        if self.auth_type == 'API_KEY':
            config = oci.config.from_file('~/.oci/config', self.auth_profile)
            self._client = GenerativeAiInferenceClient(config=config, service_endpoint=self.service_endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240))
        elif self.auth_type == 'INSTANCE_PRINCIPAL':
            config = {}
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            self._client = GenerativeAiInferenceClient(config=config, signer=signer, service_endpoint=self.service_endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240))
        elif self.auth_type == 'RESOURCE_PRINCIPAL':
            config = {}
            signer = oci.auth.signers.get_resource_principals_signer()
            self._client = GenerativeAiInferenceClient(config=config, signer=signer, service_endpoint=self.service_endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240))
        else:
            config = oci.config.from_file('~/.oci/config', self.auth_profile)
            self._client = GenerativeAiInferenceClient(config=config, service_endpoint=self.service_endpoint, retry_strategy=oci.retry.NoneRetryStrategy(), timeout=(10, 240))
    return self._client