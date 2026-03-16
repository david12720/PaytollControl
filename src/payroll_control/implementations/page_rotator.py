import io

from PIL import Image

from ..abstractions.file_preparator import PreparationStep, PreparedFile


class PageRotator(PreparationStep):
    """Detects landscape-scanned pages and rotates them to portrait orientation.

    Detection: a page is considered landscape if its width > height and
    the top/bottom 15% bands are nearly blank (white).
    """

    def process(self, files: list[PreparedFile]) -> list[PreparedFile]:
        return [self._maybe_rotate(f) for f in files]

    def _maybe_rotate(self, prepared: PreparedFile) -> PreparedFile:
        img = Image.open(io.BytesIO(prepared.data))
        w, h = img.size

        if w <= h:
            return prepared

        gray = img.convert("L")
        top_min = gray.crop((0, 0, w, max(1, int(h * 0.15)))).getextrema()[0]
        bottom_min = gray.crop((0, int(h * 0.85), w, h)).getextrema()[0]

        if top_min > 200 and bottom_min > 200:
            rotated = img.rotate(90, expand=True)
            buf = io.BytesIO()
            rotated.save(buf, format="PNG")
            return PreparedFile(
                source_path=prepared.source_path,
                data=buf.getvalue(),
                mime_type=prepared.mime_type,
                page_index=prepared.page_index,
                metadata={**prepared.metadata, "rotated": True},
            )

        return prepared
