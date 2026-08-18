@staticmethod
def serialize_messages(messages: list[BaseMessage]) -> list[Message]:
    """
		Serialize a list of browser-use messages to OCI Raw API Message objects.

		Args:
		    messages: List of browser-use messages

		Returns:
		    List of OCI Message objects
		"""
    oci_messages = []
    for message in messages:
        oci_message = Message()
        if isinstance(message, UserMessage):
            oci_message.role = 'USER'
            content = message.content
            if isinstance(content, str):
                text_content = TextContent()
                text_content.text = content
                oci_message.content = [text_content]
            elif isinstance(content, list):
                contents = []
                for part in content:
                    if part.type == 'text':
                        text_content = TextContent()
                        text_content.text = part.text
                        contents.append(text_content)
                    elif part.type == 'image_url':
                        image_content = OCIRawMessageSerializer._create_image_content(part)
                        contents.append(image_content)
                if contents:
                    oci_message.content = contents
        elif isinstance(message, SystemMessage):
            oci_message.role = 'SYSTEM'
            content = message.content
            if isinstance(content, str):
                text_content = TextContent()
                text_content.text = content
                oci_message.content = [text_content]
            elif isinstance(content, list):
                contents = []
                for part in content:
                    if part.type == 'text':
                        text_content = TextContent()
                        text_content.text = part.text
                        contents.append(text_content)
                    elif part.type == 'image_url':
                        image_content = OCIRawMessageSerializer._create_image_content(part)
                        contents.append(image_content)
                if contents:
                    oci_message.content = contents
        elif isinstance(message, AssistantMessage):
            oci_message.role = 'ASSISTANT'
            content = message.content
            if isinstance(content, str):
                text_content = TextContent()
                text_content.text = content
                oci_message.content = [text_content]
            elif isinstance(content, list):
                contents = []
                for part in content:
                    if part.type == 'text':
                        text_content = TextContent()
                        text_content.text = part.text
                        contents.append(text_content)
                    elif part.type == 'image_url':
                        image_content = OCIRawMessageSerializer._create_image_content(part)
                        contents.append(image_content)
                    elif part.type == 'refusal':
                        text_content = TextContent()
                        text_content.text = f'[Refusal] {part.refusal}'
                        contents.append(text_content)
                if contents:
                    oci_message.content = contents
        else:
            oci_message.role = 'USER'
            text_content = TextContent()
            text_content.text = str(message)
            oci_message.content = [text_content]
        if hasattr(oci_message, 'content') and oci_message.content:
            oci_messages.append(oci_message)
    return oci_messages