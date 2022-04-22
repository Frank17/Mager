class InvalidPathError(Exception):
    def __init__(self, path):
        self.message = f'{path} is not an URL nor an existing path to a file'
        super().__init__(self.message)
