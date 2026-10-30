"""ComfyUI output node: rename the file emitted by SaveVideo to an exact basename.
Install as custom_nodes/exact_filename_output/__init__.py
"""
from pathlib import Path
import re
import folder_paths

class ExactFilenameAfterSave:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "video": ("VIDEO",),
            "filename_prefix": ("STRING", {"forceInput": True}),
        }}

    RETURN_TYPES = ()
    FUNCTION = "rename"
    OUTPUT_NODE = True
    CATEGORY = "video/output"

    def rename(self, video, filename_prefix):
        root = Path(folder_paths.get_output_directory()).resolve()
        prefix = filename_prefix.replace('\\', '/').strip('/')
        relative = Path(prefix)
        target_dir = (root / relative.parent).resolve()
        if not target_dir.is_relative_to(root):
            raise ValueError('Output path must stay inside ComfyUI output directory')
        stem = relative.name
        if not stem or stem in ('.', '..'):
            raise ValueError('Invalid filename prefix')
        # SaveVideo produces names such as 2_00001_.mp4.
        pattern = re.compile(r'^' + re.escape(stem) + r'_(\d{5})_\.(mp4|mov|mkv|webm)$', re.I)
        candidates = [p for p in target_dir.iterdir() if p.is_file() and pattern.fullmatch(p.name)] if target_dir.is_dir() else []
        if not candidates:
            raise FileNotFoundError(f'No numbered SaveVideo output found for {prefix}')
        source = max(candidates, key=lambda p: (p.stat().st_mtime_ns, p.name))
        destination = target_dir / (stem + source.suffix)
        if destination.exists():
            raise FileExistsError(f'Refusing to overwrite existing output: {destination}')
        source.rename(destination)
        print(f'[ExactFilenameAfterSave] {source.name} -> {destination.name}')
        return {}

NODE_CLASS_MAPPINGS = {"ExactFilenameAfterSave": ExactFilenameAfterSave}
NODE_DISPLAY_NAME_MAPPINGS = {"ExactFilenameAfterSave": "Exact Filename After Save"}
