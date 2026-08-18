class PermissionsWatchdog(BaseWatchdog):
    """Grants browser permissions when browser connects."""
    LISTENS_TO: ClassVar[list[type[BaseEvent]]] = [BrowserConnectedEvent]
    EMITS: ClassVar[list[type[BaseEvent]]] = []

    async def on_BrowserConnectedEvent(self, event: BrowserConnectedEvent) -> None:
        """Grant permissions when browser connects."""
        permissions = self.browser_session.browser_profile.permissions
        if not permissions:
            self.logger.debug('No permissions to grant')
            return
        self.logger.debug(f'🔓 Granting browser permissions: {permissions}')
        try:
            await self.browser_session.cdp_client.send.Browser.grantPermissions(params={'permissions': permissions})
            self.logger.debug(f'✅ Successfully granted permissions: {permissions}')
        except Exception as e:
            self.logger.error(f'❌ Failed to grant permissions: {str(e)}')