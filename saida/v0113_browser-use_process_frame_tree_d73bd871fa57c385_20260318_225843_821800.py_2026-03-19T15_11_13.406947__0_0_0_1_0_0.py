def process_frame_tree(node, parent_frame_id=None):
    """Recursively process frame tree and add to all_frames."""
    frame = node.get('frame', {})
    current_frame_id = frame.get('id')
    if current_frame_id:
        actual_parent_id = frame.get('parentId') or parent_frame_id
        frame_info = {**frame, 'frameTargetId': target_id, 'parentFrameId': actual_parent_id, 'childFrameIds': [], 'isCrossOrigin': False, 'isValidTarget': self._is_valid_target(target, include_http=True, include_about=True, include_pages=True, include_iframes=True, include_workers=False, include_chrome=False, include_chrome_extensions=False, include_chrome_error=False)}
        cross_origin_type = frame.get('crossOriginIsolatedContextType')
        if cross_origin_type and cross_origin_type != 'NotIsolated':
            frame_info['isCrossOrigin'] = True
        if target.get('type') == 'iframe':
            frame_info['isCrossOrigin'] = True
        if not include_cross_origin and frame_info.get('isCrossOrigin'):
            return
        child_frames = node.get('childFrames', [])
        for child in child_frames:
            child_frame = child.get('frame', {})
            child_frame_id = child_frame.get('id')
            if child_frame_id:
                frame_info['childFrameIds'].append(child_frame_id)
        if current_frame_id in all_frames:
            existing = all_frames[current_frame_id]
            if target.get('type') == 'iframe':
                existing['frameTargetId'] = target_id
                existing['isCrossOrigin'] = True
        else:
            all_frames[current_frame_id] = frame_info
        if include_cross_origin or not frame_info.get('isCrossOrigin'):
            for child in child_frames:
                process_frame_tree(child, current_frame_id)