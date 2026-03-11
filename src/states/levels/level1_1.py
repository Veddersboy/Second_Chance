from src.objects.portal import Portal  # Import portal class
from src.objects.key_item import KeyItem
from .level import Level


class Level1_1(Level):
    def __init__(self):
        imgArr = [f"plx-{i}.png" for i in range(1, 6)]
        super().__init__(
            level=1,
            music_file="levelmusic.mp3",
            imgArr=imgArr,
            key_in_level=True
        )

    def add_portal(self):
        # Add portal at specific coordinates
        self.portal = Portal(3500, 400, "assets/backgrounds/portal.png", 150, 150)
        self.portals.add(self.portal)
        self.objects.add(self.portals)

    def add_key(self):
        self.key_item = KeyItem(2170, 80, "assets/backgrounds/key_item.png", 32, 32)
        self.keys.add(self.key_item)
        self.objects.add(self.keys)
