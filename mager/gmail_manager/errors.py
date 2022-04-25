class InvalidPathError(Exception):
    def __init__(self, path):
        self.message = f'{path} is not a valid URL to an image source nor an existing ' \
                        'path to an image file'
        super().__init__(self.message)

        
class UnmatchedImageNumberError(Exception):
    def __init__(self, temp_img_n, list_img_n):
        self.message = f'Image number found in template ({temp_img_n}) is different ' \
                       f'than the number of image paths ({list_img_n}) in the list'
        super().__init__(self.message)
