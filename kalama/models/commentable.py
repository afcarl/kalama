

class Commentable():
    """
    Properties:
        | parent    -- Commentable or None
        | focus     -- flexible
        | body      -- flexible
        | body_type -- str
        | author    -- Persona
        | score     -- float
        | permalink -- str
    """

    def __init__(self):
        self.parent = None
        self.focus = None
        self.author = None
        self.score = 0.0
        self.body = ''
        self.body_type = 'html'
        self.permalink = ''
        pass