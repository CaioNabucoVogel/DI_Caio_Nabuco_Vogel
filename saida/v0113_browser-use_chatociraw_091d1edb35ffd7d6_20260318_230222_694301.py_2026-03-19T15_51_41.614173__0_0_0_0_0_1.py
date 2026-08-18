@property
def model_name(self) -> str:
    if len(self.model_id) > 90:
        parts = self.model_id.split('.')
        if len(parts) >= 4:
            return f'oci-{self.provider}-{parts[3]}'
        else:
            return f'oci-{self.provider}-model'
    return self.model_id