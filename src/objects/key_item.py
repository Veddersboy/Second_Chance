import pygame as pg


class KeyItem(pg.sprite.Sprite):
    """Sprite class to represent a key.

    Args:
        x (int): x position to spawn at.
        y (int): y position to spawn at.
        image_path (str): Full path to key image.
        width (int): Width of key image.
        height (int): Height of key image.
    """

    def __init__(self, x, y, image_path, width, height):
        super().__init__()
        self.original_image = pg.image.load(image_path).convert_alpha()
        self.image = pg.transform.scale(self.original_image, (width, height))  # Scale the image to the desired size
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        """Draws the key onto the screen.

        Args:
            screen (pygame.Surface): Screen to draw key on.
        """
        screen.blit(self.image, self.rect)

    def update(self, scroll):
        """Updates the position of the key.

        Args:
            scroll (int): Amount to update key rect.
        """
        self.rect.x += scroll

    def collect(self):
        self.kill
